"""
warnings.py

All the warnings
"""

# FIXME: it would be better to have some structure to he warning codes
WARNINGS = {
    # metdata warnings:
    "W001": "Record name: {} is not very descriptive",
    "W002": "Record has no product type",
    "W003": '"{}" is not a valid product type. Options are: {}',
    "W004": "No api value provided",
    "W005": "API value: {api} seems unlikely",
    "W008": "No reference year provided",
    "W012": 'Location: "{}" in wrong order. Should be: "{}"',

    # missing data warnings
    "W006": "No density values provided",
    "W007": "No distillation data provided",
    "W009": "Distillation fraction recovered is missing or invalid",

    # data integrity:
    "W010": ("Temperature: {} is close to {} -- looks like it could be a "
             "K to C conversion error"),
    "W011": "{} date format: {} is invalid: {}",
    "W013": "Oil fraction in distillation cuts has duplicate entries",
    "W014": 'Non-simple value: "{}" for {}',
    "W015": "Viscosity data has shear rate for some values, but not others",

    # NOAA specific
    "W100": ("Not GNOME compatible: {}"),

}

WARNINGS = {code: (code + ": " + msg) for code, msg in WARNINGS.items()}
