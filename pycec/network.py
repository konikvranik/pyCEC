import asyncio
import functools
from functools import reduce
from multiprocessing import Queue
from typing import List

import time

from pycec import _LOGGER
from pycec.commands import CecCommand
from pycec.const import CMD_OSD_NAME, VENDORS, DEVICE_TYPE_NAMES, \
    CMD_ACTIVE_SOURCE, CMD_STREAM_PATH, ADDR_BROADCAST, CMD_DECK_STATUS, \
    CMD_AUDIO_STATUS
from pycec.const import CMD_PHYSICAL_ADDRESS, CMD_POWER_STATUS, CMD_VENDOR

DEFAULT_SCAN_INTERVAL = 30
DEFAULT_UPDATE_PERIOD = 30
DEFAULT_SCAN_DELAY = 1

UPDATEABLE = {CMD_POWER_STATUS: "_update_power_status",
              CMD_OSD_NAME: "_update_osd_name", CMD_VENDOR: "_update_vendor",
              CMD_PHYSICAL_ADDRESS: "_update_physical_address",
              CMD_DECK_STATUS: "_update_playing_status",
              CMD_AUDIO_STATUS: "_update_audio_status"}


class PhysicalAddress:
    def __init__(self, address):
        self._physical_address = int()
        if isinstance(address, (str,)):
            address = int(address.replace('.', '').replace(':', ''), 16)
        if isinstance(address, (tuple, list,)):
            if len(address) == 2:
                self._physical_address = int("%02x%02x" % tuple(address), 16)
            elif len(address) == 4:
                self._physical_address = int("%x%x%x%x" % tuple(address), 16)
            else:
                raise AttributeError("Incorrect count of members in list!")
        elif isinstance(address, (int,)):
            self._physical_address = address

    @property
    def asattr(self) -> List[int]:
        return [self._physical_address // 0x100,
                self._physical_address % 0x100]

    @property
    def asint(self) -> int:
        return self._physical_address

    @property
    def ascmd(self) -> str:
        return "%x%x:%x%x" % tuple(
            x for x in _to_digits(self._physical_address))

    @property
    def asstr(self) -> str:
        return ".".join(("%x" % x) for x in _to_digits(self._physical_address))

    def __str__(self):
        return self.asstr


class AbstractCecAdapter:
    def __init__(self):
        self._initialized = False
        self._loop = None

    def init(self, callback: callable = None):
        raise NotImplementedError

    def poll_device(self, device):
        raise NotImplementedError

    def get_logical_address(self):
        raise NotImplementedError

    def transmit(self, command: CecCommand):
        raise NotImplementedError

    def standby_devices(self):
        raise NotImplementedError

    def power_on_devices(self):
        raise NotImplementedError

    def set_command_callback(self, callback):
        raise NotImplementedError

    def shutdown(self):
        raise NotImplementedError

    @property
    def initialized(self):
        return self._initialized

    def set_event_loop(self, loop):
        self._loop = loop


class HDMIDevice:
    def __init__(self, logical_address: int, network=None,
                 update_period=DEFAULT_UPDATE_PERIOD,
                 loop=None):
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
        self._status = None
        self._task = None

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
    def status(self) -> int:
        return self._status

    @property
    def vendor_id(self) -> int:
        return self._vendor_id

    @property
    def vendor(self) -> str:
        return (
            VENDORS[self._vendor_id] if self._vendor_id in VENDORS else hex(
                self._vendor_id))

    @property
    def osd_name(self) -> str:
        return self._osd_name

    @property
    def is_on(self):
        return self.power_status == 0x00

    @property
    def is_off(self):
        return self.power_status == 0x01

    def turn_on(self):  # pragma: no cover
        self._loop.create_task(self.async_turn_on())

    @asyncio.coroutine
    def async_turn_on(self):  # pragma: no cover
        command = CecCommand(0x44, self.logical_address, att=[0x6d])
        yield from self.async_send_command(command)

    def turn_off(self):  # pragma: no cover
        self._loop.create_task(self.async_turn_off())

    @asyncio.coroutine
    def async_turn_off(self):  # pragma: no cover
        command = CecCommand(0x44, self.logical_address, att=[0x6c])
        yield from self.async_send_command(command)

    def toggle(self):  # pragma: no cover
        self._loop.create_task(self.async_toggle())

    @asyncio.coroutine
    def async_toggle(self):  # pragma: no cover
        command = CecCommand(0x44, self.logical_address, att=[0x40])
        yield from self.async_send_command(command)

    @property
    def type(self):
        return self._type

    @property
    def type_name(self):
        return (
            DEVICE_TYPE_NAMES[self.type] if self.type in range(6) else
            DEVICE_TYPE_NAMES[2])

    def update_callback(self, command: CecCommand):
        result = False
        for prop in filter(lambda x: x[1] == command.cmd, UPDATEABLE):
            getattr(self, UPDATEABLE[prop])(command)
            self._updates[prop[0]] = True
            result = True
        if result:  # pragma: no cover
            if self._update_callback:
                self._loop.call_soon_threadsafe(self._update_callback, self)
        return result

    def _update_osd_name(self, command):
        self._osd_name = reduce(lambda x, y: x + chr(y), command.att, "")

    def _update_vendor(self, command):
        self._vendor_id = reduce(lambda x, y: x * 0x100 + y, command.att)

    def _update_playing_status(self, command):
        self._status = command.att[0]

    def _update_power_status(self, command):
        self._power_status = command.att[0]

    def _update_physical_address(self, command):
        self._physical_address = PhysicalAddress(command.att[0:2])
        if len(command.att) > 2:
            self._type = command.att[2]

    def _update_audio_status(self, command):
        self._mute_status = bool(command.att[0] & 0x80)
        self._mute_value = command.att[0] & 0x7f
        pass

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    @asyncio.coroutine
    def async_run(self):
        _LOGGER.debug("Starting device %d", self.logical_address)
        while not self._stop:
            for prop in UPDATEABLE:
                if not self._stop:
                    yield from self.async_request_update(prop[0])
            start_time = self._loop.time()
            while not self._stop and self._loop.time() <= (
                start_time + self._update_period
            ):
                yield from asyncio.sleep(0.3, loop=self._loop)
        _LOGGER.info("HDMI device %s stopped.", self)  # pragma: no cover

    def stop(self):  # pragma: no cover
        _LOGGER.debug("HDMI device %s stopping", self)
        self._stop = True

    @asyncio.coroutine
    def async_request_update(self, cmd: int):
        self._updates[cmd] = False
        command = CecCommand(cmd)
        yield from self.async_send_command(command)

    def send_command(self, command):
        self._loop.create_task(self.async_send_command(command))

    @asyncio.coroutine
    def async_send_command(self, command: CecCommand):
        command.dst = self._logical_address
        yield from self._network.async_send_command(command)

    def active_source(self):
        self._loop.create_task(
            self._network.async_active_source(self.physical_address))

    @property
    def is_updated(self, cmd):
        return self._updates[cmd]

    def __eq__(self, other):
        return (isinstance(other, (
            HDMIDevice,)) and self.logical_address == other.logical_address)

    def __hash__(self):
        return self._logical_address

    def __str__(self):
        return "HDMI %d: %s, %s (%s), power %s" % (
            self.logical_address, self.vendor, self.osd_name,
            str(self.physical_address), self.power_status)

    def set_update_callback(self, callback):  # pragma: no cover
        self._update_callback = callback


class HDMINetwork:
    def __init__(self, adapter: AbstractCecAdapter,
                 scan_interval=DEFAULT_SCAN_INTERVAL, loop=None):
        self._running = False
        self._device_status = dict()
        self._managed_loop = loop is None
        if self._managed_loop:
            self._loop = asyncio.new_event_loop()
        else:
            _LOGGER.warn("Be aware! Network is using shared event loop!")
            self._loop = loop
        self._adapter = adapter
        self._adapter.set_event_loop(self._loop)
        self._scan_delay = DEFAULT_SCAN_DELAY
        self._scan_interval = scan_interval
        self._command_queue = Queue()
        self._devices = dict()
        self._command_callback = None
        self._device_added_callback = None
        self._initialized_callback = None
        self._device_removed_callback = None

    @property
    def initialized(self):
        return self._adapter.initialized

    def init(self):
        self._loop.create_task(self.async_init())

    @asyncio.coroutine
    def async_init(self):
        _LOGGER.debug("initializing")  # pragma: no cover
        _LOGGER.debug("setting callback")  # pragma: no cover
        self._adapter.set_command_callback(self.command_callback)
        _LOGGER.debug("Callback set")  # pragma: no cover
        task = self._adapter.init(self._initialized_callback)
        self._running = True
        while not (task.done() or task.cancelled()) and self._running:
            _LOGGER.debug("Init pending - %s", task)  # pragma: no cover
            yield from asyncio.sleep(1, loop=self._loop)
        _LOGGER.debug("Init done")  # pragma: no cover

    def scan(self):
        self._loop.create_task(self.async_scan())

    def _after_polled(self, device, task):
        self._device_status[device] = task.result()
        if self._device_status[device] and device not in self._devices:
            self._devices[device] = HDMIDevice(device, self, loop=self._loop)
            if self._device_added_callback:
                self._loop.call_soon_threadsafe(self._device_added_callback,
                                                self._devices[device])
            task = self._loop.create_task(self._devices[device].async_run())
            self._devices[device].task = task
            _LOGGER.debug("Found device %d", device)
        elif not self._device_status[device] and device in self._devices:
            self.get_device(device).stop()
            if self._device_removed_callback:
                self._loop.call_soon_threadsafe(self._device_removed_callback,
                                                self._devices[device])
            del (self._devices[device])

    @asyncio.coroutine
    def async_scan(self):
        _LOGGER.info("Looking for new devices...")
        if not self.initialized:
            _LOGGER.error("Device not initialized!!!")  # pragma: no cover
            return
        for d in range(15):
            task = self._adapter.poll_device(d)
            task.add_done_callback(functools.partial(self._after_polled, d))
            yield

    def send_command(self, command):
        self._loop.create_task(self.async_send_command(command))

    @asyncio.coroutine
    def async_send_command(self, command):
        if isinstance(command, str):
            command = CecCommand(command)
        _LOGGER.debug("<< %s", command)
        if command.src is None or command.src == 0xf:
            command.src = self._adapter.get_logical_address()
        self._loop.call_soon_threadsafe(self._adapter.transmit, command)

    def standby(self):
        self._loop.create_task(self.async_standby())

    @asyncio.coroutine
    def async_standby(self):
        _LOGGER.debug("Queuing system standby")  # pragma: no cover
        self._loop.call_soon_threadsafe(self._adapter.standby_devices)

    def power_on(self):
        self._loop.create_task(self.async_power_on())

    @asyncio.coroutine
    def async_power_on(self):
        _LOGGER.debug("Queuing power on")  # pragma: no cover
        self._loop.call_soon_threadsafe(self._adapter.power_on_devices)

    def active_source(self, source: PhysicalAddress):
        self._loop.create_task(self.async_active_source(source))

    @asyncio.coroutine
    def async_active_source(self, addr: PhysicalAddress):
        yield from self.async_send_command(
            CecCommand(CMD_ACTIVE_SOURCE, ADDR_BROADCAST, att=addr.asattr))
        yield from self.async_send_command(
            CecCommand(CMD_STREAM_PATH, ADDR_BROADCAST, att=addr.asattr))

    @property
    def devices(self) -> tuple:
        return tuple(self._devices.values())

    def get_device(self, i) -> HDMIDevice:
        return self._devices.get(i, None)

    @asyncio.coroutine
    def async_watch(self, loop=None):
        _LOGGER.debug("Start watching...")  # pragma: no cover
        if loop is None:
            loop = self._loop
        _LOGGER.debug("loop: %s", loop)
        while self._running:
            if self.initialized:
                _LOGGER.debug("Scanning...")  # pragma: no cover
                yield from self.async_scan()
                _LOGGER.debug("Sleep...")  # pragma: no cover
                start_time = self._loop.time()
                while (
                    self._loop.time() <= (start_time + self._scan_interval)
                    and self._running
                ):
                    yield from asyncio.sleep(0.3, loop=loop)
            else:
                _LOGGER.warning("Not initialized. Waiting for init.")
                yield from asyncio.sleep(1, loop=loop)
        _LOGGER.info("No watching anymore")

    def start(self):
        _LOGGER.info("HDMI network starting...")  # pragma: no cover
        self._running = True
        self._loop.create_task(self.async_init())
        self._loop.create_task(self.async_watch())
        if self._managed_loop:
            self._loop.run_in_executor(None, self._loop.run_forever)

    def command_callback(self, raw_command):
        _LOGGER.debug("%s", raw_command)  # pragma: no cover
        self._loop.call_soon_threadsafe(self._async_callback, raw_command)

    def _async_callback(self, raw_command):
        command = CecCommand(raw_command[3:])
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
                self._loop.call_soon_threadsafe(
                    self._command_callback, command)

    def stop(self):
        _LOGGER.debug("HDMI network shutdown.")  # pragma: no cover
        self._running = False
        for d in self._devices.values():
            d.stop()
        if self._managed_loop:
            self._loop.stop()
            while self._loop.is_running():
                time.sleep(.1)
            self._loop.close()
        self._adapter.shutdown()
        _LOGGER.info("HDMI network stopped.")  # pragma: no cover

    def set_command_callback(self, callback):
        self._command_callback = callback

    def set_new_device_callback(self, callback):
        self._device_added_callback = callback

    def set_device_removed_callback(self, callback):
        self._device_removed_callback = callback

    def set_initialized_callback(self, callback):
        self._initialized_callback = callback


def _to_digits(x: int) -> List[int]:
    for x in ("%04x" % x):
        yield int(x, 16)
