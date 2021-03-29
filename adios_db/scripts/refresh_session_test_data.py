#!/usr/bin/env python
'''
    Refresh the test data files for the session pytests.
    
    Periodically, we make code changes and changes to the actual records,
    and we need to make sure the pytests are performing tests with data that
    has proper data and good structure.  This data is located in the Git
    project noaa-oil-data.  So we will perform the following steps:

    - if you haven't gotten the repo yet:
      - git clone <noaa-oil-data-git-uri>
    - otherwise:
      - cd <path-to-noaa-oil-data-repo>
      - git pull
    - cd <this-folder>
    - python refresh_session_test_data.py <path-to-noaa-oil-data-repo>/data
'''
import sys
import io
import logging
import shutil
from argparse import ArgumentParser
from pathlib import Path

here = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

argp = ArgumentParser(description='Refresh Test Data Arguments:')

argp.add_argument('--path', nargs=1,
                  help=('Specify a path to the test data (filesystem). '
                        'If not specified, the default is to use "./data"'))


def refresh_test_data_cmd(argv):
    # make stderr unbuffered
    sys.stderr = io.TextIOWrapper(sys.stderr.detach().detach(),
                                  write_through=True)

    logging.basicConfig(level=logging.INFO, format=FORMAT)

    args = argp.parse_args(argv[1:])

    base_path = Path(args.path[0]) if args.path is not None else Path('./data')

    try:
        refresh_test_data(base_path)
    except Exception:
        print('{0}() FAILED\n'.format(refresh_test_data.__name__))
        raise


file_list = (
    ('oil', 'AD', 'AD00005.json'),
    ('oil', 'AD', 'AD00009.json'),
    ('oil', 'AD', 'AD00010.json'),
    ('oil', 'AD', 'AD00017.json'),
    ('oil', 'AD', 'AD00020.json'),
    ('oil', 'AD', 'AD00024.json'),
    ('oil', 'AD', 'AD00025.json'),
    ('oil', 'AD', 'AD00038.json'),
    ('oil', 'AD', 'AD00047.json'),
    ('oil', 'AD', 'AD00084.json'),
    ('oil', 'AD', 'AD00125.json'),
    ('oil', 'AD', 'AD00135.json'),
    ('oil', 'AD', 'AD00269.json'),
    ('oil', 'AD', 'AD01500.json'),
    ('oil', 'AD', 'AD01598.json'),
    ('oil', 'AD', 'AD01853.json'),
    ('oil', 'AD', 'AD01901.json'),
    ('oil', 'AD', 'AD01987.json'),
    ('oil', 'AD', 'AD01998.json'),
    ('oil', 'AD', 'AD02068.json'),
    ('oil', 'EC', 'EC00506.json'),
    ('oil', 'EC', 'EC00540.json'),
    ('oil', 'EC', 'EC00561.json'),
    ('oil', 'EC', 'EC02234.json'),
    ('oil', 'EC', 'EC02713.json'),
    ('oil', 'EX', 'EX00026.json'),
)


def refresh_test_data(base_path):
    '''
        Here is where we refresh the data that the session pytests use.
    '''
    logger.info('>> refresh_test_data()...')

    dest = here.parent / 'adios_db' / 'test' / 'test_session' / 'test_data'

    if base_path.is_dir() and dest.is_dir():
        for p in file_list:
            read_path = Path(base_path).joinpath(*p)
            write_path = Path(dest).joinpath(*p)

            if read_path.is_file() and write_path.parent.is_dir():
                # go ahead with the copy
                logger.info(f'copying {Path(*p)}')
                shutil.copy(read_path, write_path)
            elif not read_path.is_file():
                sys.stdout.write(f'Error: "{read_path}" is not a file.\n')
            else:
                sys.stdout.write(f'Error: "{write_path.parent}" is not a directory.\n')
    else:
        if not base_path.is_dir():
            sys.stdout.write(f'Error: "{base_path}" is not a directory.\n')
        else:
            sys.stdout.write(f'Error: "{dest}" is not a directory.\n')


if __name__ == "__main__":
    refresh_test_data_cmd(sys.argv)
