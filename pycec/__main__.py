import asyncio
import configparser
import functools
import logging
import os
from asyncio import futures, Transport
from optparse import OptionParser

from pycec import DEFAULT_PORT, DEFAULT_HOST
from pycec.cec import CecAdapter
from pycec.commands import CecCommand, PollCommand
from . import _LOGGER
from .network import HDMINetwork


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
                    t: futures.Future = self._hdmi_network._adapter.poll_device(device)
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


def configure():
    parser = OptionParser()
    parser.add_option("-i", "--interface", dest="host", action="store", type="string", default=DEFAULT_HOST,
                      help=("Address of interface to bind to. Default is '%s'." % DEFAULT_HOST))
    parser.add_option("-p", "--port", dest="port", action="store", type="int", default=DEFAULT_PORT,
                      help=("Port to bind to. Default is '%s'." % DEFAULT_PORT))
    parser.add_option("-v", "--verbose", dest="verbose", action="count", default=0, help="Increase verbosity.");
    parser.add_option("-q", "--quiet", dest="quiet", action="count", default=0, help="Decrease verbosity.")
    (options, args) = parser.parse_args()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'host': options.host, 'port': options.port,
                         'logLevel': logging.INFO + ((options.quiet - options.verbose) * 10)}
    paths = ['/etc/pycec.conf', script_dir + '/pycec.conf']
    if 'HOME' in os.environ:
        paths.append(os.environ['HOME'] + '/.pycec')
    config.read(paths)

    return config


def setup_logger(config):
    try:
        log_level = int(config['DEFAULT']['logLevel'])
    except ValueError:
        log_level = config['DEFAULT']['logLevel']
    _LOGGER.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
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


async def async_show_devices(network, loop):
    while True:
        async for d in network.devices:
            _LOGGER.debug("Present device %s", d)
        await asyncio.sleep(10)


def main():
    config = configure()

    # Configure logging
    setup_logger(config)

    loop = asyncio.get_event_loop()
    network = HDMINetwork(CecAdapter("pyCEC", activate_source=False), loop=loop)

    _LOGGER.info("CEC initialized... Starting server.")
    # Each client connection will create a new protocol instance
    connections = set()

    def _send_command_to_tcp(command):
        for c in connections:
            c.send_command_to_tcp(command)

    network.set_command_callback(_send_command_to_tcp)
    loop.run_until_complete(network.async_init())

    server = loop.run_until_complete(
        loop.create_server(lambda: CECServerProtocol(network, connections), config['DEFAULT']['host'],
                           int(config['DEFAULT']['port'])))
    # Serve requests until Ctrl+C is pressed
    _LOGGER.info('Serving on {}'.format(server.sockets[0].getsockname()))
    if _LOGGER.level >= logging.DEBUG:
        asyncio.run(async_show_devices(network, loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__ == "__main__":
    main()
