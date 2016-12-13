from unittest import TestCase

from pycec.datastruct import PhysicalAddress


class TestPhysicalAddress(TestCase):
    def test_aslist(self):
        pa = PhysicalAddress("8f:ab")
        self.assertTrue(pa.aslist == [0x8, 0xf, 0xa, 0xb])

    def test_asint(self):
        pa = PhysicalAddress("8f:ab")
        self.assertTrue(pa.asint == 0x8fab)

    def test_ascmd(self):
        pa = PhysicalAddress("8f:ab")
        self.assertTrue(pa.ascmd == "8f:ab")

    def test_str(self):
        pa = PhysicalAddress("8f:ab")
        self.assertTrue(("%s" % pa) == "8.f.a.b")
