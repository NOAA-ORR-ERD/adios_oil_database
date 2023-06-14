#!/usr/bin/env python
from pathlib import Path

# This is the file that contains the associations of the reference document
# codes and the full title of the reference document.  It can be downloaded at
# the following URL:
#
# https://data-donnees.ec.gc.ca/data/substances/scientificknowledge/
#       a-catalogue-of-crude-oil-and-oil-product-properties-1999-revised-2022/
#       References-Catalogue_of_Crude_Oil_and_Oil_Product_Properties_(1999)-Revised_2022_En_and_Fr.pdf
#
# We extract the text content in the file and name it as follows:
filename = (Path(__file__).resolve().parent.parent.parent.parent.parent
            / 'data' / 'env_canada' /
            'References-Catalogue_of_Crude_Oil_and_Oil_Product_Properties_'
            '(1999)-Revised_2022_En_and_Fr.txt')


def get_text_content_lines(filename):
    with open(filename, 'r') as text_file:
        for line in text_file.readlines():
            yield line.rstrip()


def parse_ref_entries(bufflines):
    """
    Method for parsing the lines of text in the reference codes document from
    the organization: Environment and Climate Change Canada
    """
    entry = []
    for line in bufflines:
        if line == '':
            pass
        elif (line.endswith('.')
                and not line[-4:] == 'R.G.'
                and not line[-9:] == 'Environm.'
                and not line[-3:] == 'pp.'):
            # We reached the end of our title
            # Note: This can't be parsed exactly.  When deciding when a title
            #       ends, there is no consistent pattern to work with.
            #       Basically every title seems to reliably end with a period,
            #       but there were a few edge cases we needed to add because
            #       the title was split on an abbreviated word.  I imagine this
            #       could change with any change in the content of the file.
            entry.append(line[:-1])
            yield [entry[0], ' '.join(entry[1:])]
            entry.clear()
        else:
            entry.append(line)


reference_codes = {}

for [code, title] in parse_ref_entries(get_text_content_lines(filename)):
    reference_codes[code] = title
