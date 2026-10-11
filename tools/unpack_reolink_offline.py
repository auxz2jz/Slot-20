#!/usr/bin/env python3
"""Offline package splitter and UBIFS cataloger for observed Reolink RLC-811A PAK format.

Never connects to a camera or executes extracted code. Verifies package structure,
then writes section files into the selected local output folder and processes
UBIFS rootfs and app sections with extract_ubifs_readonly.py.

Usage:
    python unpack_reolink_offline.py camera.pak --out ./firmware_analysis
    python unpack_reolink_offline.py camera.pak --out ./firmware_analysis --write-files

Be careful with --write-files: firmware may contain keys, certificates and other
security-sensitive assets. No on-device usage or flash functionality is included.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from extract_ubifs_readonly import extract

PARTITIONS=('loader','fdt','uboot','kernel','rootfs','app')
MAGIC=0x32725913


def unpack(path, out, write_files=False):
    data=path.read_bytes()
    if len(data)<4096 or struct.unpack_from('<I',data)[0]!=MAGIC:
        raise ValueError('Unsupported package header')
    rows=[]
    for i in range(24):
        rec=data[0x0c+64*i:0x0c+64*(i+1)]
        name=rec[:32].split(b'\0')[0].decode('ascii','strict')
        ver=rec[32:48].split(b'\0')[0].decode('ascii','replace')
        offs,size=struct.unpack_from('<II',rec,56)
        if not name:
            continue
        if name not in PARTITIONS:
            raise ValueError(f'Unexpected named entry {i}: {name!r}')
        if size<=0 or offs<0x600 or offs+size>len(data):
            raise ValueError(f'Invalid partition {i}: {name!r}, offset {offs}, size {size}')
        if len(rows)>=len(PARTITIONS) or name != PARTITIONS[len(rows)]:
            raise ValueError(f'Unexpected partition order at {i}: {name!r}')
        if rows and offs<rows[-1]['offset']+rows[-1]['size']:
            raise ValueError('Overlapping partitions')
        rows.append({'name':name,'version':ver,'offset':offs,'size':size})
        if name=='app':
            break
    if len(rows)!=len(PARTITIONS):
        raise ValueError('Not all required partitions are present')
    if rows[-1]['offset']+rows[-1]['size']!=len(data):
        raise ValueError('Unexpected trailing data; format needs closer inspection')
    out.mkdir(parents=True,exist_ok=True)
    sec=out/'sections';sec.mkdir(exist_ok=True)
    for row in rows:
        component=data[row['offset']:row['offset']+row['size']]
        row['sha256']=hashlib.sha256(component).hexdigest()
        (sec/(row['name']+'.bin')).write_bytes(component)
    response={'package':path.name,'sha256':hashlib.sha256(data).hexdigest(),
              'partitions':rows,'filesystem_results':{}}
    for part in ('rootfs','app'):
        response['filesystem_results'][part]=extract(sec/(part+'.bin'), out/part, write_files)
    (out/'analysis_index.json').write_text(json.dumps(response,indent=2)+'\n')
    return response


def main():
    p=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('pak',type=Path);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--write-files',action='store_true')
    a=p.parse_args()
    result=unpack(a.pak,a.out,a.write_files)
    print(f"Inspected {result['package']}; wrote {len(result['partitions'])} partition files and manifests into {a.out}")

if __name__=='__main__':main()
