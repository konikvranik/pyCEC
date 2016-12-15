import asyncio
import time
from multiprocessing import Queue

from functools import reduce

from pycec import _LOGGER
from pycec.const import CMD_PHYSICAL_ADDRESS, CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, VENDORS, DEVICE_TYPE_NAMES
from pycec.datastruct import PhysicalAddress, CecCommand

LIB_CEC = {}

DEFAULT_SCAN_INTERVAL = 30
DFAULT_UPDATE_PERIOD = 30
DEFAULT_SCAN_DELAY = 1


class HdmiDevice:
    def __init__(self, logical_address: int, network=None, update_period=DFAULT_UPDATE_PERIOD):
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
        self._type = int()

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
        return VENDORS[self._vendor_id] if self._vendor_id in VENDORS else hex(self._vendor_id)

    @property
    def osd_name(self) -> str:
        return self._osd_name

    @property
    def is_on(self):
        return self.power_status == 0x00

    @property
    def is_off(self):
        return self.power_status == 0x01

    def turn_on(self):
        self._network._loop.create_task(self.async_turn_on())

    @asyncio.coroutine
    def async_turn_on(self):
        command = CecCommand(0x44, self.logical_address, att=[0x40])
        yield from self.async_send_command(command)

    def turn_off(self):
        self._network._loop.create_task(self.async_turn_off())

    @asyncio.coroutine
    def async_turn_off(self):
        command = CecCommand(0x44, self.logical_address, att=[0x6c])
        yield from self.async_send_command(command)

    @property
    def type(self):
        return self._type

    @property
    def type_name(self):
        return DEVICE_TYPE_NAMES[self.type] if self.type in DEVICE_TYPE_NAMES else DEVICE_TYPE_NAMES[0]

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network):
        self._network = network

    def update(self, command: CecCommand):
        if command.cmd == CMD_PHYSICAL_ADDRESS[1]:
            self._physical_address = PhysicalAddress(command.att[0:2])
            self._type = command.att[2]
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
            self._osd_name = reduce(lambda x, y: x + chr(y), command.att, "")
            self._updates[CMD_OSD_NAME[0]] = True
            return True
        return False

    @asyncio.coroutine
    def async_run(self):
        _LOGGER.debug("Starting device %d", self.logical_address)
        while not self._stop:
            yield from self.async_request_update(CMD_POWER_STATUS[0])
            yield from self.async_request_update(CMD_OSD_NAME[0])
            yield from self.async_request_update(CMD_VENDOR[0])
            yield from self.async_request_update(CMD_PHYSICAL_ADDRESS[0])
            yield from asyncio.sleep(self._update_period, loop=self._network._loop)

    def stop(self):
        self._stop = True

    @asyncio.coroutine
    def async_request_update(self, cmd: int):
        self._updates[cmd] = False
        command = CecCommand(cmd, self.logical_address)
        yield from self.async_send_command(command)

    @property
    def is_updated(self, cmd):
        return self._updates[cmd]

    def __eq__(self, other):
        return isinstance(other, (HdmiDevice,)) and self.logical_address == other.logical_address

    def __hash__(self):
        return self._logical_address

    def __str__(self):
        return "HDMI %d: %s, %s (%s), power %s" % (
            self.logical_address, self.vendor, self.osd_name, str(self.physical_address), self.power_status)

    def update_power(self):
        self.update(CMD_POWER_STATUS[0])

    @asyncio.coroutine
    def async_send_command(self, command):
        yield from self._network._loop.run_in_executor(None, self.network.send_command, command)


def _init_cec(cecconfig=None):
    import cec
    lib_cec = cec.ICECAdapter.Create(cecconfig)
    adapter = None
    adapters = lib_cec.DetectAdapters()
    for adapter in adapters:
        _LOGGER.info("found a CEC adapter:")
        _LOGGER.info("port:     " + adapter.strComName)
        _LOGGER.info(
            "vendor:   " + (VENDORS[adapter.iVendorId] if adapter.iVendorId in VENDORS else hex(adapter.iVendorId)))
        _LOGGER.info("product:  " + hex(adapter.iProductId))
        adapter = adapter.strComName
    if adapter is None:
        _LOGGER.warning("No adapters found")
        return None
    else:
        if lib_cec.Open(adapter):
            _LOGGER.info("connection opened")
            return lib_cec
        else:
            _LOGGER.error("failed to open a connection to the CEC adapter")
            return lib_cec


class HdmiNetwork:
    def __init__(self, config, adapter=None, scan_interval=DEFAULT_SCAN_INTERVAL, loop=None):
        _LOGGER.info("Network init...")
        if loop is None:
            self._loop = asyncio.new_event_loop()
        else:
            _LOGGER.warn("Be aware! Network is using shared event loop!")
            self._loop = loop
        self._scan_delay = DEFAULT_SCAN_DELAY
        self._scan_interval = scan_interval
        self._command_queue = Queue()
        self._device_status = dict()
        self._devices = dict()
        _LOGGER.debug("Importing cec")
        config.SetCommandCallback(self.command_callback)
        self._adapter = adapter
        if adapter is not None:
            adapter.SetConfiguration(config)
        else:
            self._adapter = _init_cec(config)
        _LOGGER.debug("Callback set")

    def scan(self):
        _LOGGER.info("Looking for new devices...")
        for d in range(15):
            self._device_status[d] = self._adapter.PollDevice(d)
            time.sleep(self._scan_delay)
        new_devices = {k: HdmiDevice(k, self) for (k, v) in
                       filter(lambda x: x[0] not in self._devices, filter(lambda x: x[1], self._device_status.items()))}

        if new_devices:
            _LOGGER.info("Found new devices: %s", new_devices)
        else:
            _LOGGER.info("No new devices")
        self._devices.update(new_devices)
        for d in new_devices.values():
            _LOGGER.info("Adding device %d", d.logical_address)
            self._loop.create_task(d.async_run())
        for i in filter(lambda x: not x[1], self._device_status.items()):
            if i in self._devices:
                self.get_device(i).stop()

    def send_command(self, command: CecCommand):
        if command.src is None:
            command.src = self.local_address
        self._adapter.Transmit(self._adapter.CommandFromString(command.raw))

    @property
    def local_address(self):
        return self._adapter.GetLogicalAddresses().primary

    @property
    def devices(self) -> tuple:
        return tuple(self._devices.values())

    def get_device(self, i) -> HdmiDevice:
        return self._devices[i]

    @asyncio.coroutine
    def async_watch(self, loop=None):
        _LOGGER.debug("Start watching...")
        if loop is None:
            loop = self._loop
        while True:
            yield from loop.run_in_executor(None, self.scan)
            yield from asyncio.sleep(self._scan_interval, loop=loop)

    def start(self):
        self._loop.create_task(self.async_watch())
        asyncio.get_event_loop().run_in_executor(None, self._loop.run_forever)

    def command_callback(self, raw_command):
        self._loop.call_soon(self._async_callback, raw_command)

    def _async_callback(self, raw_command):
        command = CecCommand(raw_command[3:])
        updated = False
        if command.src == 15:
            for i in range(15):
                updated |= self.get_device(i).update(command)
        elif command.src in self._devices:
            updated = self.get_device(command.src).update(command)
        if not updated:
            _LOGGER.info("Queuing command %s", str(command))
            self._command_queue.put(command)

    def stop(self):
        self._loop.stop()
