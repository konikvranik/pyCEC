import asyncio
import configparser
import logging
import os
from optparse import OptionParser

from pycec import (
    DEFAULT_PORT,
    DEFAULT_HOST,
    LOCALHOST,
    CONF_DEFAULT,
    CONF_INTERFACE,
    CONF_PORT,
    CONF_LOGLEVEL,
    CONF_HOST,
    MODE_SERVER,
    CONF_MODE,
    MODE_CLIENT,
    tcp,
    _LOGGER,
)
from pycec.cec import CecAdapter
from pycec.server import CECServer


def configure():
    parser = OptionParser()
    parser.add_option(
        "-i",
        "--interface",
        dest=CONF_INTERFACE,
        action="store",
        type="string",
        help="Address of interface to bind to.",
    )
    parser.add_option(
        "-s",
        "--host",
        dest=CONF_HOST,
        action="store",
        type="string",
        help="Address of interface to bind to.",
    )
    parser.add_option(
        "-p",
        "--port",
        dest=CONF_PORT,
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
    # Převod všech hodnot na řetězce
    config[CONF_DEFAULT] = {
        CONF_INTERFACE: str(options.interface) if options.interface is not None else "",
        CONF_HOST: str(options.host) if options.host is not None else "",
        CONF_PORT: str(options.port),
        CONF_LOGLEVEL: str(logging.INFO + ((options.quiet - options.verbose) * 10)),
    }
    paths = ["/etc/pycec.conf", script_dir + "/pycec.conf"]
    if "HOME" in os.environ:
        paths.append(os.environ["HOME"] + "/.pycec")
    config.read(paths)

    if config[CONF_DEFAULT][CONF_INTERFACE] and config[CONF_DEFAULT][CONF_HOST]:
        _LOGGER.error("Only one of --interface and --host can be used.")
        exit(1)
    elif config[CONF_DEFAULT][CONF_HOST]:
        config[CONF_DEFAULT][CONF_MODE] = MODE_CLIENT
    elif config[CONF_DEFAULT][CONF_INTERFACE]:
        config[CONF_DEFAULT][CONF_MODE] = MODE_SERVER

    return config


def setup_logger(config):
    try:
        log_level = int(config[CONF_DEFAULT][CONF_LOGLEVEL])
    except ValueError:
        log_level = config[CONF_DEFAULT][CONF_LOGLEVEL]
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


async def async_local_server(interface=DEFAULT_HOST, port: int = DEFAULT_PORT):

    server = CECServer(CecAdapter("CEC server"))
    server = await server.async_start(interface, port)
    async with server:
        await server.serve_forever()

    server.close()
    await server.wait_closed()


if __name__ == "__main__":

    config = configure()
    if CONF_MODE in config[CONF_DEFAULT]:
        setup_logger(config)
        if config[CONF_DEFAULT][CONF_MODE] == MODE_SERVER:
            asyncio.run(async_local_server(config[CONF_DEFAULT][CONF_INTERFACE], int(config[CONF_DEFAULT][CONF_PORT])))
        elif config[CONF_DEFAULT][CONF_MODE] == MODE_CLIENT:
            asyncio.run(
                tcp.async_client(config[CONF_DEFAULT][CONF_HOST] if CONF_HOST in config[CONF_DEFAULT] else LOCALHOST, int(config[CONF_DEFAULT][CONF_PORT]))
            )
