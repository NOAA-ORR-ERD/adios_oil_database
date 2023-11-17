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

    print("writing: adios_distillation_data.tsv")
    outfile = open("adios_distillation_data.tsv", 'w')

    outfile.write(f"Oil ID\tName\tproduct_type\tdistillation_method\tfraction_recovered\tTBP\n")
    # outfile.write(f"Oil ID\tName\tReference\tdistillation_method\tfraction_recovered\n")
    PROD_TYPES = {"Distillate Fuel Oil", "Bio-Petro Fuel Oil"}
    for rec, pth in ads.get_all_records(base_dir):
        ID = rec.oil_id
        print(f"searching: {ID}")
        name = rec.metadata.name
        reference = rec.metadata.reference.reference.replace("\n", " ")
        dist_method = rec.sub_samples[0].distillation_data.method
        frac_recov = rec.sub_samples[0].distillation_data.fraction_recovered
        tbp = rec.sub_samples[0].distillation_data.end_point
        product_type = rec.metadata.product_type
        if frac_recov is not None and product_type in PROD_TYPES:
            frac_recov = frac_recov.converted_to('%').as_text()
            if tbp is not None:
                tbp = tbp.converted_to('C').as_text()
            outfile.write(f'{ID} \t"{name}"\t{product_type}\t{dist_method} \t{frac_recov}%\t{tbp}C\n')
            # outfile.write(f'{ID} \t"{name}" \t"{reference}" \t{dist_method} \t{frac_recov}\n')

if __name__ == "__main__":
    main()
