import asyncio
from asyncio import Transport, Server
from typing import Coroutine, Any

from pycec import _LOGGER
from pycec.commands import CecCommand, PollCommand
from pycec.network import HDMINetwork


class CECServerProtocol(asyncio.Protocol):
    buffer = ""

    def __init__(self, network: HDMINetwork, connections):
        self._hdmi_network = network
        self._connections = connections
        self._transport: Transport = None
        super().__init__()

    def connection_made(self, transport):
        _LOGGER.info("Connection opened by %s", transport.get_extra_info("peername"))
        self._transport = transport
        self._connections.add(self)

    def data_received(self, data):
        self.buffer += bytes.decode(data)
        for line in self.buffer.splitlines(keepends=True):
            if line.endswith("\r") or line.endswith("\n"):
                line = line.rstrip()
                if len(line) == 2:
                    _LOGGER.info("Received poll %s from %s", line, self._transport.get_extra_info("peername"))
                    device = CecCommand(line).dst
                    asyncio.create_task(self.async_send_command(device, line))
            else:
                self.buffer = line

    async def async_send_command(self, device, line):
        r = await self._hdmi_network._adapter.async_poll_device(device)
        if r:
            asyncio.get_running_loop().run_in_executor(
                None, self.send_command_to_tcp, PollCommand(self._hdmi_network._adapter.get_logical_address(), src=device)
            )
        else:
            _LOGGER.info("Received command %s from %s", line, self._transport.get_extra_info("peername"))
            self._hdmi_network.send_command(CecCommand(line))
        self.buffer = ""

    def connection_lost(self, exc):
        _LOGGER.info("Connection with %s lost", self._transport.get_extra_info("peername"))
        self._connections.remove(self)

    def _after_poll(self, d, f):
        if f.result():
            self.send_command_to_tcp(PollCommand(self._hdmi_network._adapter.get_logical_address(), src=d))

    def send_command_to_tcp(self, command):
        _LOGGER.info("Sending %s to %s", command, self._transport.get_extra_info("peername"))
        self._transport.write(str.encode("%s\r\n" % command.raw))


class CECServer:
    def __init__(self, adapter):
        self._adapter = adapter
        self._network = HDMINetwork(self._adapter)
        self._connections = set()
        self._server: Coroutine[Any, Any, Server] = None

    async def async_start(self, host, port) -> Server:
        _LOGGER.info("CEC initialized... Starting server.")

        # Each client connection will create a new protocol instance

        def _send_command_to_tcp(command):
            for c in self._connections:
                c.send_command_to_tcp(command)

        self._network.set_command_callback(_send_command_to_tcp)
        if not await self._network.async_init():
            raise Exception("Failed to initialize CEC network.")

        self._server = await asyncio.get_running_loop().create_server(lambda: CECServerProtocol(self._network, self._connections), host, port)

        # Serve requests until Ctrl+C is pressed
        _LOGGER.info("Serving on {}".format(self._server.sockets[0].getsockname()))
        return self._server
