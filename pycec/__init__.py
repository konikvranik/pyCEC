"""pyCEC"""

import logging
import os
import sys

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 9526
DEFAULT_HOST = "0.0.0.0"
LOCALHOST = "127.0.0.1"

CONF_DEFAULT = "DEFAULT"
CONF_PORT = "port"
CONF_HOST = "host"
CONF_INTERFACE = "interface"
CONF_LOGLEVEL = "logLevel"
CONF_MODE = "mode"

MODE_SERVER = "server"
MODE_CLIENT = "client"


"""Inicializuje CEC knihovnu a přidá cestu do PYTHONPATH"""
script_dir = os.path.dirname(os.path.abspath(__file__))
libs_dir = os.path.join(script_dir, "../libs")

if "LD_LIBRARY_PATH" in os.environ:
    os.environ["LD_LIBRARY_PATH"] = libs_dir + ":" + os.environ["LD_LIBRARY_PATH"]
else:
    os.environ["LD_LIBRARY_PATH"] = libs_dir

if sys.platform.startswith("win"):
    if "PATH" in os.environ:
        os.environ["PATH"] = libs_dir + ";" + os.environ["PATH"]
    else:
        os.environ["PATH"] = libs_dir

if libs_dir not in sys.path:
    sys.path.insert(0, libs_dir)
