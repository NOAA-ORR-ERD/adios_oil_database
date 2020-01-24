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
import contextlib
from pathlib import Path
import socket
from functools import partial

from http.server import SimpleHTTPRequestHandler, test, ThreadingHTTPServer


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

print("args:",args)

directory = str(Path(args.directory).resolve())

handler_class = partial(SimpleHTTPRequestHandler,
                        directory=directory)

print(handler_class)

test(HandlerClass=handler_class, port=args.port, bind=args.bind)


# master version -- didn't work with 3.7
# parser = argparse.ArgumentParser()
# parser.add_argument('--directory', '-d', default=os.getcwd(),
#                     help='Specify alternative directory '
#                          '[default:current directory]')
# parser.add_argument('port', action='store',
#                     default=8000, type=int,
#                     nargs='?',
#                     help='Specify alternate port [default: 8000]')
# parser.add_argument('--bind', '-b', metavar='ADDRESS',
#                     help='Specify alternate bind address '
#                          '[default: all interfaces]')
# args = parser.parse_args()

# print("args are:", args)

# handler_class = partial(SimpleHTTPRequestHandler,
#                         directory=args.directory)


# # ensure dual-stack is not disabled; ref #38907
# class DualStackServer(ThreadingHTTPServer):
#     def server_bind(self):
#         # suppress exception when protocol is IPv4
#         with contextlib.suppress(Exception):
#             self.socket.setsockopt(
#                 socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
#         return super().server_bind()

# # why in the worls is this called "test"? -- oh well
# test(HandlerClass=handler_class,
#      ServerClass=DualStackServer,
#      port=args.port,
#      bind=args.bind,
#      )



