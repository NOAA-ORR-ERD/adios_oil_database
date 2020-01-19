#!/usr/bin/env python
#
# This script performs a very stripped-down version of what pserve might do,
# with no process monitoring, and very simple argument parsing.
#

import argparse
import sys

from pyramid.scripts.common import get_config_loader


class ServerCommand(object):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('config_uri', nargs='?', default=None,
                        help='The URI to the configuration file.')

    _get_config_loader = staticmethod(get_config_loader)

    def __init__(self, argv, quiet=False):
        self.args = self.parser.parse_args(argv[1:])

    def run(self):
        if not self.args.config_uri:
            print('You must specify a config file')
            return 2

        loader = self._get_config_loader(self.args.config_uri)
        loader.setup_logging()

        server = loader.get_wsgi_server('main')
        app = loader.get_wsgi_app()

        try:
            server(app)
        except (SystemExit, KeyboardInterrupt) as e:
            if str(e):
                msg = ' ' + str(e)
            else:
                msg = ''
            print('Exiting%s' % msg)


def main(argv=sys.argv, quiet=False):
    command = ServerCommand(argv, quiet=quiet)
    return command.run()


if __name__ == '__main__':
    sys.exit(main() or 0)
