import asyncio
import logging

from pycec.commands import CecCommand
from . import _LOGGER
from .network import HDMINetwork, CecConfig


def main():
    transports = set()
    loop = asyncio.get_event_loop()
    network = HDMINetwork(CecConfig("pyCEC"), loop=loop)

    class CECServerProtocol(asyncio.Protocol):
        transport = None

        def connection_made(self, transport):
            _LOGGER.info("Connection opened by %s",
                         transport.get_extra_info('peername'))
            self.transport = transport
            transports.add(transport)

        def data_received(self, data):
            _LOGGER.info("Received %s from %s", data,
                         self.transport.get_extra_info('peername'))
            network.send_command(CecCommand(bytes.decode(data).rstrip()))

        def connection_lost(self, exc):
            _LOGGER.warn("Connection with %s lost",
                         self.transport.get_extra_info('peername'))
            transports.remove(self.transport)

    def _send_command_to_tcp(command):
        for t in transports:
            _LOGGER.info("Sending %s to %s", command,
                         t.get_extra_info('peername'))
            t.write(str.encode("%s\n" % command.raw))

    network.set_command_callback(_send_command_to_tcp)
    loop.run_until_complete(network.async_init())

    _LOGGER.info("CEC initialized... Starting server.")
    # Each client connection will create a new protocol instance
    coro = loop.create_server(CECServerProtocol, '127.0.0.1', 9526)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


def init_logger():
    _LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)


init_logger()

if __name__ == '__main__':
    main()
