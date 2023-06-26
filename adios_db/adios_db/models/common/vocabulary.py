#!/usr/bin/env python
from pathlib import Path
import csv

# This is the file that contains the allowed vocabulary for the names of
# compounds and industry properties.  We extract the .csv content in the file
# and name it as follows:
filename = (Path(__file__).resolve().parent.parent.parent.parent
            / 'data' / 'compounds_and_industry_properties.csv')

compounds = set()
industry_properties = set()


def read_file_content(filename):
    with open(filename, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile, dialect='excel')
        _labels = next(reader)[:2]  # first row is the column name

        for row in reader:
            compound, prop = row[:2]

            if isinstance(compound, str) and len(compound) > 0:
                compounds.add(compound)

            if isinstance(prop, str) and len(prop) > 0:
                industry_properties.add(prop)


read_file_content(filename)
