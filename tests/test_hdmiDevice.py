from unittest import TestCase

from pycec.commands import CecCommand
from pycec.const import CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, CMD_PHYSICAL_ADDRESS

from pycec.network import HdmiDevice


class TestHdmiDevice(TestCase):

    def test_logical_address(self):
        device = HdmiDevice(2)
        self.assertEqual(device.logical_address, 2)

    def test_update(self):
        device = HdmiDevice(2)
        cmd = CecCommand('02:%02x:4f:6e:6b:79:6f:20:48:54:58:2d:32:32:48:44:58' % CMD_OSD_NAME[1])
        device.update_callback(cmd)
        self.assertEqual(device.osd_name, 'Onkyo HTX-22HDX')

        cmd = CecCommand('02:%02x:01' % CMD_POWER_STATUS[1])
        device.update_callback(cmd)
        self.assertEqual(device.power_status, 1)
        cmd = CecCommand('02:%02x:02' % CMD_POWER_STATUS[1])
        device.update_callback(cmd)
        self.assertEqual(device.power_status, 2)

        cmd = CecCommand('02:%02x:18:C0:86' % CMD_VENDOR[1])
        device.update_callback(cmd)
        self.assertEqual(device.vendor_id, 0x18C086)
        self.assertEqual(device.vendor, 'Broadcom')

        cmd = CecCommand('02:%02x:C0:86:01' % CMD_PHYSICAL_ADDRESS[1])
        device.update_callback(cmd)
        self.assertEqual(device.physical_address.ascmd, 'c0:86')
        self.assertEqual(device.physical_address.aslist, [0xC, 0x0, 0x8, 0x6])
