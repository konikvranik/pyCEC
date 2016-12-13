from unittest import TestCase

from pycec import CecCommand


class TestCecCommand(TestCase):
    def test_src(self):
        cc = CecCommand("1f:90:02")
        self.assertTrue(cc.src == 0x1)
        cc = CecCommand("52:90:02")
        self.assertTrue(cc.src == 0x5)
        cc = CecCommand(0x8f, 0x5, 0x3)
        self.assertTrue(cc.src == 0x3)
        cc = CecCommand("52:90:02")
        cc.src = 0x4
        self.assertTrue(("%s" % cc) == "42:90:02")
        cc = CecCommand(0x8f, 0x5, 0x3, raw="78:a5:89:45")
        self.assertTrue(cc.src == 0x7)

    def test_dst(self):
        cc = CecCommand("1f:90:02")
        self.assertTrue(cc.dst == 0xf)
        cc = CecCommand("52:90:02")
        self.assertTrue(cc.dst == 0x2)
        cc = CecCommand(0x8f, 0x5, 0x3)
        self.assertTrue(cc.dst == 0x5)
        cc = CecCommand("52:90:02")
        cc.dst = 0x4
        self.assertTrue(("%s" % cc) == "54:90:02")
        cc = CecCommand(0x8f, 0x5, 0x3, raw="78:a5:89:45")
        self.assertTrue(cc.dst == 0x8)

    def test_cmd(self):
        cc = CecCommand("1f:90:02")
        self.assertTrue(cc.cmd == 0x90)
        cc = CecCommand("52:8f:02")
        self.assertTrue(cc.cmd == 0x8f)
        cc = CecCommand(0x8f, 0x5, 0x3)
        self.assertTrue(cc.cmd == 0x8f)
        cc = CecCommand("52:90:02")
        cc.cmd = 0x40
        self.assertTrue(("%s" % cc) == "52:40:02")
        cc = CecCommand(0x8f, 0x5, 0x3, raw="78:a5:89:45")
        self.assertTrue(cc.cmd == 0xa5)

    def test_att(self):
        cc = CecCommand("1f:90:02")
        self.assertTrue(cc.att == [0x02])
        cc = CecCommand("52:8f:02:56")
        self.assertTrue(cc.att == [0x02, 0x56])
        cc = CecCommand(0x8f, 0x5, 0x3, [0x45, 0x56, 0x98])
        self.assertTrue(cc.att == [0x45, 0x56, 0x98])
        cc = CecCommand("52:90:02:03:04:56")
        cc.att = [0x52, 0x90, 0x02]
        self.assertTrue(("%s" % cc) == "52:90:52:90:02")
        cc = CecCommand(0x8f, 0x5, 0x3, raw="78:a5:89:45")
        self.assertTrue(cc.att == [0x89, 0x45])

    def test_raw(self):
        cc = CecCommand("1f:90:02:05:89")
        self.assertTrue(cc.raw == "1f:90:02:05:89")
        cc = CecCommand("1f:90:02:05:89")
        cc.raw = "52:90:52:90:02"
        self.assertTrue(cc.raw == "52:90:52:90:02")
        self.assertTrue(cc.src == 0x5)
        self.assertTrue(cc.dst == 0x2)
        self.assertTrue(cc.cmd == 0x90)
        self.assertTrue(cc.att == [0x52, 0x90, 0x02])
