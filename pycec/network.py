import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Queue

from functools import reduce

from pycec import _LOGGER, CecConfig
from pycec.commands import CecCommand
from pycec.const import CMD_PHYSICAL_ADDRESS, CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, VENDORS, DEVICE_TYPE_NAMES
from pycec.datastruct import PhysicalAddress

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_UPDATE_PERIOD = 30
DEFAULT_SCAN_DELAY = 1


class HDMIDevice:
    def __init__(self, logical_address: int, network=None, update_period=DEFAULT_UPDATE_PERIOD,
                 loop=asyncio.get_event_loop()):
        self._loop = loop
        self._logical_address = logical_address
        self.name = "hdmi_%x" % logical_address
        self._physical_address = None
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
        self._update_callback = None

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
        self._loop.create_task(self.async_turn_on())

    @asyncio.coroutine
    def async_turn_on(self):
        command = CecCommand(0x44, self.logical_address, att=[0x40])
        yield from self.async_send_command(command)

    def turn_off(self):
        self._loop.create_task(self.async_turn_off())

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

    def update_callback(self, command: CecCommand):
        _LOGGER.debug("Updating device  ")
        result = False
        if command.cmd == CMD_PHYSICAL_ADDRESS[1]:
            self._physical_address = PhysicalAddress(command.att[0:2])
            self._type = command.att[2]
            self._updates[CMD_PHYSICAL_ADDRESS[0]] = True
            result = True
        elif command.cmd == CMD_POWER_STATUS[1]:
            self._power_status = command.att[0]
            self._updates[CMD_POWER_STATUS[0]] = True
            result = True
        elif command.cmd == CMD_VENDOR[1]:
            self._vendor_id = reduce(lambda x, y: x * 0x100 + y, command.att)
            self._updates[CMD_VENDOR[0]] = True
            result = True
        elif command.cmd == CMD_OSD_NAME[1]:
            self._osd_name = reduce(lambda x, y: x + chr(y), command.att, "")
            self._updates[CMD_OSD_NAME[0]] = True
            result = True
        if result:
            if self._update_callback:
                self._loop.call_soon_threadsafe(self._update_callback, self)
        return result

    @asyncio.coroutine
    def async_run(self):
        _LOGGER.debug("Starting device %d", self.logical_address)
        while not self._stop:
            yield from self.async_request_update(CMD_POWER_STATUS[0])
            yield from self.async_request_update(CMD_OSD_NAME[0])
            yield from self.async_request_update(CMD_VENDOR[0])
            yield from self.async_request_update(CMD_PHYSICAL_ADDRESS[0])
            yield from asyncio.sleep(self._update_period, loop=self._loop)

    def stop(self):
        self._stop = True

    @asyncio.coroutine
    def async_request_update(self, cmd: int):
        _LOGGER.debug("Requesting device update...")
        self._updates[cmd] = False
        command = CecCommand(cmd, self.logical_address)
        yield from self.async_send_command(command)

    @asyncio.coroutine
    def async_send_command(self, command):
        _LOGGER.debug("Device sending command %s", command)
        yield from self._network.async_send_command(command)

    @property
    def is_updated(self, cmd):
        return self._updates[cmd]

    def __eq__(self, other):
        return isinstance(other, (HDMIDevice,)) and self.logical_address == other.logical_address

    def __hash__(self):
        return self._logical_address

    def __str__(self):
        return "HDMI %d: %s, %s (%s), power %s" % (
            self.logical_address, self.vendor, self.osd_name, str(self.physical_address), self.power_status)

    def set_update_callback(self, callback):
        self._update_callback = callback


class HDMINetwork:
    def __init__(self, config, scan_interval=DEFAULT_SCAN_INTERVAL, loop=None, adapter=None):
        if loop is None:
            self._loop = asyncio.new_event_loop()
        else:
            _LOGGER.warn("Be aware! Network is using shared event loop!")
            self._loop = loop
        self._config = config
        self._adapter = adapter
        self._scan_delay = DEFAULT_SCAN_DELAY
        self._scan_interval = scan_interval
        self._command_queue = Queue()
        self._device_status = dict()
        self._devices = dict()
        self._io_executor = ThreadPoolExecutor(1)
        self._command_callback = None
        self._device_added_callback = None
        self._initialized_callback = None
        self._device_removed_callback = None

    def _init_cec(self):
        import cec
        if isinstance(self._config, (CecConfig,)):
            self._config = self._config.cecconfig
        if not self._config.clientVersion:
            self._config.clientVersion = cec.LIBCEC_VERSION_CURRENT
        _LOGGER.debug("Initing CEC...")
        adapter = cec.ICECAdapter.Create(self._config)
        _LOGGER.debug("Created adapter")
        a = None
        adapters = adapter.DetectAdapters()
        for a in adapters:
            _LOGGER.info("found a CEC adapter:")
            _LOGGER.info("port:     " + a.strComName)
            _LOGGER.info(
                "vendor:   " + (VENDORS[a.iVendorId] if a.iVendorId in VENDORS else hex(a.iVendorId)))
            _LOGGER.info("product:  " + hex(a.iProductId))
            a = a.strComName
        if a is None:
            _LOGGER.warning("No adapters found")
        else:
            if adapter.Open(a):
                _LOGGER.info("connection opened")
                self._adapter = adapter
            else:
                _LOGGER.error("failed to open a connection to the CEC adapter")
        if self._initialized_callback:
            self._initialized_callback(self)

    @property
    def initialized(self):
        return self._adapter is not None

    @asyncio.coroutine
    def async_init(self):
        _LOGGER.debug("initializing")
        config = self._config
        _LOGGER.debug("setting callback")
        config.SetCommandCallback(self.command_callback)
        _LOGGER.debug("Callback set")
        task = self._loop.run_in_executor(self._io_executor, self._init_cec)
        while not (task.done() or task.cancelled()):
            _LOGGER.debug("Init pending")
            yield from asyncio.sleep(1, loop=self._loop)
        _LOGGER.debug("Init done")

    def scan(self):
        self._loop.create_task(self.async_scan())

    @asyncio.coroutine
    def async_scan(self):
        _LOGGER.info("Looking for new devices...")
        if not self.initialized:
            _LOGGER.error("Device not initialized!!!")
            return
        for d in range(15):
            self._loop.run_in_executor(self._io_executor, self._io_poll_device, d)
            yield

    def _io_poll_device(self, d):
        self._device_status[d] = self._adapter.PollDevice(d)
        if self._device_status[d] and d not in self._devices:
            self._devices[d] = HDMIDevice(d, self, loop=self._loop)
            if self._device_added_callback:
                self._loop.call_soon_threadsafe(self._device_added_callback, self._devices[d])
            self._loop.create_task(self._devices[d].async_run())
            _LOGGER.debug("Found device %d", d)
        elif not self._device_status[d] and d in self._devices:
            self.get_device(d).stop()
            if self._device_removed_callback:
                self._loop.call_soon_threadsafe(self._device_removed_callback, self._devices[d])
            del (self._devices[d])

    def send_command(self, command):
        self._loop.create_task(self.async_send_command(command))

    @asyncio.coroutine
    def async_send_command(self, command):
        if isinstance(command, str):
            command = CecCommand(command)
        _LOGGER.debug("Queuing command %s", command)
        self._loop.call_soon_threadsafe(self.io_send_command, command)

    def io_send_command(self, command: CecCommand):
        _LOGGER.debug("Sending command %s", command)
        if command.src is None or command.src == 0xf:
            command.src = self._adapter.GetLogicalAddresses().primary
        self._loop.run_in_executor(self._io_executor, self._adapter.Transmit,
                                   self._adapter.CommandFromString(command.raw))

    @property
    def devices(self) -> tuple:
        return tuple(self._devices.values())

    def get_device(self, i) -> HDMIDevice:
        return self._devices[i]

    @asyncio.coroutine
    def async_watch(self, loop=None):
        _LOGGER.debug("Start watching...")
        if loop is None:
            loop = self._loop
        while True:
            if self.initialized:
                _LOGGER.debug("Sacnning...")
                yield from self.async_scan()
                _LOGGER.debug("Sleep...")
                yield from asyncio.sleep(self._scan_interval, loop=loop)
            else:
                _LOGGER.warning("Not initialized. Waiting for init.")
                yield from asyncio.sleep(1, loop=loop)

    def start(self):
        self._loop.create_task(self.async_init())
        self._loop.create_task(self.async_watch())
        if not self._loop.is_running():
            self._loop.run_in_executor(None, self._loop.run_forever)

    def command_callback(self, raw_command):
        _LOGGER.debug("Queuing callback")
        self._loop.call_soon_threadsafe(self._async_callback, raw_command)

    def _async_callback(self, raw_command):
        command = CecCommand(raw_command[3:])
        _LOGGER.debug("In callback %s", command)
        updated = False
        if command.src == 15:
            for i in range(15):
                updated |= self.get_device(i).update_callback(command)
                pass
        elif command.src in self._devices:
            updated = self.get_device(command.src).update_callback(command)
            pass
        if not updated:
            if self._command_callback:
                self._loop.call_soon_threadsafe(self._command_callback, command)

    def stop(self):
        self._loop.stop()

    def set_commnd_callback(self, callback):
        self._command_callback = callback

    def set_new_device_callback(self, callback):
        self._device_added_callback = callback

    def set_device_removed_callback(self, callback):
        self._device_removed_callback = callback

    def set_initialized_callback(self, callback):
        self._initialized_callback = callback
