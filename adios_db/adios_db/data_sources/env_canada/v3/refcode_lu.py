#!/usr/bin/env python
from pathlib import Path

import pypdf

import pdb
from pprint import pprint

# This is the file that contains the associations of the reference document
# codes and the full title of the reference document.  It can be downloaded at
# the following URL:
#
# https://data-donnees.ec.gc.ca/data/substances/scientificknowledge/
#       a-catalogue-of-crude-oil-and-oil-product-properties-1999-revised-2022/
#       References-Catalogue_of_Crude_Oil_and_Oil_Product_Properties_(1999)-Revised_2022_En_and_Fr.pdf
filename = (Path(__file__).resolve().parent.parent.parent.parent.parent
            / 'data' / 'env_canada' /
            'References-Catalogue_of_Crude_Oil_and_Oil_Product_Properties_'
            '(1999)-Revised_2022_En_and_Fr.pdf')


def get_pdf_content_lines(filename):
    with open(filename, 'rb') as pdf_file:
        reader = pypdf.PdfReader(pdf_file)

        for i, pg in enumerate(reader.pages):
            # remove the page header
            top_line = 5 if i == 0 else 3
            content = [l.strip() for l in pg.extract_text().split('\n')]

            for l in content[top_line:]:
                yield l


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

for [code, title] in parse_ref_entries(list(get_pdf_content_lines(filename))):
    reference_codes[code] = title
