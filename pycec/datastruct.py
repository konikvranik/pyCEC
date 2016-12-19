from typing import List

from functools import reduce


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
            self._physical_address = reduce(lambda x, y: x * 0x100 + y, address)
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
