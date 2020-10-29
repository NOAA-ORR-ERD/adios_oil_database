'''
    Calculate the completeness of the data contained in an oil record.

    The top-level interface is a single function:
        completeness(pyjson_of_an_oil_record)

    (pyjson is a python dict that is a match for the JSON)

    It performs calculations that were designed by RobertJ, and returns a value
    with a scale of 0->100%.
'''
import logging

from ..common.measurement import MassFraction, Temperature

logger = logging.getLogger(__name__)


def completeness(oil_json):
    '''
        Calculate the completeness of the data contained in an oil record.

        :param oil: The oil record to be validated, in json-compatible python
                    data structure.
    '''
    res = 0

    for check_func in CHECKS:
        res += check_func(oil_json)

    return res * 10.0


def check_emulsion_water_content(oil_json):
    '''
        One emulsion water content in any subsample. Score = 2.5
    '''
    sub_samples = oil_json.get('sub_samples', [])

    for sample in sub_samples:
        emuls = sample.get('environmental_behavior', {}).get('emulsions', [])
        for e in emuls:
            if (is_measurement_good(e)):
                return 2.5  # only need one valid emulsion

    return 0.0


def check_density(oil_json):
    '''
        Fresh oil: One density or API. Score = 1
    '''
    api = oil_json.get('metadata', {}).get('API', None)

    if api is not None:
        return 1.0

    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 0:
        ss = sub_samples[0]
        densities = ss.get('physical_properties', {}).get('densities', [])

        for d in densities:
            if (is_measurement_good(d.get('density', {})) and
                    is_measurement_good(d.get('ref_temp', {}))):
                return 1.0

    return 0.0


def check_second_density(oil_json):
    '''
        Fresh oil: Second density separated by temperature.
                   Score = deltaT/40 but not greater than 0.5
                   - maxDeltaT: The difference between the lowest and highest
                                measurement in the set.
    '''
    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 0:
        ss = sub_samples[0]
        densities = ss.get('physical_properties', {}).get('densities', [])

        temps = [(Temperature
                  .from_py_json(d.get('ref_temp', {}))
                  .convert_to('C').value)
                 for d in densities]

        if len(temps) >= 2:
            t1, *_, t2 = sorted([t for t in temps if t is not None])
            delta_t = t2 - t1

            if delta_t > 0.0:
                return min(delta_t / 40.0, 0.5)

    return 0.0


def check_viscosity(oil_json):
    '''
        Fresh oil: One viscosity. Score = 0.5
    '''
    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 0:
        ss = sub_samples[0]
        kvis = (ss.get('physical_properties', {})
                .get('kinematic_viscosities', []))
        dvis = (ss.get('physical_properties', {})
                .get('dynamic_viscosities', []))

        for v in kvis:
            if (is_measurement_good(v.get('viscosity', {})) and
                    is_measurement_good(v.get('ref_temp', {}))):
                return 0.5

        for v in dvis:
            if (is_measurement_good(v.get('viscosity', {})) and
                    is_measurement_good(v.get('ref_temp', {}))):
                return 0.5

    return 0.0


def check_second_viscosity(oil_json):
    '''
        Fresh oil: Second viscosity at a different temperature.
                   Score = maxDeltaT/40, but not greater than 0.5
                   - maxDeltaT: The difference between the lowest and highest
                                measurement in the set.
    '''
    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 0:
        ss = sub_samples[0]
        kvis = (ss.get('physical_properties', {})
                .get('kinematic_viscosities', []))
        dvis = (ss.get('physical_properties', {})
                .get('dynamic_viscosities', []))

        temps = []
        for v_i in (kvis, dvis):
            temps.extend([(Temperature
                           .from_py_json(v.get('ref_temp', {}))
                           .convert_to('C').value)
                          for v in v_i])

        if len(temps) >= 2:
            t1, *_, t2 = sorted([t for t in temps if t is not None])
            delta_t = t2 - t1

            if delta_t > 0.0:
                return min(delta_t / 40.0, 0.5)

    return 0.0


def check_distillation(oil_json):
    '''
        Fresh oil: Two Distillation cuts separated by mass or volume fraction.
                   Score = 3 * maxDeltaFraction
                   - maxDeltaFraction: The difference between the lowest and
                                       highest measurement in the set
    '''
    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 0:
        ss = sub_samples[0]
        cuts = ss.get('distillation_data', {}).get('cuts', [])

        fractions = [(MassFraction
                      .from_py_json(c.get('fraction', {}))
                      .convert_to('fraction').value)
                     for c in cuts]

        if len(fractions) >= 2:
            f1, *_, f2 = sorted([f for f in fractions if f is not None])

            return 3.0 * (f2 - f1)

    return 0.0


def check_weathered_density(oil_json):
    '''
        One Weathered oil: Density. Score = 1
    '''
    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 1:
        ss = sub_samples[1]
        densities = ss.get('physical_properties', {}).get('densities', [])

        if (len(densities) > 0 and
                is_measurement_good(densities[0].get('density', {})) and
                is_measurement_good(densities[0].get('ref_temp', {}))):
            return 1.0

    return 0.0


def check_weathered_viscosity(oil_json):
    '''
        One Weathered oil: Viscosity. Score = 1
    '''
    sub_samples = oil_json.get('sub_samples', [])

    if len(sub_samples) > 1:
        ss = sub_samples[1]
        kvis = (ss.get('physical_properties', {})
                .get('kinematic_viscosities', []))
        dvis = (ss.get('physical_properties', {})
                .get('dynamic_viscosities', []))

        if (len(kvis) > 0 and
                is_measurement_good(kvis[0].get('viscosity', {})) and
                is_measurement_good(kvis[0].get('ref_temp', {}))):
            return 1.0

        if (len(dvis) > 0 and
                is_measurement_good(dvis[0].get('viscosity', {})) and
                is_measurement_good(dvis[0].get('ref_temp', {}))):
            return 1.0

    return 0.0


def is_measurement_good(measurement):
    return not any([(a not in measurement)
                    for a in ('value', 'unit', 'unit_type')])


# build a list of all the check function:
CHECKS = [val for name, val in vars().items() if name.startswith("check_")]
