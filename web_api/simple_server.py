#!/usr/bin/env python

"""
start up script for the simplehttp server

this is the same as calling it on the command line:

python -m http.server <port_number>

(in fact, I copied (and trimmed) the code in the
__name__ == "__main__" block) from cPython 3.7
"""

import os
import argparse
from pathlib import Path
from functools import partial

from http.server import SimpleHTTPRequestHandler, test


parser = argparse.ArgumentParser()
parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                    help='Specify alternate bind address '
                         '[default: all interfaces]')
parser.add_argument('--directory', '-d', default=os.getcwd(),
                    help='Specify alternative directory '
                    '[default:current directory]')
parser.add_argument('port', action='store',
                    default=8000, type=int,
                    nargs='?',
                    help='Specify alternate port [default: 8000]')
args = parser.parse_args()


directory = str(Path(args.directory).resolve())

handler_class = partial(SimpleHTTPRequestHandler,
                        directory=directory)

# why is this called test ?!?
test(HandlerClass=handler_class, port=args.port, bind=args.bind)


