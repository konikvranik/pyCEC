import asyncio
import functools
from asyncio import Transport, futures, Server

from pycec import _LOGGER
from pycec.commands import CecCommand, PollCommand
from pycec.network import HDMINetwork


class CECServerProtocol(asyncio.Protocol):
    buffer = ''

    def __init__(self, network: HDMINetwork, connections):
        self._hdmi_network = network
        self._connections = connections
        self._transport: Transport = None
        super().__init__()

    def connection_made(self, transport):
        _LOGGER.info("Connection opened by %s", transport.get_extra_info('peername'))
        self._transport = transport
        self._connections.add(self)

    def data_received(self, data):
        self.buffer += bytes.decode(data)
        for line in self.buffer.splitlines(keepends=True):
            if line.endswith('\r') or line.endswith('\n'):
                line = line.rstrip()
                if len(line) == 2:
                    _LOGGER.info("Received poll %s from %s", line, self._transport.get_extra_info('peername'))
                    device = CecCommand(line).dst
                    t: futures.Future = self._hdmi_network._adapter.async_poll_device(device)
                    t.add_done_callback(functools.partial(self._after_poll, device))
                else:
                    _LOGGER.info("Received command %s from %s", line, self._transport.get_extra_info('peername'))
                    self._hdmi_network.send_command(CecCommand(line))
                self.buffer = ''
            else:
                self.buffer = line

    def connection_lost(self, exc):
        _LOGGER.info("Connection with %s lost", self._transport.get_extra_info('peername'))
        self._connections.remove(self)

    def _after_poll(self, d, f):
        if f.result():
            self.send_command_to_tcp(PollCommand(self._hdmi_network._adapter.get_logical_address(), src=d))

    def send_command_to_tcp(self, command):
        _LOGGER.info("Sending %s to %s", command, self._transport.get_extra_info('peername'))
        self._transport.write(str.encode("%s\r\n" % command.raw))


class CECServer:
    def __init__(self, adapter, loop=asyncio.get_event_loop()):
        self._loop = loop
        self._adapter = adapter
        self._network = HDMINetwork(self._adapter, self._loop)
        self._connections = set()
        self._server: Server = None

    def start(self, host, port):
        _LOGGER.info("CEC initialized... Starting server.")

        # Each client connection will create a new protocol instance

        def _send_command_to_tcp(command):
            for c in self._connections:
                c.send_command_to_tcp(command)

        self._network.set_command_callback(_send_command_to_tcp)
        self._loop.run_until_complete(self._network.async_init())

        self._server = self._loop.create_server(lambda: CECServerProtocol(self._network, self._connections), host, port)

        # Serve requests until Ctrl+C is pressed
        _LOGGER.info('Serving on {}'.format(self._server.sockets[0].getsockname()))
        return self._server

    def stop(self):
        # Close the server
        self._server.close()
        self._loop.run_until_complete(self._server.wait_closed())
