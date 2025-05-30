import asyncio
import logging
import time
from asyncio import Transport

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
    def __init__(self, host, port=DEFAULT_PORT, name=None, activate_source=None):
        super().__init__()
        self._polling = dict()
        self._tcp_loop = asyncio.new_event_loop()
        self._host = host
        self._port = port
        self._transport: Transport = None
        self._osd_name = name
        self._activate_source = activate_source

    async def async_init(self, callback: callable = None):
        _LOGGER.debug("Starting connection...")

        for i in range(0, MAX_CONNECTION_ATTEMPTS):
            try:
                self._transport, protocol = await self._tcp_loop.create_connection(lambda: TcpProtocol(self),
                                                                                   host=self._host, port=self._port)
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
            await self.async_shutdown()
        if self._transport:
            _LOGGER.debug("New client: %s", self._transport)
            self._initialized = True
            self._tcp_loop.run_in_executor(None, self._tcp_loop.run_forever)
        if callback:
            callback()

    async def async_shutdown(self):
        self._initialized = False
        if self._transport is not None:
            if not self._transport.is_closing():
                await self._loop.run_in_executor(self._transport.close)
        self._transport = None

    async def async_poll_device(self, device):
        timestamp = self._loop.time()
        poll_bucket = self._polling.get(device, set())
        poll_bucket.add(timestamp)
        self._polling.update({device: poll_bucket})
        await self.async_transmit(PollCommand(device))
        while self._loop.time() < (timestamp + 5):
            if timestamp not in self._polling.get(device, set()):
                _LOGGER.debug("Found device %d.", device)
                return True
            await asyncio.sleep(.1)
        return False

    def get_logical_address(self):
        return 0xf

    async def async_standby_devices(self):
        await self.async_transmit(CecCommand(CMD_STANDBY))

    async def async_transmit(self, command: CecCommand):
        if self._transport is not None:
            self._loop.run_in_executor(None, self._transport.write, ("%s\r\n" % command.raw).encode())
        else:
            _LOGGER.error("Can not transmit command. Transport is not initialized.")

    async def async_power_on_devices(self):
        await self.async_transmit(KeyPressCommand(KEY_POWER))
        await self.async_transmit(KeyReleaseCommand())

    @property
    def transport(self):
        return self._transport

    @transport.setter
    def transport(self, transport: Transport):
        self._transport = transport


class TcpProtocol(asyncio.Protocol):
    buffer = ''

    def __init__(self, adapter: TcpAdapter):
        self._adapter = adapter
        self._loop = adapter._loop

    def connection_made(self, transport):
        self._adapter.transport = transport

    def data_received(self, data: bytes):
        self.buffer += bytes.decode(data)
        for line in self.buffer.splitlines(keepends=True):
            if line.count('\n') or line.count('\r'):
                line = line.rstrip()
                _LOGGER.debug("Received %s from %s", line, self._adapter.transport.get_extra_info('peername'))
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
        self._adapter.async_shutdown()

    def connection_lost(self, exc):
        _LOGGER.warning("Connection lost. Trying to reconnect...")
        self._adapter.async_shutdown()
        self._adapter._tcp_loop.stop()
        self._adapter.init()


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

    tcp_adapter = TcpAdapter("192.168.1.5", name="HASS", activate_source=False)
    loop = asyncio.get_event_loop()
    hdmi_network = HDMINetwork(tcp_adapter, loop)
    loop.run_until_complete(hdmi_network.async_init())
    loop.create_task(hdmi_network.async_watch())
    try:
        while True:
            for d in hdmi_network.devices:
                _LOGGER.info("Device: %s", d)

            time.sleep(7)
    except KeyboardInterrupt:
        pass
    hdmi_network.async_shutdown()
