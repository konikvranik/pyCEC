import asyncio
from unittest import TestCase

from pycec.commands import CecCommand
from pycec.const import CMD_POWER_STATUS, CMD_OSD_NAME, CMD_VENDOR, CMD_PHYSICAL_ADDRESS
from pycec.network import HDMINetwork, HDMIDevice


class TestHdmiNetwork(TestCase):
    def setUp(self):
        self._loop = asyncio.new_event_loop()

    def test_scan(self):
        network = HDMINetwork(MockConfig(), adapter=MockAdapter(
            [True, True, False, True, False, True, False, False, False, False, False, False, False, False, False,
             False]), scan_interval=0, loop=self._loop)
        network._scan_delay = 0
        #network.scan()
        self._loop.create_task(network.async_init())
        self._loop.create_task(network.async_scan())
        self._loop.run_until_complete(asyncio.sleep(1,loop=self._loop))

        self.assertIn(HDMIDevice(0), network.devices)
        device = network.get_device(0)
        self.assertEqual("Test0", device.osd_name)
        self.assertEqual(2, device.power_status)

        self.assertIn(HDMIDevice(1), network.devices)
        device = network.get_device(1)
        self.assertEqual("Test1", device.osd_name)
        self.assertEqual(2, device.power_status)

        self.assertNotIn(HDMIDevice(2), network.devices)

        self.assertIn(HDMIDevice(3), network.devices)
        device = network.get_device(3)
        self.assertEqual("Test3", device.osd_name)
        self.assertEqual(2, device.power_status)

    def test_devices(self):
        network = HDMINetwork(MockConfig(), adapter=MockAdapter(
            [True, True, False, True, False, True, False, False, False, False, False, False, False, False, False,
             False]), scan_interval=0, loop=self._loop)
        network._scan_delay = 0
        network.scan()
        #        clear_event_loop()
        for i in [0, 1, 3, 5]:
            self.assertIn(HDMIDevice(i), network.devices)
        for i in [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            self.assertNotIn(HDMIDevice(i), network.devices)
        for d in network.devices:
            d.stop()
        self._loop.stop()

    def tearDown(self):
        self._loop.stop()
        self._loop.run_forever()


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
        cmd = None
        att = None
        if command.cmd == CMD_POWER_STATUS[0]:
            cmd = CMD_POWER_STATUS[1]
            att = [2]
        elif command.cmd == CMD_OSD_NAME[0]:
            cmd = CMD_OSD_NAME[1]
            att = (ord(i) for i in ("Test%d" % command.dst))
        elif command.cmd == CMD_VENDOR[0]:
            cmd = CMD_VENDOR[1]
            att = [0x00, 0x09, 0xB0]
        elif command.cmd == CMD_PHYSICAL_ADDRESS[0]:
            cmd = CMD_PHYSICAL_ADDRESS[1]
            att = [0x09, 0xB0]
        response = CecCommand(cmd, src=command.dst, dst=command.src, att=att)
        self._config.GetCommandCallback()(">> " + response.raw)

    def CommandFromString(self, cmd: str) -> CecCommand:
        return CecCommand(cmd)

    def GetLogicalAddresses(self):
        return LogicalAddress(2)

    def GetCurrentConfiguration(self):
        return self._config

    def SetConfiguration(self, config):
        self._config = config
