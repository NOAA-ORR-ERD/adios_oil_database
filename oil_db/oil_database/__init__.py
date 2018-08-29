import os
import sys
import logging

from pkg_resources import get_distribution

try:
    __version__ = get_distribution('oil_database').version
except Exception:
    __version__ = 'not_found'


def initialize_console_log(level='debug'):
    '''
    Initializes the logger to simply log everything to the console (stdout)
    Likely what you want for scripting use

    :param level='debug': the level you want your log to show. options are,
                          in order of importance: "debug", "info", "warning",
                          "error", "critical"

    You will only get the logging messages at or above the level you set.
    '''
    levels = {"debug": logging.DEBUG,
              "info": logging.INFO,
              "warning": logging.WARNING,
              "error": logging.ERROR,
              "critical": logging.CRITICAL,
              }

    level = levels[level.lower()]
    format_str = '%(levelname)s - %(module)8s - line:%(lineno)d - %(message)s'

    logging.basicConfig(stream=sys.stdout, level=level, format=format_str)


# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
