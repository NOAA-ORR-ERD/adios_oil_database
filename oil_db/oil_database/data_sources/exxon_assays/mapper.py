#!/usr/bin/env python
"""
Exxon Mapper

Not really a class -- it's really a function that build up an
oil object
"""
import logging

import unit_conversion as uc

from oil_database.util import sigfigs
from oil_database.models.oil.oil import Oil
from oil_database.models.oil.sample import Sample, SampleList
from oil_database.models.oil.values import (UnittedValue,
                                            Density,
                                            Viscosity,
                                            DistCut)

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


def norm(string):
    """
    normalizes a string for comparing

    so far: lower case, whitespace strip
    trailing and leading comma strip
    """
    return string.strip().strip(',').lower()


MAPPING = {
    norm("Mercaptan sulfur, ppm"): {
        "attr": "mercaptan_sulfur_mass_fraction",
        "unit": "ppm",
        "num_digits": 4,
        "convert_from": "ppm",
    },
    norm("Carbon, wt %"): {
        "attr": "carbon_mass_fraction",
        "unit": "%",
        "num_digits": 4,
    },
    norm("Hydrogen, wt %"): {
        "attr": "hydrogen_mass_fraction",
        "unit": "%",
        "num_digits": 4,
    },
    norm("Pour point, F"): {
        "attr": "pour_point",
        "unit": "C",
        "convert_from": "F",
    },
    norm("Nitrogen, ppm"): {
        "attr": "nitrogen_mass_fraction",
        "unit": "ppm",
    },
    norm("Neutralization number (TAN), MG/GM"): {
        "attr": "total_acid_number",
        "unit": "mg/kg",
    },
    norm("Sulfur, wt%"): {
        "attr": "sulfur_mass_fraction",
        "unit": "%",
    },
    norm("Reid Vapor Pressure (RVP) Whole Crude, psi"): {
        "attr": "reid_vapor_pressure",
        "unit": "Pa",
        "convert_from": "psi"
    },
    norm("Hydrogen Sulfide (dissolved), ppm"): {
        "attr": "hydrogen_sulfide_concentration",
        "unit": "ppm",
        "convert_from": "ppm"
    },
    norm("Salt content, ptb"): {
        "attr": "salt_content",
        "unit": "ppm",
        "convert_from": "ppb"
    },
    norm("Paraffins, vol %"): {
        "attr": "paraffin_volume_fraction",
        "unit": "%",
        "convert_from": "%"
    },
    norm("Naphthenes, vol %"): {
        "attr": "naphthene_volume_fraction",
        "unit": "%",
        "convert_from": "%"
    },
    norm("Aromatics (FIA), vol %"): {
        "attr": "aromatic_volume_fraction",
        "unit": "%",
        "convert_from": "%"
    },
    norm("CCR, wt%"): {
        "attr": "ccr_percent",
        "unit": "%",
        "convert_from": "%"
    },
    norm("Calcium, ppm"): {
        "attr": "calcium_mass_fraction",
        "unit": "ppm",
        "convert_from": "ppm"
    },
}


def ExxonMapper(record):
    """
    Accepts and Exxon record:

    tuple of:
      - oil name
      - list of lists of the spreadsheet contents

    returns an Oil Object
    """
    name, data = record
    oil = Oil(name)

    data = iter(data)

    read_header(oil, data)
    row = next_non_empty(data)

    oil._id = oil.oil_id = row[0]
    sample_names = row[1:]

    samples = SampleList([Sample(name=name) for name in sample_names])

    cut_table = read_cut_table(oil, data)

    apply_map(data, cut_table, samples)

    process_cut_table(oil, samples, cut_table)

    return oil


def read_header(oil, data):
    # fixme: this should probably be more flexible
    #        but we can wait 'till we get data that doesn't match
    # it could / should read the whole dist cut table, then map it
    # to the samples Exxon info in the header
    oil.reference = "\n".join([next(data)[0] for _ in range(3)])


def read_cut_table(_oil, data):

    cut_table = {}

    while True:
        try:
            row = next_non_empty(data)
            cut_table[norm(row[0])] = row[1:]
        except StopIteration:
            break
    return cut_table


def apply_map(data, cut_table, samples):
    for name, data in MAPPING.items():
        row = cut_table[name]
        set_sample_property(row, samples, **data)


def process_cut_table(oil, samples, cut_table):
    """
    process the parts that aren't a simple map
    """
    # Cut Volume
    # row = get_next_properties_row(data, "Cut volume, %")
    # Dist cuts -- each cut has part of it
    row = cut_table[norm("Cut volume, %")]

    for sample, val in zip(samples, row):
        try:
            sample.cut_volume = UnittedValue(round(val, 4), unit="%")
        except Exception:
            sample.cut_volume = None

    # API -- odd because we only need one!
    row = cut_table[norm("API Gravity,")]

    # pull API from first value
    try:
        oil.api = round(float(row[0]), 1)  # stored as full precision double
    except Exception:
        oil.api = None

    # use specific gravity to get density
    row = cut_table[norm("Specific Gravity (60/60F)")]
    for sample, val in zip(samples, row):
        try:
            rho = uc.convert("SG", "g/cm^3", val)
            sample.densities.append(
                Density(UnittedValue(round(rho, 8), unit="g/cm^3"),
                        UnittedValue(15.6, unit="C"))
            )
        except Exception:
            pass

    # viscosity
    # fixme: -- maybe should parse the labels for temp, etc?
    #          wait till next version
    for lbl in ("Viscosity at 20C/68F, cSt",
                "Viscosity at 40C/104F, cSt",
                "Viscosity at 50C/122F, cSt"):
        row = cut_table[norm(lbl)]
        for sample, val in zip(samples, row):
            try:
                sample.kvis.append(Viscosity(UnittedValue(round(val, 8),
                                                          unit="cSt"),
                                             UnittedValue(40,
                                                          unit="C")))
            except Exception:
                pass

    # distillation data
    if norm("Distillation type, TBP") not in cut_table:
        raise ValueError("I don't recognise this distillation data. \n"
                         'Expected: "Distillation type, TBP"')
    for name, row in cut_table.items():
        if norm("vol%, F") in name or name == norm("IBP, F"):
            # looks like a distillation cut.
            percent = 0.0 if "ibp" in name else float(name.split("vol")[0])

            for sample, val in zip(samples, row):
                if val is not None:
                    val = sigfigs(uc.convert("F", "C", val), 5)
                    sample.cuts.append(
                        DistCut(UnittedValue(percent, unit="%"),
                                UnittedValue(val, unit="C")
                                ))
    # sort them
    for sample in samples:
        sample.cuts.sort(key=lambda c: c.fraction.value)

    # "nitrogen_mass_fraction: UnittedValue"
    # "reid_vapor_pressure: UnittedValue"
    # "hydrogen_sulfide_concentration"

    oil.samples = samples

    return oil


def set_sample_property(row,
                        samples,
                        attr,
                        unit,
                        num_digits=4,
                        convert_from=None):
    """
    reads a row from the spreadsheet, and sets the sample properties

    optional rounding to "num_digits" digits
    optional converting to unit from convert_from (if the the data aren't in
    the right units)
    """
    for sample, val in zip(samples, row):
        if val is not None and val not in ('NotAvailable',):
            if convert_from is not None:
                val = uc.convert(convert_from, unit, val)

            val = sigfigs(val, num_digits)
            setattr(sample, attr, UnittedValue(val, unit=unit))


# Utilities:
def next_non_empty(data):
    while True:
        row = next(data)
        if not is_empty(row):
            break
    return row


def is_empty(row):
    return all([f is None for f in row])


def get_next_properties_row(data, exp_field):
    row = next_non_empty(data)
    if norm(row[0]) != norm(exp_field):
        raise ValueError(f'Something wrong with data sheet: {row}, '
                         'expected: {exp_field}')
    return row
