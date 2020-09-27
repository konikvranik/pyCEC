from pycec.commands import CecCommand
from pycec.const import (
    CMD_POWER_STATUS,
    CMD_VENDOR,
    CMD_OSD_NAME,
    CMD_PHYSICAL_ADDRESS,
)
from pycec.network import HDMIDevice


def test_logical_address():
    device = HDMIDevice(2)
    assert device.logical_address == 2


def test_update():
    device = HDMIDevice(2)
    cmd = CecCommand(
        "02:%02x:4f:6e:6b:79:6f:20:48:54:58:2d:32:32:48:44:58"
        % CMD_OSD_NAME[1]
    )
    device.update_callback(cmd)
    assert device.osd_name == "Onkyo HTX-22HDX"

    cmd = CecCommand("02:%02x:01" % CMD_POWER_STATUS[1])
    device.update_callback(cmd)
    assert device.power_status == 1
    cmd = CecCommand("02:%02x:02" % CMD_POWER_STATUS[1])
    device.update_callback(cmd)
    assert device.power_status == 2

    cmd = CecCommand("02:%02x:18:C0:86" % CMD_VENDOR[1])
    device.update_callback(cmd)
    assert device.vendor_id == 0x18C086
    assert device.vendor == "Broadcom"

    cmd = CecCommand("02:%02x:C0:86:01" % CMD_PHYSICAL_ADDRESS[1])
    device.update_callback(cmd)
    assert device.physical_address.ascmd == "c0:86"
    assert device.physical_address.asattr == [0xC0, 0x86]


def test_is_on():
    device = HDMIDevice(2)
    device._power_status = 1
    assert device.is_on is False
    device._power_status = 0
    assert device.is_on is True


def test_is_off():
    device = HDMIDevice(2)
    device._power_status = 1
    assert device.is_off is True
    device._power_status = 0
    assert device.is_off is False


def test_type():
    device = HDMIDevice(2)
    device._type = 2
    assert 2 == device.type


def test_type_name():
    device = HDMIDevice(2)
    device._type = 0
    assert "TV" == device.type_name
    device._type = 1
    assert "Recorder" == device.type_name
    device._type = 2
    assert "UNKNOWN" == device.type_name
    device._type = 3
    assert "Tuner" == device.type_name
    device._type = 4
    assert "Playback" == device.type_name
    device._type = 5
    assert "Audio" == device.type_name
    device._type = 6
    assert "UNKNOWN" == device.type_name
    device._type = 7
    assert "UNKNOWN" == device.type_name


def test_update_callback():
    device = HDMIDevice(3)
    device.update_callback(
        CecCommand(CMD_PHYSICAL_ADDRESS[1], att=[0x11, 0x00, 0x02])
    )
    assert "1.1.0.0" == str(device.physical_address)
    assert 2 == device.type
    device.update_callback(CecCommand(CMD_POWER_STATUS[1], att=[0x01]))
    assert 1 == device.power_status
    assert device.is_off is True
    assert device.is_on is False
    device.update_callback(CecCommand(CMD_POWER_STATUS[1], att=[0x00]))
    assert 0 == device.power_status
    assert device.is_on is True
    assert device.is_off is False
    device.update_callback(CecCommand(CMD_POWER_STATUS[1], att=[0x02]))
    assert 2 == device.power_status
    assert device.is_on is False
    assert device.is_off is False
    device.update_callback(
        CecCommand(CMD_OSD_NAME[1], att=list(map(lambda x: ord(x), "Test4")))
    )
    assert "Test4" == device.osd_name
    device.update_callback(CecCommand(CMD_VENDOR[1], att=[0x00, 0x80, 0x45]))
    assert 0x008045 == device.vendor_id
    assert "Panasonic" == device.vendor
