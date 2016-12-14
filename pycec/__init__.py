import asyncio
import logging
import time
from functools import reduce
from multiprocessing import Queue
from typing import Iterable

from pycec.const import CMD_PHYSICAL_ADDRESS, CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, VENDORS
from pycec.datastruct import PhysicalAddress, CecCommand

_LOGGER = logging.getLogger(__name__)

LIB_CEC = {}

DEFAULT_SCAN_INTERVAL = 1


class HdmiDevice:
    def __init__(self, logical_address: int, network=None, update_period=60):
        self._logical_address = logical_address
        self.name = "hdmi_%x" % logical_address
        self._physical_address = PhysicalAddress
        self._power_status = int()
        self._audio_status = int()
        self._is_active_source = False
        self._vendor_id = int()
        self._menu_language = str()
        self._osd_name = str()
        self._audio_mode_status = int()
        self._deck_status = int()
        self._tuner_status = int()
        self._menu_status = int()
        self._record_status = int()
        self._timer_cleared_status = int()
        self._timer_status = int()
        self._network = network
        self._updates = dict()
        self._stop = False
        self._update_period = update_period

    @property
    def logical_address(self) -> int:
        return self._logical_address

    @property
    def physical_address(self) -> PhysicalAddress:
        return self._physical_address

    @property
    def power_status(self) -> int:
        return self._power_status

    @property
    def vendor_id(self) -> int:
        return self._vendor_id

    @property
    def vendor(self) -> str:
        return VENDORS[self._vendor_id]

    @property
    def osd_name(self) -> str:
        return self._osd_name

    @property
    def is_on(self):
        return self.power_status == 0x00

    @property
    def is_off(self):
        return self.power_status == 0x01

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network):
        self._network = network

    def update(self, command: CecCommand):
        if command.cmd == CMD_PHYSICAL_ADDRESS[1]:
            self._physical_address = PhysicalAddress(command.att)
            self._updates[CMD_PHYSICAL_ADDRESS[0]] = True
            return True
        elif command.cmd == CMD_POWER_STATUS[1]:
            self._power_status = command.att[0]
            self._updates[CMD_POWER_STATUS[0]] = True
            return True
        elif command.cmd == CMD_VENDOR[1]:
            self._vendor_id = reduce(lambda x, y: x * 0x100 + y, command.att)
            self._updates[CMD_VENDOR[0]] = True
            return True
        elif command.cmd == CMD_OSD_NAME[1]:
            self._osd_name = "".join(map(lambda x: chr(x), command.att))
            self._updates[CMD_OSD_NAME[0]] = True
            return True
        return False

    @asyncio.coroutine
    def run(self):
        while not self._stop:
            asyncio.get_event_loop().run_in_executor(None, self.request_power_status)
            asyncio.get_event_loop().run_in_executor(None, self.request_name)
            asyncio.get_event_loop().run_in_executor(None, self.request_vendor)
            asyncio.get_event_loop().run_in_executor(None, self.request_physical_address)
            yield from asyncio.sleep(self._update_period)

    def stop(self):
        self._stop = True

    def request_update(self, cmd: int):
        self._updates[cmd] = False
        self.network.send_command(CecCommand(cmd, self.logical_address))

    def request_power_status(self):
        self.request_update(CMD_POWER_STATUS[0])

    def request_name(self):
        self.request_update(CMD_OSD_NAME[0])

    def request_physical_address(self):
        self.request_update(CMD_PHYSICAL_ADDRESS[0])

    def request_vendor(self):
        self.request_update(CMD_VENDOR[0])

    @property
    def is_updated(self, cmd):
        return self._updates[cmd]

    def __eq__(self, other):
        return isinstance(other, (HdmiDevice,)) and self.logical_address == other.logical_address

    def __hash__(self):
        return self._logical_address


class HdmiNetwork:
    def __init__(self, adapter, scan_interval=DEFAULT_SCAN_INTERVAL):
        self._scan_interval = scan_interval
        self._command_queue = Queue()
        self._adapter = adapter
        self._device_status = dict()
        self._devices = dict()
        adapter.GetCurrentConfiguration().SetCommandCallback(self.command_callback)

    def scan(self):
        for d in range(15):
            self._device_status[d] = self._adapter.PollDevice(d)
            time.sleep(self._scan_interval)
        new_devices = {k: HdmiDevice(k, self) for (k, v) in
                       filter(lambda x: x[0] not in self._devices, filter(lambda x: x[1], self._device_status.items()))}
        self._devices.update(new_devices)
        for d in new_devices.values():
            asyncio.async(d.run())
            for i in filter(lambda x: not x[1], self._device_status.items()):
                if i in self._devices:
                    self.get_device(i).stop()

    def send_command(self, command: CecCommand):
        if command.src is None:
            command.src = self.local_address
        self._adapter.Transmit(
            self._adapter.CommandFromString(command.raw))

    @property
    def local_address(self):
        return self._adapter.GetLogicalAddresses().primary

    @property
    def devices(self) -> Iterable:
        return self._devices.values()

    def get_device(self, i) -> HdmiDevice:
        return self._devices[i]

    def watch(self):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, self.scan)
        loop.run_forever()
        loop.close()

    def command_callback(self, raw_command: str):
        command = CecCommand(raw_command)
        updated = False
        if command.src == 15:
            for i in range(15):
                updated |= self.get_device(i).update(command)
        else:
            updated = self.get_device(command.src).update(command)
        if not updated:
            self._command_queue.put(command)


class CecClient:
    def __init__(self, name: str = None):
        """initialize libCEC"""
        cecconfig = None  # cec.libcec_configuration()
        cecconfig.strDeviceName = name
        cecconfig.bActivateSource = 0
        cecconfig.bMonitorOnly = 0
        # cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
        # cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        cecconfig.strDeviceLanguage = "cze"
        cecconfig.SetKeyPressCallback(self.cec_key_press_callback)
        cecconfig.SetCommandCallback(self.cec_command_callback)

        import cec
        lib_cec = cec.ICECAdapter.Create(cecconfig)

        # print libCEC version and compilation information
        _LOGGER.info("libCEC version " + lib_cec.VersionToString(
            cecconfig.serverVersion) + " loaded: " + lib_cec.GetLibInfo())

        # search for adapters
        adapter = None
        adapters = lib_cec.DetectAdapters()
        for adapter in adapters:
            _LOGGER.info("found a CEC adapter:")
            _LOGGER.info("port:     " + adapter.strComName)
            _LOGGER.info("vendor:   " + hex(adapter.iVendorId))
            _LOGGER.info("product:  " + hex(adapter.iProductId))
            adapter = adapter.strComName
        if adapter is None:
            _LOGGER.warning("No adapters found")
        else:
            if lib_cec.Open(adapter):
                lib_cec.GetCurrentConfiguration(cecconfig)
                _LOGGER.info("connection opened")
            else:
                _LOGGER.error("failed to open a connection to the CEC adapter")

    def cec_key_press_callback(self, key, duration):
        """key press callback"""
        _LOGGER.info("[key pressed] " + str(key))
        return 0

    def cec_command_callback(self, command):
        """command received callback"""
        return 0


if __name__ == '__main__':
    print("pa int: %s" % PhysicalAddress(0x12cd))
    print("pa str: %s" % PhysicalAddress("12:cd"))
    print("pa tuple: %s" % PhysicalAddress((0x12, 0xcd)))
    print("pa list: %s" % PhysicalAddress([0x12, 0xcd]))

    print("cmd num: %s" % CecCommand(0x1, 0x2, 0x8f, [0x01, 0xab]))
    print("cmd str: %s" % CecCommand(raw="12:8f:01:ab"))
