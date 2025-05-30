import asyncio
import configparser
import logging
import os
from optparse import OptionParser

from pycec import DEFAULT_PORT, DEFAULT_HOST, LOCALHOST, CONF_DEFAULT, CONF_INTERFACE, CONF_PORT
from pycec.server import CECServer
from . import _LOGGER


def configure():
    parser = OptionParser()
    parser.add_option(
        "-i",
        "--interface",
        dest="interface",
        action="store",
        type="string",
        default=DEFAULT_HOST,
        help=("Address of interface to bind to. Default is '%s'." % DEFAULT_HOST),
    )
    parser.add_option(
        "-h",
        "--host",
        dest="host",
        action="store",
        type="string",
        default=DEFAULT_HOST,
        help=("Address of interface to bind to. Default is '%s'." % LOCALHOST),
    )
    parser.add_option(
        "-p",
        "--port",
        dest="port",
        action="store",
        type="int",
        default=DEFAULT_PORT,
        help=("Port to bind to. Default is '%s'." % DEFAULT_PORT),
    )
    parser.add_option("-v", "--verbose", dest="verbose", action="count", default=0, help="Increase verbosity.")
    parser.add_option("-q", "--quiet", dest="quiet", action="count", default=0, help="Decrease verbosity.")
    (options, args) = parser.parse_args()
    script_dir = os.path.dirname(os.path.realpath(__file__))
    config = configparser.ConfigParser()
    config["DEFAULT"] = {
        "interface": options.interface,
        "port": options.port,
        "logLevel": logging.INFO + ((options.quiet - options.verbose) * 10),
    }
    paths = ["/etc/pycec.conf", script_dir + "/pycec.conf"]
    if "HOME" in os.environ:
        paths.append(os.environ["HOME"] + "/.pycec")
    config.read(paths)

    return config


def setup_logger(config):
    try:
        log_level = int(config["DEFAULT"]["logLevel"])
    except ValueError:
        log_level = config["DEFAULT"]["logLevel"]
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
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
    except ImportError:
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    _LOGGER.addHandler(ch)


def local_server(loop, interface=DEFAULT_HOST, port: int = DEFAULT_PORT):

    server = CECServer(loop)
    loop.run_until_complete(server.start(interface, port))
    server.stop()


if __name__ == "__main__":
    config = configure()
    setup_logger(config)
    loop = asyncio.get_event_loop()
    local_server(loop, config[CONF_DEFAULT][CONF_INTERFACE], int(config[CONF_DEFAULT][CONF_PORT]))
    loop.stop()
    loop.close()
