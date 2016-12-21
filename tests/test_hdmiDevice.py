from unittest import TestCase

from pycec.commands import CecCommand
from pycec.const import CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, \
    CMD_PHYSICAL_ADDRESS
from pycec.network import HDMIDevice


class TestHDMIDevice(TestCase):
    def test_logical_address(self):
        device = HDMIDevice(2)
        self.assertEqual(device.logical_address, 2)

    def test_update(self):
        device = HDMIDevice(2)
        cmd = CecCommand(
            '02:%02x:4f:6e:6b:79:6f:20:48:54:58:2d:32:32:48:44:58' %
            CMD_OSD_NAME[1])
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
        self.assertEqual(device.physical_address.asattr, [0xC0, 0x86])

    def test_is_on(self):
        device = HDMIDevice(2)
        device._power_status = 1
        self.assertFalse(device.is_on)
        device._power_status = 0
        self.assertTrue(device.is_on)

    def test_is_off(self):
        device = HDMIDevice(2)
        device._power_status = 1
        self.assertTrue(device.is_off)
        device._power_status = 0
        self.assertFalse(device.is_off)

    def test_type(self):
        device = HDMIDevice(2)
        device._type = 2
        self.assertEqual(2, device.type)

    def test_type_name(self):
        device = HDMIDevice(2)
        device._type = 0
        self.assertEqual('TV', device.type_name)
        device._type = 1
        self.assertEqual('Recorder', device.type_name)
        device._type = 2
        self.assertEqual('UNKNOWN', device.type_name)
        device._type = 3
        self.assertEqual('Tuner', device.type_name)
        device._type = 4
        self.assertEqual('Playback', device.type_name)
        device._type = 5
        self.assertEqual('Audio', device.type_name)
        device._type = 6
        self.assertEqual('UNKNOWN', device.type_name)
        device._type = 7
        self.assertEqual('UNKNOWN', device.type_name)

    def test_update_callback(self):
        device = HDMIDevice(3)
        device.update_callback(
            CecCommand(CMD_PHYSICAL_ADDRESS[1], att=[0x11, 0x00, 0x02]))
        self.assertEqual('1.1.0.0', str(device.physical_address))
        self.assertEqual(2, device.type)
        device.update_callback(
            CecCommand(CMD_POWER_STATUS[1], att=[0x01]))
        self.assertEqual(1, device.power_status)
        self.assertTrue(device.is_off)
        self.assertFalse(device.is_on)
        device.update_callback(
            CecCommand(CMD_POWER_STATUS[1], att=[0x00]))
        self.assertEqual(0, device.power_status)
        self.assertTrue(device.is_on)
        self.assertFalse(device.is_off)
        device.update_callback(
            CecCommand(CMD_POWER_STATUS[1], att=[0x02]))
        self.assertEqual(2, device.power_status)
        self.assertFalse(device.is_on)
        self.assertFalse(device.is_off)
        device.update_callback(
            CecCommand(CMD_OSD_NAME[1],
                       att=list(map(lambda x: ord(x), "Test4"))))
        self.assertEqual("Test4", device.osd_name)
        device.update_callback(
            CecCommand(CMD_VENDOR[1], att=[0x00, 0x80, 0x45]))
        self.assertEqual(0x008045, device.vendor_id)
        self.assertEqual("Panasonic", device.vendor)
