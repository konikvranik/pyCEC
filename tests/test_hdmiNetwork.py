from unittest import TestCase

from pycec import HdmiNetwork, HdmiDevice
from pycec.const import CMD_POWER_STATUS, CMD_OSD_NAME, CMD_VENDOR, CMD_PHYSICAL_ADDRESS
from pycec.datastruct import CecCommand


class TestHdmiNetwork(TestCase):
    pass

    def test_scan(self):
        network = HdmiNetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False, False, False, False, False, False,
             False]))
        network.scan()
        self.assertIn(HdmiDevice(0), network.devices)
        device = network.get_device(0)
        self.assertEqual(device.name, '')
        device.request_name()
        self.assertEqual(device.name, "Test")

    def test_devices(self):
        network = HdmiNetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False, False, False, False, False, False,
             False]))
        network.scan()
        for i in [0, 1, 3, 5]:
            self.assertIn(HdmiDevice(i), network.devices)
        for i in [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            self.assertNotIn(HdmiDevice(i), network.devices)


class MockConfig:
    def __init__(self):
        self._command_callback = None

    def SetCommandCallback(self, callback):
        self._command_callback = callback

    def GetCommandCallback(self):
        return self._command_callback


class LogicalAddress:
    def __init__(self, i):
        self.primary = i


class MockAdapter:
    def __init__(self, data):
        self._data = data
        self._config = MockConfig()

    def PollDevice(self, i):
        return self._data[i]

    def Transmit(self, command):
        response = CecCommand(src=command.dst, dst=command.src)
        if command.cmd == CMD_POWER_STATUS[0]:
            response.cmd = CMD_POWER_STATUS[1]
            response.att = [1]
            self._config.GetCommandCallback()(response.raw)
        elif command.cmd == CMD_OSD_NAME[0]:
            response.cmd = CMD_OSD_NAME[1]
            response.att = (ord(i) for i in "Test")
            self._config.GetCommandCallback()(response.raw)
        elif command.cmd == CMD_VENDOR[0]:
            response.cmd = CMD_VENDOR[1]
            response.att = [0x00, 0x09, 0xB0]
            self._config.GetCommandCallback()(response.raw)
        elif command.cmd == CMD_PHYSICAL_ADDRESS[0]:
            response.cmd = CMD_PHYSICAL_ADDRESS[1]
            response.att = [0x09, 0xB0]
            self._config.GetCommandCallback()(response.raw)

    def CommandFromString(self, cmd: str) -> CecCommand:
        return CecCommand(cmd)

    def GetLogicalAddresses(self):
        return LogicalAddress(2)

    def GetCurrentConfiguration(self):
        return self._config
