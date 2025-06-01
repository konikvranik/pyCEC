# ... vše předtím zůstává stejné až po třídu CecServerService ...
import asyncio
import os
import sys
from asyncio import run_coroutine_threadsafe, Server

import xbmc
import xbmcaddon
import xbmcvfs

from pycec import server as cec_server
from pycec.commands import CecCommand
from pycec.const import ADDR_RECORDINGDEVICE1
from pycec.network import AbstractCecAdapter
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


class CecServerService(xbmc.Monitor, cec_server.CECServer):

    def __init__(self):
        log("Initializing CEC TCP Server service...")
        super().__init__()
        self.server: Server = None
        log("CEC TCP Server service initialized")

    async def async_serve(self):
        asyncio.run_coroutine_threadsafe(self._watch_for_abort())
        await self._start_server()
        async with self.server:
            await self.server.serve_forever()

        self.server.close()
        await self.server.wait_closed()

    async def _start_server(self):
        _srv = cec_server.CECServer(KodiAdapter("CEC server"))
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

    async def _watch_for_abort(self):
        while not service.abortRequested():
            await asyncio.sleep(1)
        self.server.close()
        await self.server.wait_closed()


log(f"Starting {ADDON.getAddonInfo('name')} version {ADDON.getAddonInfo('version')}")

service = CecServerService()
asyncio.run(service.async_serve())

log("CEC TCP Server stopped")
