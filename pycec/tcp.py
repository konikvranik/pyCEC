import asyncio
import functools
import logging
import time

from pycec.commands import CecCommand, KeyPressCommand, KeyReleaseCommand, \
    PollCommand
from pycec.const import CMD_STANDBY, KEY_POWER
from pycec.network import AbstractCecAdapter, HDMINetwork

DEFAULT_PORT = 9526
MAX_CONNECTION_ATTEMPTS = 5
CONNECTION_ATTEMPT_DELAY = 3
_LOGGER = logging.getLogger(__name__)


# pragma: no cover
class TcpAdapter(AbstractCecAdapter):
    def __init__(self, host, port=DEFAULT_PORT, name=None,
                 activate_source=None):
        super().__init__()
        self._polling = dict()
        self._command_callback = None
        self._tcp_loop = asyncio.new_event_loop()
        self._host = host
        self._port = port
        self._transport = None
        self._osd_name = name
        self._activate_source = activate_source

    def _after_init(self, callback, f):
        if self._transport:
            _LOGGER.debug("New client: %s", self._transport)
            self._initialized = True
            self._tcp_loop.run_in_executor(None, self._tcp_loop.run_forever)
        if callback:
            callback()

    def _init(self):
        for i in range(0, MAX_CONNECTION_ATTEMPTS):
            try:
                self._transport, protocol = self._tcp_loop.run_until_complete(
                    self._tcp_loop.create_connection(lambda: TcpProtocol(self),
                                                     host=self._host,
                                                     port=self._port))
                _LOGGER.debug("Connection started.")
                break
            except (ConnectionRefusedError, RuntimeError) as e:
                _LOGGER.warning(
                    "Unable to connect due to %s. Trying again in %d seconds, "
                    "%d attempts remaining.",
                    e, CONNECTION_ATTEMPT_DELAY, MAX_CONNECTION_ATTEMPTS - i)
                time.sleep(CONNECTION_ATTEMPT_DELAY)
        else:
            _LOGGER.error("Unable to connect! Giving up.")
            self.shutdown()

    def init(self, callback: callable = None):
        _LOGGER.debug("Starting connection...")
        task = self._loop.run_in_executor(None, self._init)
        task.add_done_callback(functools.partial(self._after_init, callback))
        return task

    def shutdown(self):
        self._initialized = False
        if self._transport and not self._transport.is_closing():
            self._transport.close()
        self._transport = None

    def _poll_device(self, device):
        req = self._loop.time()
        poll_bucket = self._polling.get(device, set())
        poll_bucket.add(req)
        self._polling.update({device: poll_bucket})
        self.transmit(PollCommand(device))
        while True:
            if req not in self._polling.get(device, set()):
                _LOGGER.debug("Found device %d.", device)
                return True
            if self._loop.time() > (req + 5):
                return False
            time.sleep(.1)

    def poll_device(self, device):
        return self._loop.run_in_executor(None, self._poll_device, device)

    def get_logical_address(self):
        return 0xf

    def standby_devices(self):
        self.transmit(CecCommand(CMD_STANDBY))

    def transmit(self, command: CecCommand):
        self._transport.write(("%s\r\n" % command.raw).encode())

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
            if line.count('\n') or line.count('\r'):
                line = line.rstrip()
                _LOGGER.debug("Received %s from %s", line,
                              self.transport.get_extra_info('peername'))
                if len(line) == 2:
                    cmd = CecCommand(line)
                    if cmd.src in self._adapter._polling:
                        del self._adapter._polling[cmd.src]
                else:
                    self._adapter._command_callback("<< " + line)
                self.buffer = ''
            else:
                self.buffer = line

    def eof_received(self):
        self._adapter.shutdown()

    def connection_lost(self, exc):
        _LOGGER.warning("Connection lost. Trying to reconnect...")
        self._adapter.shutdown()
        self._adapter._tcp_loop.stop()
        self._adapter.init()


def main():
    """For testing purpose"""
    tcp_adapter = TcpAdapter("192.168.1.5", name="HASS", activate_source=False)
    hdmi_network = HDMINetwork(tcp_adapter)
    hdmi_network.start()
    while True:
        for d in hdmi_network.devices:
            _LOGGER.info("Device: %s", d)

        time.sleep(7)


if __name__ == '__main__':
    # Configure logging
    _LOGGER.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    try:
        from colorlog import ColoredFormatter

        formatter = ColoredFormatter(
            "%(log_color)s%(levelname)-8s %(message)s",
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red',
            }
        )
    except ImportError:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)

    main()
