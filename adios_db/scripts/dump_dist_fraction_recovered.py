#!/usr/bin/env python

"""
script to dump the distillation cut fraction recovered data

well, the distillation data, so we can add the fraction recovered
"""

import adios_db.scripting as ads




USAGE = """
dump_dist_fraction_recovered [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():

    base_dir, dry_run = ads.process_input(USAGE)

    print("writing: adios_distillation_data.csv")
    outfile = open("adios_distillation_data.csv", 'w')

    outfile.write(f"Oil ID\tName\tReference\tdistillation_method\tfraction_recovered\n")
    for rec, pth in ads.get_all_records(base_dir):
        ID = rec.oil_id
        name = rec.metadata.name
        reference = rec.metadata.reference.reference
        dist_method = rec.sub_samples[0].distillation_data.method
        frac_recov = rec.sub_samples[0].distillation_data.fraction_recovered

        outfile.write(f'{ID} \t"{name}" \t"{reference}" \t{dist_method} \t{frac_recov}\n')


if __name__ == "__main__":
    main()