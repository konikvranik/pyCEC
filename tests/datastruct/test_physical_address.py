from pycec.network import PhysicalAddress


def test_creation():
    pa = PhysicalAddress("8F:65")
    assert 0x8F65 == pa.asint
    pa = PhysicalAddress("0F:60")
    assert 0x0F60 == pa.asint
    pa = PhysicalAddress("2.F.6.5")
    assert 0x2F65 == pa.asint
    assert "2.f.6.5" == pa.asstr
    pa = PhysicalAddress("0.F.6.0")
    assert 0x0F60 == pa.asint
    pa = PhysicalAddress([2, 15, 6, 4])
    assert 0x2F64 == pa.asint
    pa = PhysicalAddress([0, 15, 6, 0])
    assert 0x0F60 == pa.asint
    pa = PhysicalAddress(0x0F60)
    assert 0x0F60 == pa.asint


def test_aslist():
    pa = PhysicalAddress("8f:ab")
    assert pa.asattr == [0x8F, 0xAB]
    pa = PhysicalAddress("00:00")
    assert pa.asattr == [0x0, 0x0]
    pa = PhysicalAddress("00:10")
    assert pa.asattr == [0x0, 0x10]


def test_asint():
    pa = PhysicalAddress("8f:ab")
    assert pa.asint == 0x8FAB
    pa = PhysicalAddress("00:00")
    assert pa.asint == 0x0000
    pa = PhysicalAddress("00:10")
    assert pa.asint == 0x0010


def test_ascmd():
    pa = PhysicalAddress("8f:ab")
    assert pa.ascmd == "8f:ab"
    pa = PhysicalAddress("00:00")
    assert pa.ascmd == "00:00"
    pa = PhysicalAddress("00:10")
    assert pa.ascmd == "00:10"


def test_str():
    pa = PhysicalAddress("8f:ab")
    assert ("%s" % pa) == "8.f.a.b"
    pa = PhysicalAddress("00:00")
    assert ("%s" % pa) == "0.0.0.0"
    pa = PhysicalAddress("00:10")
    assert ("%s" % pa) == "0.0.1.0"
