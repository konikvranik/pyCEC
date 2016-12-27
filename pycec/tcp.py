import asyncio
import functools
import logging
import signal
import time

from pycec.commands import CecCommand, KeyPressCommand, KeyReleaseCommand
from pycec.const import CMD_STANDBY, KEY_POWER
from pycec.network import AbstractCecAdapter, HDMINetwork

DEFAULT_PORT = 9526

_LOGGER = logging.getLogger(__name__)


# pragma: no cover
class TcpAdapter(AbstractCecAdapter):
    def __init__(self, host, port=DEFAULT_PORT, name=None,
                 activate_source=None):
        super().__init__()
        self._command_callback = None
        self._inner_loop = asyncio.new_event_loop()
        self._host = host
        self._port = port
        self._client = None
        self._transport = None
        self._osd_name = name
        self._activate_source = activate_source
        for signame in ('SIGINT', 'SIGTERM'):
            self._inner_loop.add_signal_handler(getattr(signal, signame),
                                                self.shutdown())

    def _after_init(self, callback, f):
        _LOGGER.debug("New client: %s", self._client)
        self._initialized = True
        if callback:
            callback()
        self._inner_loop.run_in_executor(None, self._inner_loop.run_forever)

    def init(self, callback: callable = None):
        future = asyncio.Future(loop=self._loop)
        future.add_done_callback(functools.partial(self._after_init, callback))
        _LOGGER.debug("Starting connection...")
        self._client, status = self._inner_loop.run_until_complete(
            self._inner_loop.create_connection(lambda: TcpProtocol(self),
                                               host=self._host,
                                               port=self._port))
        _LOGGER.debug("Connection started.")
        future.set_result(True)
        return future

    def shutdown(self):
        if self._client:
            self._client.close()
        if self._transport:
            self._transport.close()

    def poll_device(self, device):
        # self.transmit(CecCommand(CMD_POWER_STATUS[0], dst=device))
        f = asyncio.Future(loop=self._loop)
        f.set_result(True)
        return f

    def get_logical_address(self):
        return 0xf

    def standby_devices(self):
        self.transmit(CecCommand(CMD_STANDBY))

    def transmit(self, command: CecCommand):
        self._client.write(("%s\n" % command.raw).encode())

    def set_command_callback(self, callback):
        self._command_callback = callback

    def power_on_devices(self):
        self.transmit(KeyPressCommand(KEY_POWER))
        self.transmit(KeyReleaseCommand())

    def set_transport(self, transport):
        self._transport = transport


class TcpProtocol(asyncio.Protocol):
    buffer = ''

    def __init__(self, adapter: TcpAdapter):
        self._adapter = adapter
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        self._adapter.set_transport = transport

    def data_received(self, data: bytes):
        self.buffer += bytes.decode(data)
        for line in self.buffer.splitlines(keepends=True):
            if line.endswith('\n'):
                _LOGGER.debug("Received %s forom %s", line.rstrip(),
                              self.transport.get_extra_info('peername'))
                self._adapter._command_callback("<< " + line.rstrip())
                self.buffer = ''
            else:
                self.buffer = line

    def eof_received(self):
        self._adapter.shutdown()

    def connection_lost(self, exc):
        self._adapter.shutdown()


def main():
    tcp_adapter = TcpAdapter("192.168.1.3", name="HASS", activate_source=False)
    hdmi_network = HDMINetwork(tcp_adapter)
    hdmi_network.start()
    while True:
        for d in hdmi_network.devices:
            _LOGGER.info("Device: %s", d)

        time.sleep(2)


if __name__ == '__main__':
    # Configure logging
    _LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)

    main()
