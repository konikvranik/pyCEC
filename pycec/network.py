import asyncio
from asyncio import AbstractEventLoop
from functools import reduce
from multiprocessing import Queue
from typing import List

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
        return "%x%x:%x%x" % tuple(x for x in _to_digits(self._physical_address))

    @property
    def asstr(self) -> str:
        return ".".join(("%x" % x) for x in _to_digits(self._physical_address))

    def __str__(self):
        return self.asstr


class AbstractCecAdapter:
    """
    Facilitates an abstract interface for handling Consumer Electronics Control (CEC) commands and device management.

    This class acts as a foundational interface for interacting with devices that support CEC commands. The primary
    purpose is to define methods for initializing CEC communication, sending commands, polling devices, and managing
    device states. It also provides the ability to set event loops and command callbacks. Concrete implementations of
    this class should handle the actual details of communication and interaction with the devices.

    :ivar _initialized: Indicates whether the adapter is initialized.
    :type _initialized: bool
    :ivar _loop: Reference to the event loop associated with the adapter.
    :type _loop: AbstractEventLoop
    :ivar _command_callback: Stores the callback function for command handling.
    :type _command_callback: callable or None
    """

    def __init__(self, callback = None):
        self._initialized = False
        self._loop: AbstractEventLoop = None
        self._command_callback = callback

    def init(self, callback: callable = None):
        self._loop.run_until_complete(self.async_init(callback))

    async def async_init(self, callback: callable = None):
        """
        Initializes an instance with an optional callback function.

        The constructor provides an interface to initialize the object, allowing an
        optional callable callback function to be provided.

        :param callback: A callable object or function that can be executed or invoked.
        :return: None
        """
        raise NotImplementedError

    async def async_poll_device(self, device) -> bool:
        """
        Polls the given device and returns a Future object.
        The returned Future allows asynchronous handling of the polling operation.

        :param device: The device to poll.
        :type device: Any
        :return: A Future object representing the polling operation.
        :rtype: concurrent.futures.Future
        """
        raise NotImplementedError

    def get_logical_address(self):
        """
        Retrieves the logical address of the current instance.

        It is designed to provide a specific logical address relating to the instance's domain.
         The logical address concept is context-dependent and should be appropriately
        defined in the implementing subclass.

        :raises NotImplementedError: Raised when the method is not implemented
            in a subclass.
        :rtype: None
        :return: None, as the method is abstract and must be implemented
            by subclasses.
        """
        raise NotImplementedError

    async def async_transmit(self, command: CecCommand):
        """
        Asynchronously transmits a given CEC (Consumer Electronics Control) command using an executor.

        This method schedules the transmission of a CEC command to be executed asynchronously
        in a separate thread or process outside the main event loop, using the event loop's
        executor. It ensures non-blocking execution, enabling other coroutine tasks to proceed.

        :param command: The CEC command to be transmitted.
        :type command: CecCommand
        :return: None
        """
        raise NotImplementedError

    async def async_standby_devices(self):
        """
        Places devices into standby mode. This function defines the specific logic for entering standby mode.

        :raises NotImplementedError: Indicates that the method is not implemented in the
                                      subclass.
        :return: None
        """
        raise NotImplementedError

    async def async_power_on_devices(self):
        """
        Power on the devices managed by this instance.

        This method is intended to activate or turn on the devices associated
        with the instance.

        :raises NotImplementedError: When called on a base class or abstract
            implementation without an override.
        :return: None
        """
        raise NotImplementedError

    def set_on_command_callback(self, callback):
        """
        Sets the callback function for handling commands. The provided callback function
        will be invoked whenever a command needs to be processed, allowing customization
        of command processing behavior.

        :param callback: The function to be called when a command is triggered.
        :type callback: Callable[[Any], None]
        :return: None
        """
        self._command_callback = callback

    async def async_shutdown(self):
        """
        Shuts down the operation of a component or service implementing this method.

        This method is expected to be implemented by subclasses to define specific
        shutdown behavior. Calling this method in the base class directly without an
        implementation will result in `NotImplementedError`.

        :raises NotImplementedError: If the method is not implemented by a subclass.
        """
        raise NotImplementedError

    @property
    def initialized(self):
        return self._initialized

    def set_event_loop(self, loop):
        """
        Sets the event loop for the current instance.

        This method allows for assigning an event loop to the object,
        which will then be stored internally for further use. Use
        this function to manage or update the event loop of a
        specific instance.

        :param loop: The event loop to be set for the instance.
        :type loop: AbstractEventLoop
        :return: None
        """
        self._loop = loop


class HDMIDevice:
    """
    Represents an HDMI device connected to a network for communication and control.

    This class manages the state and properties of an HDMI device, such as its
    physical and logical addresses, power status, vendor information, and audio
    settings. It provides methods for controlling the device (e.g., turning it on
    or off, toggling states) and retrieving or updating its status. The class also
    handles asynchronous communication for sending and receiving commands over the
    HDMI network.

    :ivar name: A unique name for the HDMI device based on its logical address.
    :type name: str
    :ivar _loop: The event loop used for asynchronous operations with the device.
    :type _loop: asyncio.AbstractEventLoop
    :ivar _logical_address: Logical address of the HDMI device, representing
        its unique identifier on the HDMI network.
    :type _logical_address: int
    :ivar _physical_address: Physical address of the HDMI device, representing
        its connectivity structure on the HDMI network.
    :type _physical_address: PhysicalAddress
    :ivar _power_status: Current power state of the HDMI device.
    :type _power_status: int
    :ivar _audio_status: Current audio status of the HDMI device.
    :type _audio_status: int
    :ivar _is_active_source: Indicates if the device is the active HDMI source.
    :type _is_active_source: bool
    :ivar _vendor_id: Vendor ID representing the manufacturer of the device.
    :type _vendor_id: int
    :ivar _menu_language: Language code of the device's menu settings.
    :type _menu_language: str
    :ivar _osd_name: The On-Screen Display (OSD) name of the device.
    :type _osd_name: str
    :ivar _audio_mode_status: Status of the audio mode for the device.
    :type _audio_mode_status: int
    :ivar _volume_status: The current volume status of the device,
        indicating its audio level.
    :type _volume_status: int
    :ivar _mute_status: Indicates whether the device's audio is muted.
    :type _mute_status: bool
    :ivar _deck_status: Represents the playback status of the device.
    :type _deck_status: int
    :ivar _tuner_status: Represents the tuner status of the device.
    :type _tuner_status: int
    :ivar _menu_status: Indicates the menu state of the device.
    :type _menu_status: int
    :ivar _record_status: Represents the recording status of the device.
    :type _record_status: int
    :ivar _timer_cleared_status: Indicates whether the device's timer
        has been cleared.
    :type _timer_cleared_status: int
    :ivar _timer_status: Current timer status of the device.
    :type _timer_status: int
    :ivar _network: HDMI network interface used for communication with the device.
    :type _network: Any
    :ivar _updates: A mapping of updateable properties and their update states.
    :type _updates: dict
    :ivar _stop: Indicates whether the device's execution loop should stop.
    :type _stop: bool
    :ivar _update_period: Interval for periodic device updates.
    :type _update_period: float
    :ivar _type: Represents the type of the HDMI device.
    :type _type: int
    :ivar _update_callback: A callback function that gets invoked when the
        device's state updates.
    :type _update_callback: Callable
    :ivar _status: Represents the detailed status of the device.
    :type _status: Any
    :ivar _task: The asyncio task managing the device's operation.
    :type _task: asyncio.Task
    """

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
        self._volume_status = int()
        self._mute_status = False
        self._deck_status = int()
        self._tuner_status = int()
        self._menu_status = int()
        self._record_status = int()
        self._timer_cleared_status = int()
        self._timer_status = int()
        self._network = network
        self._updates = {cmd: False for cmd in UPDATEABLE}
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

    async def async_turn_on(self):  # pragma: no cover
        command = CecCommand(0x44, self.logical_address, att=[0x6d])
        await self.async_send_command(command)

    def turn_off(self):  # pragma: no cover
        self._loop.create_task(self.async_turn_off())

    async def async_turn_off(self):  # pragma: no cover
        command = CecCommand(0x44, self.logical_address, att=[0x6c])
        await self.async_send_command(command)

    def toggle(self):  # pragma: no cover
        self._loop.create_task(self.async_toggle())

    async def async_toggle(self):  # pragma: no cover
        command = CecCommand(0x44, self.logical_address, att=[0x40])
        await self.async_send_command(command)

    @property
    def type(self):
        return self._type

    @property
    def type_name(self):
        return (
            DEVICE_TYPE_NAMES[self.type] if self.type in range(6) else
            DEVICE_TYPE_NAMES[2])

    @property
    def mute_status(self) -> bool:
        return self._mute_status

    @property
    def volume_status(self) -> int:
        return self._volume_status

    async def async_update(self, command: CecCommand):
        """
        Updates a component's properties based on a received command. The method verifies
        if the command matches any predefined updatable properties and updates them accordingly.
        Triggers a callback if any updates were made.

        :param command: The command containing information to update the component
                        properties.
        :type command: CecCommand
        :return: Boolean indicating whether any updates were successfully applied.
        :rtype: bool
        """
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
        raw_volume_status = command.att[0] & 0x7f
        if raw_volume_status == 0x7f:
            # Volume is unknown
            self._updates[CMD_AUDIO_STATUS[0]] = False
        else:
            # Valid volumes cover a range of 0-100, just clamp invalid values
            self._volume_status = min(raw_volume_status, 100)

    @property
    def task(self):
        return self._task

    @task.setter
    def task(self, task):
        self._task = task

    async def async_run(self):
        """
        Asynchronously executes a loop for updating device properties and managing periodic
        wait cycles until the stop condition is met.

        The function iterates over a list of updateable properties and requests updates
        only if the stop condition has not been triggered. After each set of property
        updates, it waits for a defined update period, periodically checking if the
        stop condition has been met. Once the loop exits, the function logs that the
        device has stopped.

        :param self: Represents the instance of the class this method belongs to.
        :type self: object

        :return: Does not return any value. Represents a coroutine that must be awaited.
        :rtype: None
        """
        _LOGGER.debug("Starting device %d", self.logical_address)
        while not self._stop:
            for prop in UPDATEABLE:
                if not self._stop:
                    await self.async_request_update(prop[0])
            start_time = self._loop.time()
            while not self._stop and self._loop.time() <= (
                    start_time + self._update_period
            ):
                await asyncio.sleep(0.3)
        _LOGGER.info("HDMI device %s stopped.", self)  # pragma: no cover

    def stop(self):  # pragma: no cover
        _LOGGER.debug("HDMI device %s stopping", self)
        self._stop = True

    async def async_request_update(self, cmd: int):
        self._updates[cmd] = False
        command = CecCommand(cmd)
        await self.async_send_command(command)

    def send_command(self, command):
        self._loop.create_task(self.async_send_command(command))

    async def async_send_command(self, command: CecCommand):
        command.dst = self._logical_address
        await self._network.async_send_command(command)

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
    """
    Represents a network for managing and monitoring HDMI devices using the
    CEC (Consumer Electronics Control) protocol.

    This class provides a mechanism to control and monitor HDMI devices
    connected through an HDMI-CEC adapter. It supports asynchronous operations
    to manage devices, send commands, and handle events via callbacks.

    :ivar _adapter: The CEC adapter used for communication and control.
    :type _adapter: AbstractCecAdapter
    :ivar _loop: The asyncio event loop used for asynchronous operations.
    :type _loop: asyncio.AbstractEventLoop
    :ivar _running: Indicates whether the HDMI network is currently running.
    :type _running: bool
    :ivar _scan_delay: The delay duration to apply during scanning operations.
    :type _scan_delay: float
    :ivar _scan_interval: Interval between scan operations for detecting devices.
    :type _scan_interval: float
    :ivar _command_queue: Queue to manage outbound HDMI-CEC commands.
    :type _command_queue: Queue
    :ivar _devices: Collection of connected HDMI devices indexed by device ID.
    :type _devices: dict[int, HDMIDevice]
    :ivar _device_status: Holds the status of connected devices indexed by ID.
    :type _device_status: dict[int, bool]
    :ivar _command_callback: Callback function invoked on receiving a new command.
    :type _command_callback: Optional[Callable[[CecCommand], None]]
    :ivar _device_added_callback: Callback invoked when a new device is added.
    :type _device_added_callback: Optional[Callable[[HDMIDevice], None]]
    :ivar _device_removed_callback: Callback invoked when a device is removed.
    :type _device_removed_callback: Optional[Callable[[HDMIDevice], None]]
    :ivar _initialized_callback: Callback executed after initialization completes.
    :type _initialized_callback: Optional[Callable[[], None]]
    ```
    """

    def __init__(self, adapter: AbstractCecAdapter, loop: AbstractEventLoop,
                 scan_interval=DEFAULT_SCAN_INTERVAL):
        self._running = False
        self._device_status = dict()
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
        self._adapter.set_on_command_callback(self.async_update)

    @property
    def initialized(self):
        return self._adapter.initialized

    async def async_init(self):
        _LOGGER.debug("initializing")  # pragma: no cover

        await self._adapter.async_init(self._initialized_callback)
        self._running = True
        _LOGGER.debug("Init done")  # pragma: no cover

    def scan(self):
        self._loop.run_until_complete(self.async_scan())

    async def async_scan(self):
        _LOGGER.info("Looking for new devices...")
        if not self.initialized:
            _LOGGER.error("Device not initialized!!!")  # pragma: no cover
            return
        for device in range(15):
            self._device_status[device] = await self._adapter.async_poll_device(device)
            if self._device_status[device] and device not in self._devices:
                self._devices[device] = HDMIDevice(device, self, loop=self._loop)
                if self._device_added_callback:
                    self._loop.call_soon_threadsafe(self._device_added_callback, self._devices[device])
                self._devices[device].task = self._loop.create_task(self._devices[device].async_run())
                _LOGGER.debug("Found device %d", device)
            elif not self._device_status[device] and device in self._devices:
                self.get_device(device).stop()
                if self._device_removed_callback:
                    self._loop.call_soon_threadsafe(self._device_removed_callback, self._devices[device])
                del (self._devices[device])

    def send_command(self, command):
        self._loop.create_task(self.async_send_command(command))

    async def async_send_command(self, command):
        if isinstance(command, str):
            command = CecCommand(command)
        _LOGGER.debug("<< %s", command)
        if command.src is None or command.src == 0xf:
            command.src = self._adapter.get_logical_address()
        await self._adapter.async_transmit(command)

    def standby(self):
        self._loop.create_task(self.async_standby())

    async def async_standby(self):
        _LOGGER.debug("Queuing system standby")  # pragma: no cover
        self._loop.call_soon_threadsafe(self._adapter.standby_devices)

    def power_on(self):
        self._loop.create_task(self.async_power_on())

    async def async_power_on(self):
        _LOGGER.debug("Queuing power on")  # pragma: no cover
        self._loop.call_soon_threadsafe(self._adapter.power_on_devices)

    def active_source(self, source: PhysicalAddress):
        self._loop.create_task(self.async_active_source(source))

    async def async_active_source(self, addr: PhysicalAddress):
        await self.async_send_command(
            CecCommand(CMD_ACTIVE_SOURCE, ADDR_BROADCAST, att=addr.asattr))
        await self.async_send_command(
            CecCommand(CMD_STREAM_PATH, ADDR_BROADCAST, att=addr.asattr))

    @property
    def devices(self) -> tuple:
        return tuple(self._devices.values())

    def get_device(self, i) -> HDMIDevice:
        return self._devices.get(i, None)

    async def async_watch(self, loop=None):
        """
        Watches asynchronously and performs scanning at regular intervals or until stopped. If the instance is not
        initialized, it waits for the initialization before starting the scanning process. The method operates within
        an event loop and maintains its operation based on the provided or internal loop object.

        :param loop: Event loop used for running asynchronous operations. If not provided, it defaults to the instance's
                     internal loop.
        :type loop: asyncio.AbstractEventLoop, optional
        :return: None
        :rtype: None
        """
        _LOGGER.debug("Start watching...")  # pragma: no cover
        if loop is None:
            loop = self._loop
        _LOGGER.debug("loop: %s", loop)
        while self._running:
            if self.initialized:
                _LOGGER.debug("Scanning...")  # pragma: no cover
                await self.async_scan()
                _LOGGER.debug("Sleep...")  # pragma: no cover
                start_time = self._loop.time()
                while (
                        self._loop.time() <= (start_time + self._scan_interval)
                        and self._running
                ):
                    await asyncio.sleep(0.3)
            else:
                _LOGGER.warning("Not initialized. Waiting for init.")
                await asyncio.sleep(1)
        _LOGGER.info("No watching anymore")

    async def async_update(self, raw_command):
        command = CecCommand(raw_command[3:])
        updated = False
        if command.src == 15:
            for i in range(15):
                updated |= await self.get_device(i).async_update(command)
                pass
        elif command.src in self._devices:
            updated = await self.get_device(command.src).async_update(command)
            pass
        if not updated:
            if self._command_callback:
                self._loop.call_soon_threadsafe(self._command_callback, command)

    async def async_shutdown(self):
        _LOGGER.debug("HDMI network shutdown.")  # pragma: no cover
        self._running = False
        for d in self._devices.values():
            d.stop()
        await self._adapter.async_shutdown()
        _LOGGER.info("HDMI network stopped.")  # pragma: no cover

    def set_command_callback(self, callback):
        self._command_callback = callback

    def set_new_device_callback(self, callback):
        self._device_added_callback = callback

    def set_device_removed_callback(self, callback):
        self._device_removed_callback = callback

    def set_initialized_callback(self, callback):
        self._initialized_callback = callback


def _to_digits(x: int):
    for x in ("%04x" % x):
        yield int(x, 16)
