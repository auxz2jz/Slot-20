import hashlib
import stat
import struct
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import extract_ubifs_readonly as ubifs  # noqa: E402
import unpack_reolink_offline as pak  # noqa: E402


class PakTests(unittest.TestCase):
    @staticmethod
    def make_package(names=pak.PARTITIONS, trailing=b""):
        component_size = 512
        first_offset = 0x800
        raw = bytearray(first_offset + component_size * len(names))
        struct.pack_into("<I", raw, 0, pak.MAGIC)
        offset = first_offset
        for index, name in enumerate(names):
            record = 0x0C + 64 * index
            raw[record : record + len(name)] = name.encode("ascii")
            raw[record + 32 : record + 38] = b"v1.0.0"
            struct.pack_into("<II", raw, record + 56, offset, component_size)
            raw[offset : offset + component_size] = bytes([index + 1]) * component_size
            offset += component_size
        return bytes(raw) + trailing

    def test_valid_package_is_split_and_indexed(self):
        raw = self.make_package()
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            source = temp / "camera.pak"
            source.write_bytes(raw)
            result = pak.unpack(source, temp / "out")

            self.assertEqual([row["name"] for row in result["partitions"]], list(pak.PARTITIONS))
            self.assertEqual(result["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["filesystem_results"], {"rootfs": [], "app": []})
            for index, name in enumerate(pak.PARTITIONS):
                section = (temp / "out" / "sections" / f"{name}.bin").read_bytes()
                self.assertEqual(section, bytes([index + 1]) * 512)

    def test_package_rejects_out_of_order_partitions(self):
        names = list(pak.PARTITIONS)
        names[3], names[4] = names[4], names[3]
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "camera.pak"
            source.write_bytes(self.make_package(names))
            with self.assertRaisesRegex(ValueError, "partition order"):
                pak.unpack(source, Path(temp) / "out")

    def test_package_rejects_trailing_data(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "camera.pak"
            source.write_bytes(self.make_package(trailing=b"unexpected"))
            with self.assertRaisesRegex(ValueError, "trailing data"):
                pak.unpack(source, Path(temp) / "out")


class UbifsTests(unittest.TestCase):
    @staticmethod
    def make_peb(sequence, marker):
        peb = bytearray(ubifs.PEB_SIZE)
        peb[:4] = b"UBI#"
        vid = 2048
        peb[vid : vid + 4] = b"UBI!"
        struct.pack_into(">I", peb, vid + 8, 0)
        struct.pack_into(">I", peb, vid + 12, 7)
        struct.pack_into(">Q", peb, vid + 36, sequence)
        peb[ubifs.DATA_OFFSET] = marker
        return bytes(peb)

    def test_decode_volumes_uses_full_64_bit_sequence_number(self):
        older = self.make_peb(0x00000001FFFFFFFF, 0x11)
        newer = self.make_peb(0x0000000200000000, 0x22)
        volumes = ubifs.decode_volumes(older + newer)
        sequence, payload, peb_offset = volumes[0][7]

        self.assertEqual(sequence, 0x0000000200000000)
        self.assertEqual(payload[0], 0x22)
        self.assertEqual(peb_offset, ubifs.PEB_SIZE)

    def test_names_reject_path_separators_and_dot_entries(self):
        for name in (b"", b".", b"..", b"/absolute", b"a/b", b"a\\b", b"a\0b"):
            with self.subTest(name=name):
                self.assertFalse(ubifs.valid_name(name))
        self.assertTrue(ubifs.valid_name(b"normal-name"))

    def test_reconstruction_caps_reported_file_size(self):
        parsed = {
            "inodes": {1: {"size": 250_000_001, "mode": stat.S_IFREG}},
            "data": {},
        }
        with self.assertRaisesRegex(ValueError, "Excessive file size"):
            ubifs.reconstruct_file(1, parsed)


if __name__ == "__main__":
    unittest.main()
