import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from pycec.commands import CecCommand, KeyPressCommand
from pycec.const import VENDORS, ADDR_RECORDINGDEVICE1
from pycec.network import AbstractCecAdapter

_LOGGER = logging.getLogger(__name__)


# pragma: no cover
class CecAdapter(AbstractCecAdapter):
    def __init__(self, name: str = None, monitor_only: bool = None, activate_source: bool = None, device_type=ADDR_RECORDINGDEVICE1):
        super().__init__()
        self._adapter = None
        self._io_executor = ThreadPoolExecutor(1)
        import cec

        self._cecconfig = cec.libcec_configuration()
        if monitor_only is not None:
            self._cecconfig.bMonitorOnly = 1 if monitor_only else 0
        self._cecconfig.strDeviceName = name[:13]
        if activate_source is not None:
            self._cecconfig.bActivateSource = 1 if activate_source else 0
        self._cecconfig.deviceTypes.Add(device_type)

    def set_on_command_callback(self, callback):
        self._cecconfig.SetKeyPressCallback(lambda key, delay: callback(KeyPressCommand(key).raw))
        self._cecconfig.SetCommandCallback(callback)

    async def async_standby_devices(self):
        await asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.StandbyDevices)

    async def async_poll_device(self, device):
        return await asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.PollDevice, device)

    async def async_shutdown(self):
        self._io_executor.shutdown()
        if self._adapter:
            await asyncio.get_running_loop().run_in_executor(None, self._adapter.Close)

    def get_logical_address(self):
        return self._adapter.GetLogicalAddresses().primary

    async def async_power_on_devices(self):
        await asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.PowerOnDevices)

    async def async_transmit(self, command: CecCommand):
        await asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.Transmit, self._adapter.CommandFromString(command.raw))

    async def async_init(self, callback: callable = None):
        import cec

        if not self._cecconfig.clientVersion:
            self._cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        _LOGGER.debug("Initializing CEC...")
        adapter = await asyncio.get_running_loop().run_in_executor(self._io_executor, cec.ICECAdapter.Create, self._cecconfig)
        _LOGGER.debug("Created adapter")
        a = None
        adapters = await asyncio.get_running_loop().run_in_executor(self._io_executor, adapter.DetectAdapters)
        for a in adapters:
            _LOGGER.info("found a CEC adapter:")
            _LOGGER.info("port:     " + a.strComName)
            _LOGGER.info("vendor:   " + (VENDORS[a.iVendorId] if a.iVendorId in VENDORS else hex(a.iVendorId)))
            _LOGGER.info("product:  " + hex(a.iProductId))
            a = a.strComName
        if a is None:
            _LOGGER.warning("No adapters found")
        else:
            if await asyncio.get_running_loop().run_in_executor(self._io_executor, adapter.Open, a):
                _LOGGER.info("connection opened")
                self._adapter = adapter
                self._initialized = True
            else:
                _LOGGER.error("failed to open a connection to the CEC adapter")
        if callback:
            callback()
