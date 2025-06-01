"""pyCEC"""

import ctypes
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


def initialize_cec():
    """Inicializuje CEC knihovnu a přidá cestu do PYTHONPATH"""
    # Získání absolutní cesty k adresáři skriptu
    script_dir = os.path.dirname(os.path.abspath(__file__))
    libs_dir = os.path.join(script_dir, "../libs")

    # Přidání cesty k knihovnám do LD_LIBRARY_PATH
    if "LD_LIBRARY_PATH" in os.environ:
        os.environ["LD_LIBRARY_PATH"] = libs_dir + ":" + os.environ["LD_LIBRARY_PATH"]
    else:
        os.environ["LD_LIBRARY_PATH"] = libs_dir

    # Přidání cesty pro Windows
    if sys.platform.startswith("win"):
        if "PATH" in os.environ:
            os.environ["PATH"] = libs_dir + ";" + os.environ["PATH"]
        else:
            os.environ["PATH"] = libs_dir

    # Přidání cesty do sys.path pro Python moduly
    if libs_dir not in sys.path:
        sys.path.insert(0, libs_dir)

    # Explicitní načtení libcec knihovny
    try:
        if sys.platform.startswith("win"):
            libcec_path = os.path.join(libs_dir, "libcec.dll")
        else:
            libcec_path = os.path.join(libs_dir, "libcec.so")

        ctypes.CDLL(libcec_path)
        print(f"Úspěšně načtena knihovna libcec z {libcec_path}")
        return True
    except Exception as e:
        print(f"Chyba při načítání libcec: {str(e)}")
        return False


# Automaticky inicializujte při importu balíčku
initialize_cec()
