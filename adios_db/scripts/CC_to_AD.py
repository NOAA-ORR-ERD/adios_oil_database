#!/usr/bin/env python
"""
Process the ECCC oil records that were reconciled by Rin.  He merged the data
for most of the records, and has compiled a spreadsheet list of "CC" record IDs
and their associated AD IDs.

I have placed the file in the same folder as this script ("./CC_to_AD.xlsx").

Input: a list of CC related oil entries that were kept.

    - Column 1 ("CC ID"): The CC ID oil entry that is still up on the
                          Stage Server.
    - Column 2 ("New AD ID"): The AD ID that was a match to the CC in the
                              first column.

Chris wants the first column names to be changed to the second column names.
Rin went through and got rid of the other issues (i.e IDs for the CC that we
got rid of or kept because there were no exact matches), so there are only
the CCs that we kept that need to be renamed.
"""
import os
import sys
from pathlib import Path
from argparse import ArgumentParser

from openpyxl import load_workbook

import adios_db
from adios_db.models.oil.oil import Oil


argp = ArgumentParser(description='Database Backup Arguments:')
argp.add_argument('--path', nargs=1,
                  help=('Specify a path to a data storage area (filesystem). '
                        'If not specified, the default is to use "./data"'))
argp.add_argument('-d', '--dry_run', action='store_true',
                  help=('Do not perform the file actions, only print '
                        'the actions out.'))

def generate_sheet(file):
    wb = load_workbook(file, data_only=True)
    return wb['Sheet1']  # First sheet is not set in the file, use default.


def generate_row_iter(sheet):
    sheet_iter = sheet.iter_rows()
    sheet_iter.__next__()  # bypass column names

    return sheet_iter


def oil_json_file_path(base_path, collection_name, oil_id):
    return (Path(base_path) / collection_name / oil_id[:2] / f'{oil_id}.json')


def clobber_file(cc_file, ad_file, dry_run):
    print(f'clobbering {cc_file} into {ad_file}')
    if dry_run:
        return

    temp_oil = Oil.from_file(cc_file)
    temp_oil.oil_id = ad_file.name.split('.')[0]

    os.remove(ad_file)
    temp_oil.to_file(ad_file)
    os.remove(cc_file)


def rename_file(cc_file, ad_file, dry_run):
    print(f'rename {cc_file} to {ad_file}')
    if dry_run:
        return

    temp_oil = Oil.from_file(cc_file)
    temp_oil.oil_id = ad_file.name.split('.')[0]

    # The AD file doesn't exist, so the underlying paths might not either
    dir_path = os.path.dirname(ad_file)
    os.makedirs(dir_path, exist_ok=True)

    temp_oil.to_file(ad_file)
    os.remove(cc_file)


def set_id_to_filename(cc_file, ad_file, dry_run):
    print(f'set_id_to_filename {ad_file}')
    if dry_run:
        return

    temp_oil = Oil.from_file(ad_file)

    temp_oil.oil_id = ad_file.name.split('.')[0]
    temp_oil.to_file(ad_file)


def main(argv=sys.argv):
    args = argp.parse_args(argv[1:])

    base_path = Path(args.path[0]) if args.path is not None else Path('./data')
    print(f'Work directory: {base_path}')

    dry_run = args.dry_run
    if dry_run:
        print(f'Dry run...no files to be changed.')

    sheet = generate_sheet(Path('./CC_to_AD.xlsx'))

    for r in generate_row_iter(sheet):
        cc_id, ad_id = [f.value for f in r]
        cc_file = oil_json_file_path(base_path, "oil", cc_id)
        ad_file = oil_json_file_path(base_path, "oil", ad_id)

        if ad_file.is_file():
            set_id_to_filename(cc_file, ad_file, dry_run)
        else:
            print(f'{ad_file} does not exist.')


if __name__ == "__main__":
    main()
