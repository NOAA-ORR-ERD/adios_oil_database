#!/usr/bin/env python
"""
Process the ECCC oil records that have both types of distillation sets.
( /gnome/oil_database/oil_database/-/issues/587 )

There should be 106 such records in the source data.
I have placed the data file in the same folder as this script:
    ("./recs_with_both_dist_sets.csv").

Input: a list of CC related oil entries that were kept.

    - Column 1 (source_id): The source ID of the ECCC record
    - Column 2 (adios_id): The ADIOS ID of the imported ECCC record
    - Column 3 (fraction count): The number of cuts from Boiling Point
                                 Cumulative Weight Fraction
    - Column 4 (temperature count): The number of cuts from Boiling Point
                                    Temperature Cut Off
    - Column 5 (which has more?): Which distillation set has more cuts
                                  ("fraction count", "temperature count",
                                   "equal")

"""
import os
import sys
from pathlib import Path
from argparse import ArgumentParser

import csv

import adios_db
from adios_db.models.oil.oil import Oil


argp = ArgumentParser(description='Script Arguments:')
argp.add_argument('--path', nargs=1,
                  help=('Specify a path to a data storage area (filesystem). '
                        'If not specified, the default is to use "./data"'))
argp.add_argument('--source_path', nargs=1,
                  help=('Specify a path to a source file storage area '
                        '(filesystem). '
                        'If not specified, the default is to use "./data"'))
argp.add_argument('-d', '--dry_run', action='store_true',
                  help=('Do not perform the file actions, only print '
                        'the actions out.'))

def generate_sheet(file):
    wb = load_workbook(file, data_only=True)
    return wb['Sheet1']  # First sheet is not set in the file, use default.


def generate_row_iter(csvfile):
    csv_reader = csv.reader(csvfile)
    csv_reader.__next__()  # bypass column names

    return csv_reader


def oil_json_file_path(base_path, collection_name, oil_id):
    return (Path(base_path) / collection_name / oil_id[:2] / f'{oil_id}.json')


def clobber_file(oil_obj, oil_file_path, dry_run):
    """
    We basically are re-saving our file with new dist properties
    """
    print(f'clobbering {oil_obj.oil_id} into {oil_file_path}')
    if dry_run:
        return

    if oil_file_path.is_file():
        os.remove(oil_file_path)
    oil_obj.to_file(oil_file_path)


def rename_file(cc_obj, cc_file_path, ad_file_path, dry_run):
    print(f'rename {cc_file_path} to {ad_file_path}')
    if dry_run:
        return

    # The AD file doesn't exist, so the underlying paths might not either
    dir_path = os.path.dirname(ad_file_path)
    os.makedirs(dir_path, exist_ok=True)

    cc_obj.to_file(ad_file_path)
    os.remove(cc_file_path)


def set_id_from_filename(oil_obj, oil_file_path, dry_run):
    print(f'set_id_from_filename {oil_file_path}')
    oil_obj.oil_id = oil_file_path.name.split('.')[0]


def diag_print_oil_fields(oil_obj):
    msg = f'''    {oil_obj.oil_id=},'''
    for i, s in enumerate(oil_obj.sub_samples):
        msg += f'\n        s{i}: {[c.fraction.value for c in s.distillation_data.cuts]}'
    print(msg)


def get_fields_from_oil(ad_oil):
    new_reference_content = ('\n\n'
                             'As published in: '
                             'Environment and Climate Change Canada, '
                             'A Catalogue of Crude Oil and Oil Product Properties '
                             '(1999)- Revised 2022, '
                             'Environment and Climate Change Canada, 2022.')

    return (ad_oil.oil_id,
            ad_oil.metadata.labels,
            ad_oil.metadata.alternate_names,
            ad_oil.metadata.comments,
            ad_oil.metadata.reference.reference + new_reference_content)


def update_oil_fields(src_oil, dest_oil):
    """
    Basically we just copy over our cuts from the src to the dest object
    """
    if len(src_oil.sub_samples) != len(dest_oil.sub_samples):
        print(f'Warning: {src_oil.oil_id}: {len(src_oil.sub_samples)} samples'
              f'not equal to {dest_oil.oil_id}: {len(dest_oil.sub_samples)} samples')

    for src_smpl, dest_smpl in zip(src_oil.sub_samples, dest_oil.sub_samples):
        src_dist = src_smpl.distillation_data
        dest_dist = dest_smpl.distillation_data
        
        dest_dist.cuts = src_dist.cuts


def main(argv=sys.argv):
    args = argp.parse_args(argv[1:])

    source_path = Path('../distillation_cut_set_resolved')  # default
    if args.source_path is not None:
        source_path = Path(args.source_path[0])
    print(f'Work directory: {source_path}')

    base_path = Path(args.path[0]) if args.path is not None else Path('./data')
    print(f'Work directory: {base_path}')

    dry_run = args.dry_run
    if dry_run:
        print(f'Dry run...no files to be changed.')

    with open('./recs_with_both_dist_sets.csv', newline='') as csvfile:
        for r in generate_row_iter(csvfile):
            src_id, ad_id, frac_count, temp_count, chosen_set = [f.strip()
                                                                 for f in r]
            src_file = Path(source_path) / f'{ad_id}.json'
            dest_file = oil_json_file_path(base_path, "oil", ad_id)

            if src_file.is_file() and dest_file.is_file():
                src_oil = Oil.from_file(src_file)
                dest_oil = Oil.from_file(dest_file)

                # copy distillation sets from src to dest & save dest
                print(f'\nCopy {src_file} distillation sets to {dest_file}.')

                #print('Before:')
                #diag_print_oil_fields(dest_oil)

                update_oil_fields(src_oil, dest_oil)

                #print('After:')
                #diag_print_oil_fields(dest_oil)

                clobber_file(dest_oil, dest_file, dry_run)
            elif src_file.is_file():
                # copy src to dest since dest file doesn't exist
                #print(f'Copy {src_file} to {dest_file}.')

                src_oil = Oil.from_file(src_file)
                clobber_file(src_oil, dest_file, dry_run)
            else:
                print(f'{src_file} file is missing.')


            #diag_print_oil_fields(cc_oil)
            pass


if __name__ == "__main__":
    main()
