"""pyCEC"""
import logging

import cec

_LOGGER = logging.getLogger(__name__)


class CecConfig(cec.libcec_configuration):
    def __init__(self, name: str = None, monitor_only: bool = False, activate_source: bool = False,
                 device_type=cec.CEC_DEVICE_TYPE_RECORDING_DEVICE):
        super().__init__()
        self.bMonitorOnly = 1 if monitor_only else 0
        self.strDeviceName = name
        self.bActivateSource = 1 if activate_source else 0
        self.deviceTypes.Add(device_type)
