from typing import List


def _to_digits(x: int) -> List[int]:
    for x in ("%04x" % x):
        yield int(x, 16)


class PhysicalAddress:
    def __init__(self, address):
        self._physical_address = int()
        if isinstance(address, (str,)):
            address = int(address.replace('.', '').replace(':', ''), 16)
        if isinstance(address, (tuple, list,)):
            if len(address) == 2:
                self._physical_address = int("%02x%02x" % tuple(address), 16)
            elif len(address) == 4:
                self._physical_address = int("%x%x%x%x" % tuple(address), 16)
            else:
                raise AttributeError("Incorrect count of members in list!")
        elif isinstance(address, (int,)):
            self._physical_address = address

    @property
    def asattr(self) -> List[int]:
        return [self._physical_address // 0x100,
                self._physical_address % 0x100]

    @property
    def asint(self) -> int:
        return self._physical_address

    @property
    def ascmd(self) -> str:
        return "%x%x:%x%x" % tuple(
            x for x in _to_digits(self._physical_address))

    @property
    def asstr(self) -> str:
        return ".".join(("%x" % x) for x in _to_digits(self._physical_address))

    def __str__(self):
        return self.asstr
