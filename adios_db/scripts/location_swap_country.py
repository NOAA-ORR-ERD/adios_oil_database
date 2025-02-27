#!/usr/bin/env python
"""
This updates the location field for more normalization

It normalized whether it's country, location vs location, county
e.g "Canada, Beaufort Sea" vs "Beaufort Sea, Canada")

The second is prefered

"""

import sys

from adios_db.scripting import get_all_records, process_input

# orig_locations = ("Gulf of Mexico", "USA, Gulf of Mexico", "Gulf of Mexico, USA", "Gulf of Mexico")
# new_location = "Gulf of America"

# orig_locations = ("USA, Alaska",)
# new_location = "Alaska, USA"

# orig_locations = ("Canada, Beaufort Sea", "Beaufort Sea, Canada")
# new_location = "Beaufort Sea, Canada"

# orig_locations = ("Canada, Alberta", "Alberta, Canada")
# new_location = "Alberta, Canada"


USAGE = """
update_location_field.py data_dir [dry_run]

data_dir is the dir where the data are: the script will recursively
search for JSON files

If "dry_run" is on the command line, it will report what it would do,
but not save any changes
"""
countries = {
 'Mauritius',
 'Australia',
 'Denmark',
 'Texas, Beaumont',
 'Alaska, ALPINE MODULE AT KUPARUK CPF-2',
 'New Zealand',
 'Pennsylvania, Philadelphia',
 'Colombia',
 'Mexico',
 'Texas, Houston',
 'Argentina',
 'Germany',
 'Venezuela',
 'Qatar',
 'Canada',
 'Libya',
 'Norway',
 'Japan',
 'Brazil',
 'UK',
 'Zaire',
 'Hong Kong',
 'Busan',
 'Indonesia',
 'Angola',
 'Iran',
 'United Kingdom',
 'Iraq',
 'China',
 'the Netherlands',
 'Saudi Arabia',
 'Singapore',
 'South Korea',
 'Nigeria',
 'Egypt',
 'USA',
 'United Arab Emirates',
}

def normalize(name):
    name = " ".join(namestrip().split())
    return name

def run_through():
    base_dir, dry_run = process_input(USAGE=USAGE)
    countries_in_data = set()
    for oil, pth in get_all_records(base_dir):
        id = oil.oil_id
        name = oil.metadata.name
        location = oil.metadata.location

        splitup = location.split(", ", maxsplit=1)

        if len(splitup) == 2:
            countries_in_data.add(splitup[0])
            countries_in_data.add(splitup[1])
        if len(splitup) == 2 and splitup[0] in countries:
            # breakpoint()
            new_location = ", ".join((splitup[1], splitup[0]))

            # Is this the only one?
            if new_location.rsplit(', ')[1] == "UK":
                new_location.replace(", UK", ", United Kingdom")
                # breakpoint()
        # for orig in orig_locations:
        #     if normalize(location) == normalize(orig):
        #         match = True
        #         break
        # else:
        #     match = False
        # if match:
            print("\nProcessing:", id, name)
            print("location was:", location)
            print("changing location to:", new_location)

            oil.metadata.location = new_location

            if not dry_run:
                print("Saving out:", pth)
                oil.to_file(pth)
            else:
                print("Dry Run: Nothing saved")

    with open("country_locations.txt",'w') as outfile:
        for location in countries_in_data:
            outfile.write(f"{location}\n")



if __name__ == "__main__":
    run_through()
