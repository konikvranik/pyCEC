"""pyCEC"""
import logging

from pycec.const import TYPE_RECORDER_1

_LOGGER = logging.getLogger(__name__)


class CecConfig:
    def __init__(self, name: str = None, monitor_only: bool = False,
                 activate_source: bool = False,
                 device_type=TYPE_RECORDER_1):
        import cec
        self._command_callback = None
        self._cecconfig = cec.libcec_configuration()
        self._cecconfig.bMonitorOnly = 1 if monitor_only else 0
        self._cecconfig.strDeviceName = name
        self._cecconfig.bActivateSource = 1 if activate_source else 0
        self._cecconfig.deviceTypes.Add(device_type)

    @property
    def cecconfig(self):
        return self._cecconfig

    def SetCommandCallback(self, callback):
        self._cecconfig.SetCommandCallback(callback)
