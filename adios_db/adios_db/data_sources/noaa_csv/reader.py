"""
module for reading the "standard CSV format"

Generated from the Excel Template:

adios_db/data/ADIOS_data_template.xlsx
"""
import csv

from ...models.oil.oil import ADIOS_DATA_MODEL_VERSION, Version, Oil


def read_csv(filename, oil_id="PlaceHolder"):
    reader = Reader(oil_id)
    reader.load_from_csv(filename)

    return reader.oil


class Reader():
    def __init__(self, oil_id):
        self.oil = Oil(oil_id)

    def load_from_csv(self, infile):
        with open(infile, newline='') as csvfile:
            self.reader = reader = csv.reader(csvfile, delimiter=',')

            header = next(reader)
            if header[0].lower() == "ADIOS Data Model Version".lower():
                data_model_version = Version(header[1])
            else:
                raise ValueError("First line doesn't match "
                                 "-- are you sure this is a standard "
                                 "ADIOS CSV file?\n"
                                 f"First line of file: {header}")

            if data_model_version != ADIOS_DATA_MODEL_VERSION:
                raise ValueError("Version mismatch -- this file is: "
                                 f"{data_model_version}\n"
                                 "The code version is: "
                                 f"{ADIOS_DATA_MODEL_VERSION}")

            self.oil = Oil("Placeholder")

            # metadata
            line = next_non_empty(reader)
            if line[0].lower() != "Record Metadata".lower():
                raise ValueError("Next section should be Record Metadata")

            for line in reader:
                if line[0].lower().strip() == "subsample metadata":
                    print("reached subsample, breaking")
                    break
                else:
                    self.read_record_metadata(line)

    def read_record_metadata(self, line):
        line = [f.strip() for f in line]
        field = line[0].lower().strip()
        value = line[1].strip()

        print("reading metadata line")
        print(line)
        print(f"{field=}, {value=}")

        if field == "name":
            self.oil.metadata.name = value
        elif field == "api gravity":
            self.oil.metadata.API = round(float(value), 2)
        elif field == 'source id':
            self.oil.metadata.source_id = value
        elif field == 'alternate names':
            for name in line[1:]:
                if name:
                    self.oil.metadata.alternate_names.append(name)
        elif field == 'location':
            self.oil.metadata.location = value
        elif field == 'reference':
            try:
                year = int(value)
                print(year)

                if not(1900 < year < 2100):
                    raise ValueError("year not in bounds")
                self.oil.metadata.reference.year = int(value)
            except ValueError:
                raise

            if line[2]:
                self.oil.metadata.reference.reference = line[2].strip()


def next_non_empty(reader):
    """
    returns the next line that has nothing in the first field
    """
    while True:
        line = next(reader)
        if line[0]:
            return line
