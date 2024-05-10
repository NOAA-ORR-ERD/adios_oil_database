#!/usr/bin/env python
"""
script to set fraction recovered to 100% for distillate fuels
and oils with a method that is known to give 100%

Methods:

ASTM D86: The test method is designed for the analysis of
          distillate fuels; it is not applicable to products
          containing appreciable quantities of residual material.

            NOT set to 100%

ASTM D7169: Standard Test Method for Boiling Point Distribution
            of Samples with Residues Such as Crude Oils

            Set to 100%

ASTM D6730: This test method covers the determination of individual
            hydrocarbon components of spark-ignition engine fuels
            and their mixtures containing oxygenate blends
            (MTBE, ETBE, ethanol, and so forth) with boiling ranges up to 225°C

            Not set to 100% (unless combined with ASTM D7169)

ASTM D2887: Boiling range distributions obtained by this test method are essentially
            equivalent to those obtained by true boiling point (TBP) distillation.

            Set to 100%

ESTS 5.10/x.x/M: don't know what to do with this -- will send not to ESTS.





"""
import adios_db.scripting as ads



USAGE = """
update_dist_fraction_recovered.py [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():
    base_dir, dry_run = ads.process_input(USAGE)

    for rec, pth in ads.get_all_records(base_dir):
        ID = rec.oil_id
#        print(f"searching: {ID}")
        name = rec.metadata.name
        distillation_data = rec.sub_samples[0].distillation_data
        dist_method = distillation_data.method
        frac_recov = distillation_data.fraction_recovered
        dist_cuts = distillation_data.cuts
        product_type = rec.metadata.product_type
        if product_type == "Distillate Fuel Oil" and dist_cuts:
            # print("number of cuts", len(dist_cuts))
            # print("Found a Distillate:", ID)
            # print("Fraction_recovered:", repr(frac_recov))
            distillation_data.fraction_recovered = ads.MassOrVolumeFraction(value=100.0, unit='%', unit_type='massfraction')
        elif dist_method:
            print(ID, dist_method)
            if (("ASTM D7169" in dist_method)
                or ("D2887" in dist_method)
                ):
                print("Setting Fraction recovered to 100%")
                distillation_data.fraction_recovered = ads.MassOrVolumeFraction(value=100.0, unit='%', unit_type='massfraction')

        if not dry_run:
            # print("saving out:", ID)
            rec.to_file(pth)
        else:
            pass
            # print("not saving")

if __name__ == "__main__":
    main()
