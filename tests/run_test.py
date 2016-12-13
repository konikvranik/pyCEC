import unittest

from pycec import PhysicalAddress, CecCommand


class PyCecTests(unittest.TestCase):
    def testPhysicalAddress(self):
        pa = PhysicalAddress("8f:ab")
        self.failUnless(("%s" % pa) == "8f:ab")

    def testCecCommand(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(("%s" % cc) == "1f:90:02")
        self.failUnless(cc.cmd == 0x90)
        self.failUnless(cc.dst == 0xf)
        self.failUnless(cc.src == 0x1)
        self.failUnless(cc.att == [0x02])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
