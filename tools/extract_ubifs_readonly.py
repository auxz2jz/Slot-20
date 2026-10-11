#!/usr/bin/env python3
"""Read-only/offline extractor for the observed Reolink UBIFS-in-UBI images.

Only parses input bytes. Optional output files are written beneath a new target
folder. Never runs extracted code or changes a device. This is a forensic helper,
not a vetted replacement for ubireader/mtd-utils, and does not replay journal
transactions, provide a clean UBIFS mount, or validate boot compatibility.
"""
import argparse
from collections import Counter, defaultdict, deque
import ctypes
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import sys
import zlib

PEB_SIZE = 131072
DATA_OFFSET = 4096
UBIFS_MAGIC = b'\x31\x18\x10\x06'


def valid_name(name):
    return bool(name and name not in (b'.', b'..') and b'/' not in name and b'\\' not in name and b'\0' not in name and name[:1]!=b'/')


def clean(name):
    s = name.decode('utf-8', 'surrogateescape')
    # filenames stay bounded and unambiguous for the analysis host
    return ''.join(c if c.isprintable() and c not in ('/','\\',':') else '_' for c in s)


def decode_volumes(raw):
    volumes=defaultdict(dict)
    for pos in range(0,len(raw),PEB_SIZE):
        peb=raw[pos:pos+PEB_SIZE]
        if len(peb) != PEB_SIZE or peb[:4]!=b'UBI#':
            continue
        vid=peb[2048:2112]
        if vid[:4]!=b'UBI!':
            continue
        vol_id=struct.unpack_from('>I',vid,8)[0]
        lnum=struct.unpack_from('>I',vid,12)[0]
        # ubi_vid_hdr stores sqnum as a big-endian 64-bit value at offset 36.
        # Reading only the low 32 bits can select an older duplicate LEB after
        # the sequence number crosses a 32-bit boundary.
        seq=struct.unpack_from('>Q',vid,36)[0]
        if vol_id > 100 or lnum>100000:
            continue
        previous=volumes[vol_id].get(lnum)
        if previous is None or seq>=previous[0]:
            volumes[vol_id][lnum]=(seq,peb[DATA_OFFSET:],pos)
    return volumes


def scan_nodes(lebmap):
    by_type=Counter(); valid=0; invalid=0
    inodes={}; dents={}; data={}; compressor=Counter(); node_sizes=Counter()
    for lnum,(seq,leb,peboff) in sorted(lebmap.items()):
        offset=0
        while True:
            start=leb.find(UBIFS_MAGIC, offset)
            if start<0:break
            offset=start+4
            if start+24>len(leb):continue
            crc,sqnum,size=struct.unpack_from('<IQI',leb,start+4)
            kind=leb[start+20]
            if size<24 or start+size>len(leb) or (zlib.crc32(leb[start+8:start+size])^0xffffffff)!=crc:
                invalid+=1
                continue
            valid+=1;by_type[kind]+=1
            node=leb[start:start+size]
            key=(struct.unpack_from('<I',node,24)[0] if len(node)>=28 else 0)
            if kind==0 and len(node)>=160:
                filesize=struct.unpack_from('<Q',node,48)[0]
                mode=struct.unpack_from('<I',node,104)[0]
                inline_len=struct.unpack_from('<I',node,112)[0]
                if inline_len>len(node)-160:continue
                r={'inode':key,'mode':mode,'size':filesize,'inline':node[160:160+inline_len], 'sqnum':sqnum}
                if key not in inodes or sqnum>inodes[key]['sqnum']:inodes[key]=r
            elif kind==2 and len(node)>=56:
                inum=struct.unpack_from('<Q',node,40)[0]
                dtype=node[49]
                nlen=struct.unpack_from('<H',node,50)[0]
                if nlen>255 or len(node)<56+nlen:continue
                name=node[56:56+nlen]
                if not valid_name(name):continue
                k=(key,name)
                r={'parent':key,'inode':inum,'dtype':dtype,'name':name, 'sqnum':sqnum}
                if k not in dents or sqnum>dents[k]['sqnum']:dents[k]=r
            elif kind==1 and len(node)>=48:
                size_unc=struct.unpack_from('<I',node,40)[0]
                compr=struct.unpack_from('<H',node,44)[0]
                idx=struct.unpack_from('<I',node,28)[0]&0x1fffffff
                if size_unc>4096 or compr>3:continue
                compressor[compr]+=1
                k=(key,idx)
                r={'inode':key,'index':idx,'compression':compr,'uncompressed':size_unc,'data':node[48:], 'sqnum':sqnum}
                if k not in data or sqnum>data[k]['sqnum']:data[k]=r
    return {'types':by_type,'valid':valid,'invalid':invalid,'inodes':inodes,'dents':dents,'data':data,'compression':compressor}


def make_paths(parsed):
    children=defaultdict(list)
    for d in parsed['dents'].values():
        if d['inode']:
            children[d['parent']].append(d)
    output=[]; dirs=deque([(1, '',0)])
    visited={(1,'')}
    while dirs:
        inode,parent,depth=dirs.popleft()
        if depth>45:continue
        for d in sorted(children[inode],key=lambda x:x['name']):
            name=clean(d['name'])
            candidate=f'{parent}/{name}' if parent else name
            if len(candidate)>300 or not candidate or candidate.startswith('/') or '..' in PurePosixPath(candidate).parts:
                continue
            rec={'path':candidate,'inode':d['inode'],'direntry_type':d['dtype']}
            meta=parsed['inodes'].get(d['inode'])
            if meta:
                rec['size']=meta['size'];rec['mode']=oct(meta['mode']);rec['kind']='dir' if stat.S_ISDIR(meta['mode']) else 'regular' if stat.S_ISREG(meta['mode']) else 'symlink' if stat.S_ISLNK(meta['mode']) else 'other'
            else:rec['kind']='unknown'
            output.append(rec)
            if rec['kind']=='dir' and (d['inode'], candidate) not in visited:
                visited.add((d['inode'],candidate));dirs.append((d['inode'],candidate,depth+1))
    return output


def lzo_decompress(blob, outlen):
    lib=ctypes.CDLL('liblzo2.so.2')
    fn=lib.lzo1x_decompress_safe
    fn.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.POINTER(ctypes.c_size_t),ctypes.c_void_p]
    fn.restype=ctypes.c_int
    src=ctypes.create_string_buffer(blob)
    dest=ctypes.create_string_buffer(outlen if outlen else 1)
    dstsize=ctypes.c_size_t(outlen)
    rc=fn(src,len(blob),dest,ctypes.byref(dstsize),None)
    if rc or dstsize.value!=outlen: raise ValueError(f'LZO decompression failed: {rc}/{dstsize.value}/{outlen}')
    return dest.raw[:outlen]


def reconstruct_file(inode, parsed):
    meta=parsed['inodes'][inode]
    size=meta['size']
    if size>250_000_000:raise ValueError('Excessive file size')
    if stat.S_ISLNK(meta['mode']):return meta['inline']
    chunks=[]
    blockcount=(size+4095)//4096
    if blockcount>65000:raise ValueError('Excessive block count')
    for idx in range(blockcount):
        rec=parsed['data'].get((inode,idx))
        if not rec:raise ValueError(f'Missing block {idx} for inode {inode}')
        typ=rec['compression'];payload=rec['data'];want=rec['uncompressed']
        if typ==0:val=payload
        elif typ==1:val=lzo_decompress(payload,want)
        elif typ==2:val=zlib.decompress(payload)
        else:raise ValueError(f'Unsupported compressor {typ}')
        if len(val)!=want:raise ValueError(f'Unexpected decompressed size {len(val)} instead of {want}')
        chunks.append(val)
    all_data=b''.join(chunks)
    if len(all_data)<size:raise ValueError('Incomplete inode data')
    return all_data[:size]


def extract(path, folder, include_binary=False):
    raw=path.read_bytes()
    volumes=decode_volumes(raw)
    results=[]
    for vol_id, lebmap in sorted(volumes.items()):
        if vol_id>=100:continue
        parsed=scan_nodes(lebmap)
        records=make_paths(parsed)
        vol_out=folder/f'volume_{vol_id}'
        vol_out.mkdir(parents=True,exist_ok=True)
        failures=[]; hashes={}
        for rec in records:
            if rec['kind'] not in ('regular','symlink'):continue
            inode=rec['inode']
            if inode not in parsed['inodes']:continue
            # Never create symlinks or device nodes. Optional files are inert host copies.
            try:
                content=reconstruct_file(inode,parsed)
                hashes[rec['path']]=hashlib.sha256(content).hexdigest()
                if include_binary:
                    target=(vol_out/rec['path'])
                    if rec['kind']=='symlink':target=Path(str(target)+'.symlink.txt')
                    target.parent.mkdir(parents=True,exist_ok=True)
                    if not target.is_relative_to(vol_out):raise ValueError('Unsafe output path')
                    target.write_bytes(content)
            except Exception as ex:
                failures.append({'path':rec['path'],'error':str(ex)[:180]})
        manifest={'source':str(path.name),'volume_id':vol_id,'leb_count':len(lebmap),
                  'ubifs_valid_nodes':parsed['valid'],'node_types':dict(parsed['types']),
                  'compressions':dict(parsed['compression']),
                  'inode_count':len(parsed['inodes']),'dentry_count':len(parsed['dents']),
                  'resolved_paths':len(records),'files':records,
                  'file_sha256':hashes, 'failures':failures,
                  'extractor_limits':'Static extraction only; not full journal replay, inode version selection based on sequence number, not a bootable image.'}
        report=folder/f'volume_{vol_id}_manifest.json'
        report.write_text(json.dumps(manifest,indent=2,ensure_ascii=True)+'\n')
        results.append({'volume':vol_id,'manifest':str(report),'entries':len(records), 'failures':len(failures),'lzo':parsed['compression'][1]})
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('ubi',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--write-files',action='store_true',help='Also write extracted files, with symlinks saved as text')
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    print(json.dumps(extract(args.ubi,args.out,args.write_files),indent=2))

if __name__=='__main__':main()
