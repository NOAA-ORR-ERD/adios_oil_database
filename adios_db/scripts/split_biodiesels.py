#!/usr/bin/env python
'''
    Split up the Env. Canada biodiesel records.

    Env. Canada has a system for identifying the oil samples that exist
    for any particular oil.  Typically an oil sample will have a multipart
    numerical sample ID separated by periods (.), in which the first number
    will identify the oil that it is a part of.

    But in the case of biodiesel records, it appears that multiple biodiesels
    share a common first-part identifier.  So multiple samples that should
    belong to multiple unique oil records are being concatenated into a single
    record.

    Because this is an exceptional case that only affects a few records,
    we will post-process them in noaa-oil-data using this script.

    We will perform the following steps:

    - if you haven't gotten the repo yet:
      - git clone <noaa-oil-data-git-uri>
    - otherwise:
      - cd <path-to-noaa-oil-data-repo>
      - git pull
    - cd <this-folder>
    - python split_biodiesels.py <path-to-noaa-oil-data-repo>/data
'''
import sys
import io
import re
import logging
from argparse import ArgumentParser
from pathlib import Path
from itertools import zip_longest
import copy

from adios_db.models.oil.oil import Oil
from adios_db.models.oil.sample import SampleList


here = Path(__file__).resolve().parent
logger = logging.getLogger(__name__)
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

argp = ArgumentParser(description='Split Biodiesels Arguments:')

argp.add_argument('--path', nargs=1,
                  help=('Specify a path to the test data (filesystem). '
                        'If not specified, the default is to use "./data"'))


def split_biodiesels_cmd(argv):
    # make stderr unbuffered
    sys.stderr = io.TextIOWrapper(sys.stderr.detach().detach(),
                                  write_through=True)

    logging.basicConfig(level=logging.INFO, format=FORMAT)

    args = argp.parse_args(argv[1:])

    base_path = Path(args.path[0]) if args.path is not None else Path('./data')

    try:
        split_biodiesels(base_path)
    except Exception:
        print('{0}() FAILED\n'.format(split_biodiesels.__name__))
        raise


file_list = (
    ('oil', 'EC', 'EC01002.json'),
    ('oil', 'EC', 'EC01003.json'),
    ('oil', 'EC', 'EC01004.json'),
    ('oil', 'EC', 'EC01484.json'),
    ('oil', 'EC', 'EC01485.json'),
    ('oil', 'EC', 'EC01486.json'),
)


def split_biodiesels(base_path):
    '''
    Here is where we split the biodiesel records.
    '''
    logger.info('>> split_biodiesels()...')

    if base_path.is_dir():
        for p in file_list:
            read_path = Path(base_path).joinpath(*p)

            if read_path.is_file():
                # go ahead with modification
                logger.info('')
                logger.info(f'file: {Path(*p)}')

                #
                # split the file
                #
                oil_orig = Oil.from_file(read_path)
                names = split_names(oil_orig.metadata.name)
                comments = split_comments(oil_orig.metadata.comments)

                for sample, name, comment in zip_longest(oil_orig.sub_samples,
                                                         names, comments):
                    sample_id = sample.metadata.sample_id

                    oil_new = copy.deepcopy(oil_orig)

                    oil_new.metadata.name = name
                    oil_new.metadata.comments = comment
                    oil_new.oil_id = make_new_oil_id('EC', sample_id)
                    oil_new.metadata.source_id = sample_id

                    oil_new.sub_samples = SampleList([
                        s for s in oil_new.sub_samples
                        if s.metadata.sample_id == sample_id
                    ])

                    write_path = Path(base_path).joinpath(*p[:-1]) / f'{oil_new.oil_id}.json'
                    logger.info(f'\twrite path: {write_path}')
                    oil_new.to_file(write_path)
                
                read_path.unlink()
            else:
                sys.stdout.write(f'Error: "{read_path}" is not a file.\n')
    else:
        sys.stdout.write(f'Error: "{base_path}" is not a directory.\n')


def split_names(name):
    '''
        The way we imported these records, the names of the individual oils
        should be appended together.  Unfortunately we didn't have the
        foresight to put a separator between them.  But all the biodiesel
        records in the dataset have names that begin with 'Biodiesel'.
    '''
    names_idx = [m.start() for m in re.finditer('Bio', name)]

    return [name[begin:end].strip()
            for begin, end in zip_longest(names_idx, names_idx[1:])]


def split_comments(comments):
    '''
        The way we imported these records, the comments of the individual oils
        should be appended together.  Unfortunately we didn't have the
        foresight to put a separator between them.  But all the biodiesel
        records in the dataset have either redundant comment fields, or no
        comment field at all.
    '''
    try:
        first_word = comments.split(None, 1)[0]
    except:
        return []

    comments_idx = [m.start() for m in re.finditer(first_word, comments)]

    return [comments[begin:end].strip()
            for begin, end in zip_longest(comments_idx, comments_idx[1:])]


def make_new_oil_id(prefix, sample_id):
    new_id = int(''.join(sample_id.split('.')))
    return f'{prefix}{new_id:05d}'


if __name__ == "__main__":
    split_biodiesels_cmd(sys.argv)
















