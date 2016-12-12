import logging

# import cec
from typing import List

_LOGGER = logging.getLogger(__name__)


class CecCommand:
    def __init__(self, src: int() = None, dst: int() = None, cmd: int() = None,
                 att: list([int()]) = None, raw: str() = None):
        self._src = int()
        self._dst = int()
        self._cmd = int()
        self._att = list([int])

        self.src = src or None
        self.dst = dst or None
        self.cmd = cmd or None
        self.att = att or None
        if raw is not None:
            self.raw = raw

    @property
    def src(self) -> int:
        return self._src

    @src.setter
    def src(self, value: int):
        self._src = value

    @property
    def dst(self) -> int:
        return self._dst

    @dst.setter
    def dst(self, value: int):
        self._dst = value

    @property
    def cmd(self) -> int:
        return self._cmd

    @cmd.setter
    def cmd(self, value: int):
        self._cmd = value

    @property
    def att(self) -> List[int]:
        return self._att

    @att.setter
    def att(self, value: List[int]):
        self._att = value

    @property
    def raw(self) -> str:
        return "%1x%1x:%02x%s" % (
            self.src, self.dst, self.cmd,
            "".join(((":%02x" % i) for i in self.att)))

    @raw.setter
    def raw(self, value: str):
        atts = value.split(':')
        self.src = int(atts[0][0], 16)
        self.dst = int(atts[0][1], 16)
        self.cmd = int(atts[1], 16)
        self.att = [int(x, 16) for x in atts[2:]]

    def __str__(self):
        return self.raw


CMD_PHYSICAL_ADDRESS = (0x83, 0x84)
CMD_POWER_STATUS = (0x8f, 0x90)
CMD_AUDIO_STATUS = (0x71, 0x7a)
CMD_VENDOR = (0x8c, 0x87)
CMD_MENU_LANGUAGE = (0x91, 0x32)
CMD_OSD_NAME = (0x46, 0x47)
CMD_AUDIO_MODE_STATUS = (0x7d, 0x7e)
CMD_DECK_STATUS = (0x1a, 0x1b)
CMD_TUNER_STATUS = (0x07, 0x08)
CMD_MENU_STATUS = (0x8d, 0x8e)


def _to_digits(x: int) -> List[int]:
    while x > 0:
        yield x % 0x10
        x //= 0x10
    return x


class PhysicalAddress:
    def __init__(self, address):
        self._physical_address = int()
        if isinstance(address, (str,)):
            address = [int(x, 16) for x in address.split(':')]
        if isinstance(address, (tuple, list,)):
            self._physical_address = address[0] * 0x100 + address[1]
        elif isinstance(address, (int,)):
            self._physical_address = address

    def __str__(self):
        return ".".join(
            reversed([("%x" % x) for x in _to_digits(self._physical_address)]))


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
