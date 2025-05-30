# -*- coding: utf-8 -*-
"""
Hlavní vstupní bod CEC TCP serveru
"""
import os
import sys

import xbmc
import xbmcaddon
import xbmcvfs

from pycec.commands import KeyPressCommand, CecCommand
from pycec.const import ADDR_RECORDINGDEVICE1
from pycec.network import AbstractCecAdapter
from pycec.server import CECServer

# Získání instance addonu a cest
ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo('path'))

# Přidání cest k potřebným knihovnám
LIB_DIR = os.path.join(ADDON_PATH, 'lib')
RESOURCES_LIB_DIR = os.path.join(ADDON_PATH, 'resources', 'lib')

# Přidání cest do systémové cesty pro import
sys.path.insert(0, LIB_DIR)
sys.path.insert(0, RESOURCES_LIB_DIR)


# Logger pro Kodi
def log(msg, level=xbmc.LOGINFO):
    xbmc.log("[{}] {}".format(ADDON_ID, msg), level)


class KodiAdapter(AbstractCecAdapter):
    def __init__(self, name: str = None, monitor_only: bool = None, activate_source: bool = None,
                 device_type=ADDR_RECORDINGDEVICE1):
        super().__init__()

    def set_on_command_callback(self, callback):
        self._cecconfig.SetKeyPressCallback(
            lambda key, delay: callback(KeyPressCommand(key).raw))
        self._cecconfig.SetCommandCallback(callback)

    async def async_standby_devices(self):
        self._loop.run_in_executor(self._io_executor,
                                   self._adapter.StandbyDevices)

    def async_poll_device(self, device):
        return self._loop.run_in_executor(
            self._io_executor, self._adapter.PollDevice, device)

    async def async_shutdown(self):
        self._io_executor.shutdown()
        if self._adapter:
            self._adapter.Close()

    def get_logical_address(self):
        return self._adapter.GetLogicalAddresses().primary

    async def async_power_on_devices(self):
        await self._loop.run_in_executor(self._io_executor, self._adapter.PowerOnDevices)

    async def async_transmit(self, command: CecCommand):
        self._loop.run_in_executor(self._io_executor, self._adapter.Transmit,
                                   self._adapter.CommandFromString(command.raw))

    async def async_init(self, callback: callable = None):
        return self._loop.run_in_executor(self._io_executor, self._init, callback)

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
        super(CecServerService, self).__init__()
        self.server = None

    def start(self):
        """Spustí TCP server"""
        # Získání nastavení
        host = ADDON.getSetting('host') or '0.0.0.0'
        port = int(ADDON.getSetting('port') or 9998)

        log(f"Starting CEC TCP Server on {host}:{port}")

        try:
            self.server = CECServer()
            self.server.start(host, port)
            log("CEC TCP Server started successfully")
        except Exception as e:
            log(f"Failed to start CEC TCP Server: {str(e)}", xbmc.LOGERROR)

    def onSettingsChanged(self): #noqa: N802
        """Reaguje na změnu nastavení"""
        log("Settings changed, restarting server")
        if self.server:
            self.server.stop()
        self.start()

    def shutdown(self):
        """Ukončí server"""
        if self.server:
            log("Shutting down CEC TCP Server")
            self.server.stop()


# Hlavní funkce addonu
if __name__ == '__main__':
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
