import asyncio
import configparser
import functools
import getopt
import logging
import os
import sys

from pycec import DEFAULT_PORT, DEFAULT_HOST
from pycec.cec import CecAdapter
from pycec.commands import CecCommand, PollCommand
from . import _LOGGER
from .network import HDMINetwork


@asyncio.coroutine
def async_show_devices(network, loop):
    while True:
        for d in network.devices:
            _LOGGER.debug("Present device %s", d)
            yield
        yield from asyncio.sleep(10, loop=loop)


def usage():
    print("python -m pycec OPTS")
    print()
    print("OPTS:")
    print("    --interface=INTERFACE_ADDRESS    " +
          "Address of interface to bind to. Default is '%s'." % DEFAULT_HOST)
    print("    -i INTERFACE_ADDRESS")
    print()
    print("    --port=PORT                      " +
          "Port to bind to. Default is '%s'." % DEFAULT_PORT)
    print("    -p PORT")
    print("    --help                           " +
          "Print this help message.")
    print("    -h")
    print()
    pass


def main():
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:p:",
                                   ["help", "interface=", "port="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    for o, a in opts:
        if o in ("-i", "--interface"):
            host = a
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-p", "--port"):
            port = a
        else:
            assert False, "unhandled option"

    script_dir = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config['DEFAULT'] = {'host': host, 'port': port, 'logLevel': 'INFO'}
    config.read(['/etc/pycec.conf', os.environ['HOME'] + '/.pycec',
                 script_dir + '/pycec.conf'])

    # Configure logging
    setup_logger(config)

    transports = set()
    loop = asyncio.get_event_loop()
    network = HDMINetwork(CecAdapter("pyCEC", activate_source=False),
                          loop=loop)

    class CECServerProtocol(asyncio.Protocol):
        transport = None
        buffer = ''

        def connection_made(self, transport):
            _LOGGER.info("Connection opened by %s",
                         transport.get_extra_info('peername'))
            self.transport = transport
            transports.add(transport)

        def data_received(self, data):
            self.buffer += bytes.decode(data)
            for line in self.buffer.splitlines(keepends=True):
                if line.endswith('\n'):
                    line = line.rstrip()
                    if len(line) == 2:
                        _LOGGER.info("Received poll %s from %s", line,
                                     self.transport.get_extra_info('peername'))
                        d = CecCommand(line).dst
                        t = network._adapter.poll_device(d)
                        t.add_done_callback(
                            functools.partial(_after_poll, d))
                    else:
                        _LOGGER.info("Received command %s from %s", line,
                                     self.transport.get_extra_info('peername'))
                        network.send_command(CecCommand(line))
                    self.buffer = ''
                else:
                    self.buffer = line

        def connection_lost(self, exc):
            _LOGGER.info("Connection with %s lost",
                         self.transport.get_extra_info('peername'))
            transports.remove(self.transport)

    def _after_poll(d, f):
        if f.result():
            cmd = PollCommand(network._adapter.get_logical_address(), src=d)
            _send_command_to_tcp(cmd)

    def _send_command_to_tcp(command):
        for t in transports:
            _LOGGER.info("Sending %s to %s", command,
                         t.get_extra_info('peername'))
            t.write(str.encode("%s\n" % command.raw))

    network.set_command_callback(_send_command_to_tcp)
    loop.run_until_complete(network.async_init())

    _LOGGER.info("CEC initialized... Starting server.")
    # Each client connection will create a new protocol instance
    coro = loop.create_server(CECServerProtocol, config['host'],
                              config['port'])
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    _LOGGER.info('Serving on {}'.format(server.sockets[0].getsockname()))
    if _LOGGER.level >= logging.DEBUG:
        loop.create_task(async_show_devices(network, loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


def setup_logger(config):
    log_level = getattr(logging, config['logLevel'])
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


if __name__ == '__main__':
    main()
