import asyncio
import logging

from . import _LOGGER
from .network import HDMINetwork, CecConfig

if __name__ == '__main__':

    _LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)

    _LOGGER.info("Starting network...")
    network = HDMINetwork(CecConfig("pyCEC"))

    network.start()


    @asyncio.coroutine
    def async_print():
        while True:
            for d in network.devices:
                _LOGGER.info("%s", str(d))
                yield from asyncio.sleep(5)


    loop = asyncio.get_event_loop()
    loop.create_task(async_print())
    loop.run_forever()
