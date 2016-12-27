import asyncio
import logging
from unittest import TestCase

from pycec import _LOGGER
from pycec.commands import CecCommand
from pycec.const import CMD_POWER_STATUS, CMD_OSD_NAME, CMD_VENDOR, \
    CMD_PHYSICAL_ADDRESS, CMD_DECK_STATUS, CMD_AUDIO_STATUS
from pycec.network import HDMINetwork, HDMIDevice, AbstractCecAdapter


class TestHDMINetwork(TestCase):
    def setUp(self):

        # Configure logging
        _LOGGER.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        _LOGGER.addHandler(ch)

    def test_devices(self):
        loop = asyncio.get_event_loop()
        network = HDMINetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False,
             False, False, False, False, False,
             False]), scan_interval=0, loop=loop)
        network._scan_delay = 0
        # network._adapter.set_command_callback(network.command_callback)
        network.init()
        network.scan()
        loop.run_until_complete(asyncio.sleep(.1, loop))
        loop.stop()
        loop.run_forever()
        for i in [0, 1, 3, 5]:
            self.assertIn(HDMIDevice(i), network.devices)
        for i in [2, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]:
            self.assertNotIn(HDMIDevice(i), network.devices)
        for d in network.devices:
            d.stop()
        network.stop()
        loop.stop()
        loop.run_forever()

    def test_scan(self):
        loop = asyncio.get_event_loop()
        network = HDMINetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False,
             False, False, False, False, False, False]), scan_interval=0,
            loop=loop)
        network._scan_delay = 0
        # network._adapter.set_command_callback(network.command_callback)
        network.init()
        network.scan()
        loop.run_until_complete(asyncio.sleep(.1, loop))
        loop.stop()
        loop.run_forever()

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
        for d in network.devices:
            d.stop()
        network.stop()
        loop.stop()
        loop.run_forever()


class LogicalAddress:
    def __init__(self, i):
        self.primary = i


class MockAdapter(AbstractCecAdapter):
    def shutdown(self):
        pass

    def init(self, callback: callable = None):
        f = asyncio.Future()
        f.set_result(True)
        self._initialized = True
        return f

    def power_on_devices(self):
        pass

    def standby_devices(self):
        pass

    def set_command_callback(self, callback):
        self._command_callback = callback

    def __init__(self, data):
        self._data = data
        self._command_callback = None
        super().__init__()

    def poll_device(self, i):
        f = asyncio.Future()
        f.set_result(self._data[i])
        return f

    def transmit(self, command):
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
            att = [0x09, 0xB0, 0x02]
        elif command.cmd == CMD_DECK_STATUS[0]:
            cmd = CMD_DECK_STATUS[1]
            att = [0x09]
        elif command.cmd == CMD_AUDIO_STATUS[0]:
            cmd = CMD_AUDIO_STATUS[1]
            att = [0x65]
        response = CecCommand(cmd, src=command.dst, dst=command.src, att=att)
        self._command_callback(">> " + response.raw)

    def get_logical_address(self):
        return 2
