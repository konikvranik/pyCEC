from unittest import TestCase

from pycec.network import PhysicalAddress


class TestPhysicalAddress(TestCase):
    def test_creation(self):
        pa = PhysicalAddress('8F:65')
        self.assertEqual(0x8f65, pa.asint)
        pa = PhysicalAddress('0F:60')
        self.assertEqual(0x0f60, pa.asint)
        pa = PhysicalAddress('2.F.6.5')
        self.assertEqual(0x2f65, pa.asint)
        self.assertEqual('2.f.6.5', pa.asstr)
        pa = PhysicalAddress('0.F.6.0')
        self.assertEqual(0x0f60, pa.asint)
        pa = PhysicalAddress([2, 15, 6, 4])
        self.assertEqual(0x2f64, pa.asint)
        pa = PhysicalAddress([0, 15, 6, 0])
        self.assertEqual(0x0f60, pa.asint)
        pa = PhysicalAddress(0x0f60)
        self.assertEqual(0x0f60, pa.asint)

    def test_aslist(self):
        pa = PhysicalAddress("8f:ab")
        self.assertEqual(pa.asattr, [0x8f, 0xab])
        pa = PhysicalAddress("00:00")
        self.assertEqual(pa.asattr, [0x0, 0x0])
        pa = PhysicalAddress("00:10")
        self.assertEqual(pa.asattr, [0x0, 0x10])

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
