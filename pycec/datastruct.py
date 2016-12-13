from typing import List


class CecCommand:
    def __init__(self, cmd=None, dst: int = None, src: int = None,
                 att: List[int] = None, raw: str = None):

        self._src = int()
        self._dst = int()
        self._cmd = int()
        self._att = list()

        if isinstance(cmd, (str,)):
            self.raw = cmd
        else:
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
        return self._att if self._att else []

    @att.setter
    def att(self, value: List[int]):
        self._att = value

    @property
    def raw(self) -> str:
        atts = "".join(((":%02x" % i) for i in self.att))
        return "%1x%1x:%02x%s" % (self.src, self.dst, self.cmd, atts)

    @raw.setter
    def raw(self, value: str):
        atts = value.split(':')
        self.src = int(atts[0][0], 16)
        self.dst = int(atts[0][1], 16)
        self.cmd = int(atts[1], 16)
        self.att = list(int(x, 16) for x in atts[2:])

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
            address = list(int(x, 16) for x in address.split(':'))
        if isinstance(address, (tuple, list,)):
            self._physical_address = address[0] * 0x100 + address[1]
        elif isinstance(address, (int,)):
            self._physical_address = address

    @property
    def aslist(self) -> List[int]:
        return list(
            reversed(list(x for x in _to_digits(self._physical_address))))

    @property
    def asint(self) -> int:
        return self._physical_address

    @property
    def ascmd(self) -> str:
        return "%x%x:%x%x" % tuple(
            reversed([x for x in _to_digits(self._physical_address)]))

    def __str__(self):
        return ".".join(
            reversed([("%x" % x) for x in _to_digits(self._physical_address)]))
