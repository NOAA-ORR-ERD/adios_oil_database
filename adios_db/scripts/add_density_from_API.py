#!/usr/bin/env python3
"""
script to go through all the data, and add an API if one is not already there

This could use a bit more polish:
  - flag to have it report what it will do, but not do it
  - pass in a single file or the whole dir

Testing! -- not entirely sure if it breaks the records!
"""
import unit_conversion as uc
import adios_db.scripting as ads


USAGE = """
add_density_from data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""


def main():
    base_dir, dry_run = ads.process_input(USAGE)

    for rec, pth in ads.get_all_records(base_dir):
        # print("\n\n******************\n")
        # print("processing:", rec.oil_id)
        # print("API is:", rec.metadata.API)
        densities = rec.sub_samples[0].physical_properties.densities

        if len(densities) == 0:
            print("no density data in record:", rec.oil_id)
            API = rec.metadata.API
            print("API is:", API)

            if API is None:
                print("No API provided, moving on")
                continue
            else:
                dens = round(uc.convert("api", "kg/m^3", API), 2)
                density = ads.Density(dens, unit="kg/m^3")
                temp = ads.Temperature(288.16, unit="K")

                densities.append(ads.DensityPoint(
                    density=density,
                    ref_temp=temp,
                    method="Converted from API"
                ))

            print("Densities:", densities[0])

            if not dry_run:
                print("Saving out:", pth)
                rec.to_file(pth)
            else:
                print("Nothing saved")


if __name__ == "__main__":
    main()
