#!/usr/bin/env python

"""
This script reads the CSV file:

deleted_records_info.tsv

which was generated from this Excel file:

https://docs.google.com/spreadsheets/d/1_WcJGaq28lcOGVEnlLu6_xDZnE50dNrP/edit?usp=sharing&ouid=112738556987743288660&rtpof=true&sd=true

The data in the CSV file is used to generate an RST file for inclusion in the docs.

"""

# URL Of Record in gitHub
# https://github.com/NOAA-ORR-ERD/noaa-oil-data/blob/Before-Duplicate-Removal/data/oil/AD/AD00009.json
import csv
from pathlib import Path

HERE = Path(__file__).parent

def make_link(oil):
    ID =oil.strip()[:7]
    if ID:
        url = f"https://github.com/NOAA-ORR-ERD/noaa-oil-data/blob/Before-Duplicate-Removal/data/oil/{ID[:2]}/{ID}.json"
        rst = f"`{oil} <{url}>`_"
        return rst
    else:
        return ""

def format_multiple(field):
    # fields = ["| " + f.strip() for f in field.split(";")]
    # fields = [f.strip() for f in field.split(";")]
    fields = [f.strip() for f in field.split(";")]
    fields = [f + '\n' for f in fields]
    return fields


with open(HERE / 'deleted_records_info.tsv') as infile:
    reader = csv.reader(infile, delimiter='\t')
    next(reader)  # skip the header
    data = list(reader)

# make the IDs URLs
for row in data:
    row[0] = make_link(row[0])
# figure out the field lengths
id_length = max([len(r[0]) for r in data])
name_length = max([len(r[1]) for r in data])

# dup_length = max([len(r[5]) for r in data])
dup_length = 20

## write the rst file
header_line = f"{'='*id_length}  {'='*name_length}  {'='*dup_length}\n"
with open(HERE / 'deleted_records_table.rst', 'w') as outfile:
    outfile.write(header_line)
    outfile.write(f"{'Original ID':{id_length}s}   {'Original Name':{name_length}s}  {'Existing Record ID':{dup_length}s}\n")
    outfile.write(header_line)
    for row in data[:]:
        last = format_multiple(row[5])
        outfile.write(f"{row[0]:{id_length}s}  {row[1]:{name_length}s}  {last[0]:s}\n")
        for item in last[1:]:
            outfile.write(f"{'':{id_length}s}  {'':{name_length}s}  {item:s}\n")

    outfile.write(header_line)

# ####
# EXAMPLES OF TABLE FORMAT OPTIONS
# ####

#     outfile.write("""

# +------------------------+------------+----------+----------+
# | Header row, column 1   | Header 2   | Header 3 | Header 4 |
# | (header rows optional) |            |          |          |
# +========================+============+==========+==========+
# | body row 1, column 1   | column 2   | column 3 | column 4 |
# +------------------------+------------+----------+----------+
# | body row 2             | Cells may span columns.          |
# | body row 2             |                                  |
# |                        | Cells may span columns.          |
# | body row 2             |                                  |
# | body row 2             | Cells may span columns.          |
# +------------------------+------------+---------------------+
# | body row 3             | Cells may  | - Table cells       |
# +------------------------+ span rows. | - contain           |
# | body row 4             |            | - body elements.    |
# +------------------------+------------+---------------------+

# """)

#     outfile.write("""

# =====  =====
# col 1  col 2
# =====  =====
# 1      Second column of row 1.
# 2      | Second column of row 2.
#        | Second line of paragraph.
# 3      - Second column of row 3.

#        - Second item in bullet
#          list (row 3, column 2).
# \      Row 4; column 1 will be empty.
# =====  =====
# """)

