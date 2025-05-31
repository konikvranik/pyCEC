# ... vše předtím zůstává stejné až po třídu CecServerService ...
import asyncio
import os
import sys
import threading
from asyncio import AbstractEventLoop, run_coroutine_threadsafe, Server

import xbmc
import xbmcaddon
import xbmcvfs

from pycec.commands import CecCommand
from pycec.const import ADDR_RECORDINGDEVICE1
from pycec.network import AbstractCecAdapter
from pycec.server import CECServer
from pycec.tcp import DEFAULT_PORT

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))

LIB_DIR = os.path.join(ADDON_PATH, "lib")
RESOURCES_LIB_DIR = os.path.join(ADDON_PATH, "resources", "lib")

sys.path.insert(0, LIB_DIR)
sys.path.insert(0, RESOURCES_LIB_DIR)


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
        pass

    async def async_standby_devices(self):
        pass

    async def async_poll_device(self, device):
        pass

    async def async_shutdown(self):
        pass

    def get_logical_address(self):
        pass

    async def async_power_on_devices(self):
        pass

    async def async_transmit(self, command: CecCommand):
        pass

    async def async_init(self, callback: callable = None):
        pass

    def _init(self, callback: callable = None):
        log("Initializing CEC...")
        log("Created adapter")
        if callback:
            callback()


class CecServerService(xbmc.Monitor):

    def __init__(self):
        log("Initializing CEC TCP Server service...")
        super().__init__()
        self.loop: AbstractEventLoop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.server: Server = None
        self.loop_thread.start()
        log("CEC TCP Server service initialized")

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        log("Starting CEC TCP Server")
        future = run_coroutine_threadsafe(self._start_server(), self.loop)

        def handle_result(fut):
            try:
                fut.result()
            except Exception as e:
                log(f"Error starting CEC TCP server: {e}", xbmc.LOGERROR)

        future.add_done_callback(handle_result)
        log("CEC TCP Server started (async task submitted)")

    async def _start_server(self):
        _srv = CECServer(KodiAdapter("CEC server"))
        interface = ADDON.getSettingString("interface")
        port = ADDON.getSettingInt("port")
        port = port if port else DEFAULT_PORT
        self.server = await _srv.async_start(interface, port)
        log("CEC server started on %s:%s" % (interface, port))

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


log(f"Starting {ADDON.getAddonInfo('name')} version {ADDON.getAddonInfo('version')}")

# Vytvoření a spuštění služby
service = CecServerService()
service.start()

# Hlavní smyčka - běží dokud není Kodi ukončeno
while not service.abortRequested():
    if service.waitForAbort(1):
        break

# Ukončení služby
service.shutdown()
log("CEC TCP Server stopped")
