import logging
from typing import List

from pycec.datastruct import CMD_PHYSICAL_ADDRESS, PhysicalAddress, CMD_POWER_STATUS, CMD_VENDOR, CMD_OSD_NAME, \
    CecCommand

_LOGGER = logging.getLogger(__name__)


class HdmiDevice:
    def __init__(self, logical_address: int):
        self._logical_address = logical_address
        self._physical_address = int()
        self._power_status = int()
        self._audio_status = int()
        self._is_active_source = bool()
        self._vendor_id = int()
        self._menu_language = str()
        self._osd_name = str()
        self._audio_mode_status = int()
        self._deck_status = int()
        self._tuner_status = int()
        self._menu_status = int()
        self._record_status = int()
        self._timer_cleared_status = int()
        self._timer_status = int()

    @property
    def logical_address(self) -> int:
        return self._logical_address

    @logical_address.setter
    def logical_address(self, value: int):
        self._logical_address = value

    def update(self, command: CecCommand):
        if command.cmd == CMD_PHYSICAL_ADDRESS[1]:
            self._physical_address = PhysicalAddress(
                (command.att[0], command.att[0]))
        elif command.cmd == CMD_POWER_STATUS[1]:
            pass
        elif command.cmd == CMD_VENDOR[1]:
            pass
        elif command.cmd == CMD_OSD_NAME[1]:
            pass


class HdmiNetwork:
    def __init__(self, adapter):
        pass

    def scan(self):
        pass

    @property
    def devices(self) -> List[HdmiDevice]:
        pass


class CecClient:
    def __init__(self):
        """initialize libCEC"""
        cecconfig = None  # cec.libcec_configuration()
        cecconfig.strDeviceName = "HA"
        cecconfig.bActivateSource = 0
        cecconfig.bMonitorOnly = 0
        # cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
        # cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT
        cecconfig.strDeviceLanguage = "cze"
        cecconfig.SetKeyPressCallback(self.cec_key_press_callback)
        cecconfig.SetCommandCallback(self.cec_command_callback)

        lib_cec = None  # cec.ICECAdapter.Create(cecconfig)

        # print libCEC version and compilation information
        _LOGGER.info("libCEC version " + lib_cec.VersionToString(
            cecconfig.serverVersion) + " loaded: " + lib_cec.GetLibInfo())

        # search for adapters
        adapter = None
        adapters = lib_cec.DetectAdapters()
        for adapter in adapters:
            _LOGGER.info("found a CEC adapter:")
            _LOGGER.info("port:     " + adapter.strComName)
            _LOGGER.info("vendor:   " + hex(adapter.iVendorId))
            _LOGGER.info("product:  " + hex(adapter.iProductId))
            adapter = adapter.strComName
        if adapter is None:
            _LOGGER.warning("No adapters found")
            return None
        else:
            if lib_cec.Open(adapter):
                lib_cec.GetCurrentConfiguration(cecconfig)
                _LOGGER.info("connection opened")
                return lib_cec
            else:
                _LOGGER.error("failed to open a connection to the CEC adapter")
                return None

    def cec_key_press_callback(self, key, duration):
        """key press callback"""
        _LOGGER.info("[key pressed] " + str(key))
        return 0

    def cec_command_callback(self, command):
        """command received callback"""
        return 0


if __name__ == '__main__':
    print("pa int: %s" % PhysicalAddress(0x12cd))
    print("pa str: %s" % PhysicalAddress("12:cd"))
    print("pa tuple: %s" % PhysicalAddress((0x12, 0xcd)))
    print("pa list: %s" % PhysicalAddress([0x12, 0xcd]))

    print("cmd num: %s" % CecCommand(0x1, 0x2, 0x8f, [0x01, 0xab]))
    print("cmd str: %s" % CecCommand(raw="12:8f:01:ab"))
