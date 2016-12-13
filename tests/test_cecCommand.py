from unittest import TestCase

from pycec import CecCommand


class TestCecCommand(TestCase):
    def test_src(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(cc.src == 0x1)
        cc = CecCommand("52:90:02")
        self.failUnless(cc.src == 0x5)
        cc = CecCommand(0x8f, 0x5, 0x3)
        self.failUnless(cc.src == 0x3)
        cc = CecCommand("52:90:02")
        cc.src = 0x4
        self.failUnless(("%s" % cc) == "42:90:02")
        cc = CecCommand(0x8f, 0x5, 0x3, raw="78:a5:89:45")
        self.failUnless(cc.src == 0x7)

    def test_dst(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(cc.dst == 0xf)
        cc = CecCommand("52:90:02")
        self.failUnless(cc.dst == 0x2)
        cc = CecCommand(0x8f, 0x5, 0x3)
        self.failUnless(cc.dst == 0x5)
        cc = CecCommand("52:90:02")
        cc.dst = 0x4
        self.failUnless(("%s" % cc) == "54:90:02")
        cc = CecCommand(0x8f, 0x5, 0x3,raw="78:a5:89:45")
        self.failUnless(cc.dst == 0x8)

    def test_cmd(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(cc.cmd == 0x90)

    def test_att(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(cc.att == [0x02])

    def test_raw(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(cc.raw == "1f:90:02")

    def test_str(self):
        cc = CecCommand("1f:90:02")
        self.failUnless(("%s" % cc) == "1f:90:02")
