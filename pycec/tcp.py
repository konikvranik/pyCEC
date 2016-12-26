import asyncio

from pycec.commands import CecCommand
from pycec.network import AbstractCecAdapter

DEFAULT_PORT = 9526


class TcpProtocol(asyncio.Protocol):
    def __init__(self, adapter: TcpAdapter):
        self._adapter = adapter

    def connection_made(self, transport):
        self.transport = transport
        self._adapter.set_transport = transport

    def data_received(self, data:bytes):
        self._adapter._command_callback(CecCommand(data.decode().rstrip()))

    def eof_received(self):
        self._adapter.shutdown()

    def connection_lost(self, exc):
        self._adapter.shutdown()


class TcpAdapter(AbstractCecAdapter):
    def __init__(self, host, port=DEFAULT_PORT, loop=asyncio.new_event_loop()):
        super().__init__()
        self._command_callback = None
        self._loop = loop
        self._host = host
        self._port = port
        self._client = None
        self._transport = None

    def init(self, callback: callable = None):
        self._client = self._loop.create_connection(
            lambda: TcpProtocol(self),
            host=self._host,
            port=self._port)
        self._initialized = True

    def shutdown(self):
        self._transport.close()

    def PollDevice(self, device):
        pass

    def GetLogicalAddresses(self):
        pass

    def StandbyDevices(self):
        pass

    def Transmit(self, command: CecCommand):
        self._client.write(command.raw.encode())

    def SetCommandCallback(self, callback):
        self._command_callback = callback

    def PowerOnDevices(self):
        pass

    def set_transport(self, transport):
        self._transport = transport
