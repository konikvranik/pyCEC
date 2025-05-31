# ... vše předtím zůstává stejné až po třídu CecServerService ...
import asyncio
import os
import sys
import threading
from asyncio import AbstractEventLoop, run_coroutine_threadsafe, Server

import xbmc
import xbmcaddon
import xbmcvfs
from xbmc import log

from pycec.commands import CecCommand, KeyPressCommand
from pycec.const import ADDR_RECORDINGDEVICE1
from pycec.network import AbstractCecAdapter
from pycec.server import CECServer

# Získání instance addonu a cest
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))

# Přidání cest k potřebným knihovnám
LIB_DIR = os.path.join(ADDON_PATH, "lib")
RESOURCES_LIB_DIR = os.path.join(ADDON_PATH, "resources", "lib")

# Přidání cest do systémové cesty pro import
sys.path.insert(0, LIB_DIR)
sys.path.insert(0, RESOURCES_LIB_DIR)


# Logger pro Kodi
def log(msg, level=xbmc.LOGINFO):
    xbmc.log("[{}] {}".format(ADDON_ID, msg), level)


class KodiAdapter(AbstractCecAdapter):
    def __init__(
        self,
        name: str = None,
        monitor_only: bool = None,
        activate_source: bool = None,
        device_type=ADDR_RECORDINGDEVICE1,
    ):
        super().__init__()

    def set_on_command_callback(self, callback):
        self._cecconfig.SetKeyPressCallback(lambda key, delay: callback(KeyPressCommand(key).raw))
        self._cecconfig.SetCommandCallback(callback)

    async def async_standby_devices(self):
        asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.StandbyDevices)

    async def async_poll_device(self, device):
        return asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.PollDevice, device)

    async def async_shutdown(self):
        self._io_executor.shutdown()
        if self._adapter:
            self._adapter.Close()

    def get_logical_address(self):
        return self._adapter.GetLogicalAddresses().primary

    async def async_power_on_devices(self):
        await asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.PowerOnDevices)

    async def async_transmit(self, command: CecCommand):
        asyncio.get_running_loop().run_in_executor(self._io_executor, self._adapter.Transmit, self._adapter.CommandFromString(command.raw))

    async def async_init(self, callback: callable = None):
        return asyncio.get_running_loop().run_in_executor(self._io_executor, self._init, callback)

    def _init(self, callback: callable = None):
        log("Initializing CEC...")
        log("Created adapter")
        if callback:
            callback()


class CecServerService(xbmc.Monitor):
    """
    Služba Kodi pro spuštění TCP serveru s CEC funkcionalitou
    """

    def __init__(self):
        super().__init__()
        self.loop: AbstractEventLoop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.server: Server = None
        self.loop_thread.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        run_coroutine_threadsafe(self._start_server(), self.loop)

    async def _start_server(self):
        _srv = CECServer(KodiAdapter("CEC server"))
        self.server = await _srv.async_start(ADDON.getSettingString("interface"), ADDON.getSettingInt("port"))
        log("CEC server started")

    async def _stop_server(self):
        if self.server:
            log("Shutting down CEC TCP Server")
            self.server.close()
            await self.server.wait_closed()
            self.server = None

    def onSettingsChanged(self):  # noqa: N802
        log("Settings changed, restarting server")
        run_coroutine_threadsafe(self._restart_server(), self.loop)

    async def _restart_server(self):
        await self._stop_server()
        await self._start_server()

    def shutdown(self):
        if self.server:
            run_coroutine_threadsafe(self._stop_server(), self.loop).result(timeout=5)
        log("Stopping asyncio loop")
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.loop_thread.join()
