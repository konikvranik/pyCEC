# -*- coding: utf-8 -*-
"""
Kodi plugin implementující CEC funkcionalitu jako služba
"""
import os
import sys
import json
import time
import xbmc
import xbmcaddon
import asyncio
from asyncio import futures
from threading import Thread

# Přidání cesty k lib adresáři pro import knihoven
addon_dir = os.path.dirname(os.path.abspath(__file__))
lib_dir = os.path.join(addon_dir, 'lib')
sys.path.insert(0, lib_dir)

# Import pycec knihovny
from pycec.commands import CecCommand, PollCommand
from pycec.const import CMD_POLL
from pycec.network import AbstractCecAdapter, HDMINetwork

# Logger pro Kodi
def log(msg, level=xbmc.LOGINFO):
    xbmc.log("[service.cec.sender] {}".format(msg), level)

# Třída implementující CEC adapter pro Kodi
class KodiCecAdapter(AbstractCecAdapter):
    def __init__(self):
        super().__init__()
        self._initialized = False
        self._command_callback = None
        self._polling = {}  # Pro ukládání polling požadavků
        
    def init(self, callback=None):
        """Inicializuje CEC adapter"""
        self._initialized = True
        if callback:
            callback()
        return asyncio.Future()
        
    def poll_device(self, device):
        """Ověří, zda zařízení existuje"""
        result = futures.Future()
        
        # Implementace pollování přes Kodi JSON-RPC API
        request = {
            "jsonrpc": "2.0",
            "method": "CEC.GetDeviceList",
            "id": 1
        }
        response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        
        if "result" in response and "devices" in response["result"]:
            devices = response["result"]["devices"]
            for dev in devices:
                if dev["logicaladdress"] == device:
                    result.set_result(True)
                    log(f"Device {device} found via Kodi CEC", xbmc.LOGDEBUG)
                    return result
        
        # Pokud nebyl nalezen v Kodi seznamu, použijeme polling přes pycec
        request = self._loop.time()
        poll_bucket = self._polling.get(device, set())
        poll_bucket.add(request)
        self._polling.update({device: poll_bucket})
        self.transmit(PollCommand(device))
        
        # Spustíme kontrolu v separátním vlákně
        def check_poll():
            start_time = time.time()
            while time.time() < (start_time + 5):  # 5 sekund timeout
                if request not in self._polling.get(device, set()):
                    result.set_result(True)
                    return
                time.sleep(0.1)
            result.set_result(False)
        
        Thread(target=check_poll).start()
        return result
        
    def get_logical_address(self):
        """Vrací logickou adresu Kodi zařízení"""
        request = {
            "jsonrpc": "2.0",
            "method": "CEC.GetActiveSource",
            "id": 1
        }
        response = json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        
        if "result" in response and "logicaladdress" in response["result"]:
            return response["result"]["logicaladdress"]
        return 1  # Výchozí hodnota pro Playback Device 1
        
    def transmit(self, command: CecCommand):
        """Odešle CEC příkaz přes Kodi CEC API"""
        log(f"Sending CEC command: {command.raw}", xbmc.LOGDEBUG)
        
        # Pro poll příkaz použijeme Kodi API
        if command.cmd == CMD_POLL:
            request = {
                "jsonrpc": "2.0",
                "method": "CEC.SendCommand",
                "params": {
                    "destination": command.dst, 
                    "command": "poll"
                },
                "id": 1
            }
            xbmc.executeJSONRPC(json.dumps(request))
            return
            
        # Pro ostatní příkazy pošleme raw command
        request = {
            "jsonrpc": "2.0",
            "method": "CEC.SendCommand",
            "params": {
                "command": command.raw
            },
            "id": 1
        }
        xbmc.executeJSONRPC(json.dumps(request))
        
    def standby_devices(self):
        """Pošle všem zařízením příkaz k uspání"""
        request = {
            "jsonrpc": "2.0",
            "method": "CEC.Standby",
            "id": 1
        }
        xbmc.executeJSONRPC(json.dumps(request))
        
    def power_on_devices(self):
        """Zapne všechna zařízení"""
        request = {
            "jsonrpc": "2.0",
            "method": "CEC.Activate",
            "id": 1
        }
        xbmc.executeJSONRPC(json.dumps(request))
        
    def set_command_callback(self, callback):
        """Nastaví callback pro přijaté CEC příkazy"""
        self._command_callback = callback
        
    def shutdown(self):
        """Ukončení adapteru"""
        self._initialized = False


class KodiCecServer(xbmc.Monitor):
    def __init__(self):
        super(KodiCecServer, self).__init__()
        self.loop = asyncio.new_event_loop()
        self.adapter = KodiCecAdapter()
        self.adapter.set_event_loop(self.loop)
        self.network = HDMINetwork(self.adapter, loop=self.loop)
        self.connections = []
        
        # Spustíme asynchronní loop v samostatném vlákně
        self.thread = Thread(target=self._run_loop)
        self.thread.daemon = True
        self.thread.start()
        
        # Inicializace a spuštění HDMINetwork
        self.network.set_command_callback(self._handle_cec_command)
        self.loop.call_soon_threadsafe(self.network.init)
        log("CEC Server initialized", xbmc.LOGINFO)

    def _run_loop(self):
        """Spouští event loop v samostatném vlákně"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    def _handle_cec_command(self, command):
        """Zpracování přijatých CEC příkazů"""
        log(f"Received CEC command: {command}", xbmc.LOGINFO)
        # Zde bychom mohli implementovat další zpracování příkazů
        
    def onNotification(self, sender, method, data):
        """Zpracování Kodi notifikací"""
        if method == "System.OnQuit":
            self.shutdown()
            
    def shutdown(self):
        """Ukončí server a uvolní prostředky"""
        log("Shutting down CEC Server", xbmc.LOGINFO)
        self.network.stop()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=1.0)


# Hlavní spouštěcí bod
if __name__ == "__main__":
    addon = xbmcaddon.Addon()
    log(f"Starting {addon.getAddonInfo('name')} version {addon.getAddonInfo('version')}", xbmc.LOGINFO)
    
    server = KodiCecServer()
    
    # Hlavní smyčka čekání na ukončení
    while not server.abortRequested():
        if server.waitForAbort(1):
            break
            
    # Ukončení služby
    server.shutdown()
    log("CEC Server stopped", xbmc.LOGINFO)