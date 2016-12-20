from unittest import TestCase

from pycec.datastruct import PhysicalAddress


class TestPhysicalAddress(TestCase):
    def test_aslist(self):
        pa = PhysicalAddress("8f:ab")
        self.assertEqual(pa.aslist, [0x8, 0xf, 0xa, 0xb])
        pa = PhysicalAddress("00:00")
        self.assertEqual(pa.aslist, [0x0, 0x0, 0x0, 0x0])
        pa = PhysicalAddress("00:10")
        self.assertEqual(pa.aslist, [0x0, 0x0, 0x1, 0x0])

    def test_asint(self):
        pa = PhysicalAddress("8f:ab")
        self.assertEqual(pa.asint, 0x8fab)
        pa = PhysicalAddress("00:00")
        self.assertEqual(pa.asint, 0x0000)
        pa = PhysicalAddress("00:10")
        self.assertEqual(pa.asint, 0x0010)

    def test_ascmd(self):
        pa = PhysicalAddress("8f:ab")
        self.assertEqual(pa.ascmd, "8f:ab")
        pa = PhysicalAddress("00:00")
        self.assertEqual(pa.ascmd, "00:00")
        pa = PhysicalAddress("00:10")
        self.assertEqual(pa.ascmd, "00:10")

    def test_str(self):
        pa = PhysicalAddress("8f:ab")
        self.assertEqual(("%s" % pa), "8.f.a.b")
        pa = PhysicalAddress("00:00")
        self.assertEqual(("%s" % pa), "0.0.0.0")
        pa = PhysicalAddress("00:10")
        self.assertEqual(("%s" % pa), "0.0.1.0")
