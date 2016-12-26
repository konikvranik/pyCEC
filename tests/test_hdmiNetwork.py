import asyncio
from unittest import TestCase

from pycec.commands import CecCommand
from pycec.const import CMD_POWER_STATUS, CMD_OSD_NAME, CMD_VENDOR, \
    CMD_PHYSICAL_ADDRESS
from pycec.network import HDMINetwork, HDMIDevice, AbstractCecAdapter


class TestHDMINetwork(TestCase):
    def test_devices(self):
        loop = asyncio.get_event_loop()
        network = HDMINetwork(MockAdapter(
            [True, True, False, True, False, True, False, False, False, False,
             False, False, False, False, False,
             False]), scan_interval=0, loop=loop)
        network._scan_delay = 0
        network._adapter.SetCommandCallback(network.command_callback)
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
        network._adapter.SetCommandCallback(network.command_callback)
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
        self._initialized = True

    def PowerOnDevices(self):
        pass

    def StandbyDevices(self):
        pass

    def SetCommandCallback(self, callback):
        self._command_callback = callback

    def __init__(self, data):
        self._data = data
        self._command_callback = None
        super().__init__()

    def PollDevice(self, i):
        f = asyncio.Future()
        f.set_result(self._data[i])
        return f

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
            att = [0x09, 0xB0, 0x02]
        response = CecCommand(cmd, src=command.dst, dst=command.src, att=att)
        self._command_callback(">> " + response.raw)

    def GetLogicalAddresses(self):
        return LogicalAddress(2)
