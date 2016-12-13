from unittest import TestCase

from pycec.datastruct import CecCommand
from const import CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, CMD_PHYSICAL_ADDRESS

from pycec import HdmiDevice


class TestHdmiDevice(TestCase):
    pass

    #    def test_logical_address(self):
    #        self.fail()

    def test_update(self):
        device = HdmiDevice(2)
        cmd = CecCommand('02:%02x:4f:6e:6b:79:6f:20:48:54:58:2d:32:32:48:44:58' % CMD_OSD_NAME[1])
        device.update(cmd)
        self.assertTrue(device.name == 'Onkyo HTX-22HDX')

        cmd = CecCommand('02:%02x:01' % CMD_POWER_STATUS[1])
        device.update(cmd)
        self.assertTrue(device.power_status == 1)
        cmd = CecCommand('02:%02x:02' % CMD_POWER_STATUS[1])
        device.update(cmd)
        self.assertTrue(device.power_status == 2)

        cmd = CecCommand('02:%02x:18:C0:86' % CMD_VENDOR[1])
        device.update(cmd)
        self.assertTrue(device.vendor_id == 0x18C086)
        self.assertTrue(device.vendor == 'Broadcom')

        cmd = CecCommand('02:%02x:C0:86' % CMD_PHYSICAL_ADDRESS[1])
        device.update(cmd)
        self.assertTrue(device.physical_address.ascmd == 'c0:86')
        self.assertTrue(device.physical_address.aslist == [0xC, 0x0, 0x8, 0x6])
