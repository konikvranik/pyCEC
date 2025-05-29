# -*- coding: utf-8 -*-
"""
Hlavní vstupní bod CEC TCP serveru
"""
import asyncio
import os
import sys
import xbmc
import xbmcaddon
import xbmcvfs

from pycec.server import CECServerProtocol, CECServer
from pycec.cec import CecAdapter
from pycec.network import HDMINetwork, AbstractCecAdapter

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
    def __init__(self, name: str = None, monitor_only: bool = None,
                 activate_source: bool = None,
                 device_type=ADDR_RECORDINGDEVICE1):
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

    def set_command_callback(self, callback):
        self._cecconfig.SetKeyPressCallback(
            lambda key, delay: callback(KeyPressCommand(key).raw))
        self._cecconfig.SetCommandCallback(callback)

    def standby_devices(self):
        self._loop.run_in_executor(self._io_executor,
                                   self._adapter.StandbyDevices)

    def poll_device(self, device):
        return self._loop.run_in_executor(
            self._io_executor, self._adapter.PollDevice, device)

    def shutdown(self):
        self._io_executor.shutdown()
        if self._adapter:
            self._adapter.Close()

    def get_logical_address(self):
        return self._adapter.GetLogicalAddresses().primary

    def power_on_devices(self):
        self._loop.run_in_executor(self._io_executor,
                                   self._adapter.PowerOnDevices)

    def transmit(self, command: CecCommand):
        self._loop.run_in_executor(
            self._io_executor, self._adapter.Transmit,
            self._adapter.CommandFromString(command.raw))

    def init(self, callback: callable = None):
        return self._loop.run_in_executor(self._io_executor, self._init,
                                          callback)

    def _init(self, callback: callable = None):
        import cec
        if not self._cecconfig.clientVersion:
            self._cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        _LOGGER.debug("Initializing CEC...")
        adapter = cec.ICECAdapter.Create(self._cecconfig)
        _LOGGER.debug("Created adapter")
        a = None
        adapters = adapter.DetectAdapters()
        for a in adapters:
            _LOGGER.info("found a CEC adapter:")
            _LOGGER.info("port:     " + a.strComName)
            _LOGGER.info("vendor:   " + (
                VENDORS[a.iVendorId] if a.iVendorId in VENDORS else hex(
                    a.iVendorId)))
            _LOGGER.info("product:  " + hex(a.iProductId))
            a = a.strComName
        if a is None:
            _LOGGER.warning("No adapters found")
        else:
            if adapter.Open(a):
                _LOGGER.info("connection opened")
                self._adapter = adapter
                self._initialized = True
            else:
                _LOGGER.error("failed to open a connection to the CEC adapter")
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

    def onSettingsChanged(self):
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
