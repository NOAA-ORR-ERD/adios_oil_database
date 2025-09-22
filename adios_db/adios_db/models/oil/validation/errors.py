ERRORS = {
    # E01* : meta data related
    "E010": "Record has no oil_id: every record must have an ID",
    "E011": ("Record has invalid oil_id: every record must have a valid ID. "
             "{} is not valid"),
    "E012": "Reference year: {} is not a valid year (between {} and {})",
    "E013": "Review Status: {} is not valid, must be one of {}",
    # E03* -- physical properties related
    "E030": "Oils must have an API",
    "E031": "No Properties data at all",
    "E032": 'Distillation type is "{}", it must be one of: {}',
    "E033": 'Visual Stability is "{}", it must be one of: {}',

    # E04* -- units or values
    "E040": "Value for {}: {} is out of range: unit error?",
    "E041": "Value for {}: {} must be between 0 and 1",
    "E042": "Must have a value for {}",
    "E043": "API, {} does not match density at 60F. API should be: {:.1f}",
#    "E044": "Value: '{}' for '{}' is not valid",
    "E044": "Measurement value: {} is not a valid number for the {} field of a measurement",
    "E045": "Unit: '{}' is not a valid unit for unit type: '{}'. Options are: {}",
    "E046": "A unit must be specified for unit type: '{}'",
    "E047": "A measurement can not have min, max, and value: '{}'",
    "E048": "Missing reference temperature for {} with value: {}",
    "E049": "Missing value for {} with reference temperature: {}",

    # E05* -- duplicates, etc
    "E050": "Duplicate {} in {}",
    "E051": ("Duplicate sub_sample short name(s): {} "
             "Sub_sample short names must be unique"),
    "E052": ("Duplicate sub_sample name(s): {} "
             "names must be unique"),
    # E06* -- dataset error
    "E060": "Oil fraction in distillation cuts is not accumulative",
    "E061": "Boiling points in distillation cuts are not strictly increasing",
    "E062": "Viscosity data is not strictly decreasing with increasing temperature",
    "E063": "Viscosity data has shear rate for some values, but not others",

    # E09* -- system errors
    "E098": "Exception Raised while computing completeness",
    "E099": "Exception Raised while validating"
}

ERRORS = {code: (code + ": " + msg) for code, msg in ERRORS.items()}
