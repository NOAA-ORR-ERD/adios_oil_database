#!/usr/bin/env python

"""
This script reads the CSV file:

deleted_records_info.tsv

which was generated from this Excel file:

https://docs.google.com/spreadsheets/d/1_WcJGaq28lcOGVEnlLu6_xDZnE50dNrP/edit?usp=sharing&ouid=112738556987743288660&rtpof=true&sd=true

The data in the CSV file is used to generate an RST file for inclusion in teh docs.

"""
import csv
from pathlib import Path

HERE = Path(__file__).parent

print(HERE)

with open(HERE / 'deleted_records_info.tsv') as infile:
    reader = csv.reader(infile, delimiter='\t')
    next(reader)  # skip the header
    data = list(reader)

# figure out the field lengths
name_length = max([len(r[1]) for r in data])
dup_length = max([len(r[5]) for r in data])

print("Longest name:", name_length)

## write the rst file
header_line = f"============  {'='*name_length}  {'='*dup_length}\n"
with open(HERE / 'deleted_records_table.rst', 'w') as outfile:
    outfile.write(header_line)
    outfile.write(f"Original ID   {'Original Name':{name_length}s}  {'Existing Record ID':{dup_length}s}\n")
    outfile.write(header_line)
    for row in data[:100]:
        print(row)
        outfile.write(f"{row[0]:12s}  {row[1]:{name_length}s}  {row[5]:s}\n")

    outfile.write(header_line)

## write the rst file
"""
+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+---------------------+
| body row 3             | Cells may  | - Table cells       |
+------------------------+ span rows. | - contain           |
| body row 4             |            | - body elements.    |
+------------------------+------------+---------------------+
"""
# name_length += 2
# dup_length += 2

# header_line = f"+{'-' * 8}+{'-' * (name_length)}+{'-' * (dup_length)}\n"
# with open(HERE / 'deleted_records_table.rst', 'w') as outfile:
#     outfile.write(header_line)
#     outfile.write(f"Original ID   {'Original Name':{name_length}s}  {'Existing Record ID':{dup_length}s}\n")
#     outfile.write(header_line.replace('-', '='))
#     for row in data[10]:
#         outfile.write(f"{row[0]:12s}  {row[1]:{name_length}s}  {row[5]:}\n")

#     outfile.write(header_line)
