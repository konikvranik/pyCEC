from pycec.commands import CecCommand
from pycec.const import CMD_POLL


def test_src():
    cc = CecCommand("1f:90:02")
    assert cc.src == 0x1
    cc = CecCommand("52:90:02")
    assert cc.src == 0x5
    cc = CecCommand(0x8F, 0x5, 0x3)
    assert cc.src == 0x3
    cc = CecCommand("52:90:02")
    cc.src = 0x4
    assert ("%s" % cc) == "42:90:02"
    cc = CecCommand(0x8F, 0x5, 0x3, raw="78:a5:89:45")
    assert cc.src == 0x7


def test_dst():
    cc = CecCommand("1f:90:02")
    assert cc.dst == 0xF
    cc = CecCommand("52:90:02")
    assert cc.dst == 0x2
    cc = CecCommand(0x8F, 0x5, 0x3)
    assert cc.dst == 0x5
    cc = CecCommand("52:90:02")
    cc.dst = 0x4
    assert ("%s" % cc) == "54:90:02"
    cc = CecCommand(0x8F, 0x5, 0x3, raw="78:a5:89:45")
    assert cc.dst == 0x8


def test_cmd():
    cc = CecCommand("1f:90:02")
    assert cc.cmd == 0x90
    cc = CecCommand("52:8f:02")
    assert cc.cmd == 0x8F
    cc = CecCommand(0x8F, 0x5, 0x3)
    assert cc.cmd == 0x8F
    cc = CecCommand(0x8F, 0x5, 0x3, raw="78:a5:89:45")
    assert cc.cmd == 0xA5


def test_att():
    cc = CecCommand("1f:90:02")
    assert cc.att == [0x02]
    cc = CecCommand("52:8f:02:56")
    assert cc.att == [0x02, 0x56]
    cc = CecCommand(0x8F, 0x5, 0x3, [0x45, 0x56, 0x98])
    assert cc.att == [0x45, 0x56, 0x98]
    cc = CecCommand(0x8F, 0x5, 0x3, raw="78:a5:89:45")
    assert cc.att == [0x89, 0x45]


def test_raw():
    cc = CecCommand("1f:90:02:05:89")
    assert cc.raw == "1f:90:02:05:89"
    cc = CecCommand("1f:90")
    assert cc.raw == "1f:90"
    cc = CecCommand("2c")
    assert cc.raw == "2c"
    cc = CecCommand(CMD_POLL, dst=3)
    assert cc.raw == "f3"
