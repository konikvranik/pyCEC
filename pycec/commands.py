from typing import List

from pycec.const import CMD_KEY_PRESS, CMD_KEY_RELEASE


class CecCommand:
    def __init__(self, cmd, dst: int = None, src: int = None,
                 att: List[int] = None, raw: str = None):

        self._src = src
        self._dst = dst
        self._cmd = cmd
        self._att = att

        if raw is not None:
            self._raw(raw)
        elif isinstance(cmd, (str,)):
            self._raw(cmd)
        else:
            self.src = src
            self.dst = dst
            self._cmd = cmd
            self._att = att

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

    @property
    def att(self) -> List[int]:
        return self._att if self._att else []

    def _att(self, value: List[int]):
        self._att = value

    @property
    def raw(self) -> str:
        atts = "".join(((":%02x" % i) for i in self.att))
        return "%1x%1x:%02x%s" % (
            self.src if self.src is not None else 0xf, self.dst if self.dst is not None else 0xf, self.cmd, atts)

    def _raw(self, value: str):
        atts = value.split(':')
        self.src = int(atts[0][0], 16)
        self.dst = int(atts[0][1], 16)
        self._cmd = int(atts[1], 16)
        self._att = list(int(x, 16) for x in atts[2:])

    def __str__(self):
        return self.raw


class KeyPressCommand(CecCommand):
    def __init__(self, key, dst: int = None, src: int = None):
        super().__init__(CMD_KEY_PRESS, dst, src, [key])
        self._key = key

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, key):
        self._key = key


class KeyReleaseCommand(CecCommand):
    def __init__(self, dst: int = None, src: int = None):
        super().__init__(CMD_KEY_RELEASE, dst, src)
