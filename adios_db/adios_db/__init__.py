import sys
from logging import (basicConfig, getLogger, NullHandler,
                     DEBUG, INFO, WARNING, ERROR, CRITICAL)


__version__ = "1.2.7"


def initialize_console_log(level='debug'):
    '''
    Initializes the logger to simply log everything to the console (stdout)
    Likely what you want for scripting use

    :param level='debug': the level you want your log to show. options are,
                          in order of importance: "debug", "info", "warning",
                          "error", "critical"

    You will only get the logging messages at or above the level you set.
    '''
    levels = {"debug": DEBUG,
              "info": INFO,
              "warning": WARNING,
              "error": ERROR,
              "critical": CRITICAL,
              }

    level = levels[level.lower()]
    format_str = '%(levelname)s - %(module)8s - line:%(lineno)d - %(message)s'

    basicConfig(stream=sys.stdout, level=level, format=format_str, force=True)


getLogger(__name__).addHandler(NullHandler())
