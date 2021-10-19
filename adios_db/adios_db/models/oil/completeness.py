'''
Calculate the completeness of the data contained in an oil record.

The top-level interface is a single function:
    completeness(oil)

Where oil is an oil record

It performs calculations that were designed by Robert Jones,
and returns a value with a scale of 0->100

As of June 2021, these were the criteria:

The scores should be normalized by total possible score.

One emulsion water content in any subsample. Score = 2.5

Fresh oil:
  One density. Score = 1

  Second density separated by temperature.
    Score = deltaT/40 but not greater than 0.5

  One viscosity. Score = 0.5

  Second viscosity at a different temperature.
    Score = maxDeltaT/40, but not greater than 0.5

Two Distillation cuts separated by mass or volume fraction.  Score = 3*maxDeltaFraction
  Fraction recovered =1.  Score = 2.
  Fraction recovered <1. Score = 1.

One Weathered oil:
  Density. Score = 1
  Viscosity. Score = 1
'''

# FixMe: These classes could be merged to make them a bit less redundant.

import logging

from .oil import Oil

# from ..common.measurement import MassFraction, Temperature

logger = logging.getLogger(__name__)


# this gets calculated later
# used to normalize the score
MAX_SCORE = None

# is this function needed???
# answer: SRP, it's the right thing to do
def set_completeness(oil):
    oil.metadata.model_completeness = completeness(oil)


def completeness(oil):
    '''
    Calculate the completeness of the data contained in an oil record.

    :param oil: The oil record to be validated
    '''
    score = 0
    for check_func in CHECKS:
        score += check_func(oil)

    return round(score / MAX_SCORE * 100)


class Check_emulsion_water_content:

    max_score = 2.5

    def __call__(self, oil):
#       def check_emulsion_water_content(oil):
        '''
        One emulsion water content in any subsample. Score = 2.5
        '''
        sub_samples = oil.sub_samples

        for sample in sub_samples:
            emuls = sample.environmental_behavior.emulsions
            for e in emuls:
                if (is_measurement_good(e.water_content)):
                    return 2.5  # only need one valid emulsion water content

        return 0.0
# check_emulsion_water_content = Check_emulsion_water_content()

# def check_density(oil):

class Check_density:
    '''
    Fresh oil: One density Score = 1
    '''
    max_score = 1.0

    def __call__(self, oil):

        if len(oil.sub_samples) > 0:
            ss = oil.sub_samples[0]
            densities = ss.physical_properties.densities
            for d in densities:
                if (is_measurement_good(d.density) and
                        is_measurement_good(d.ref_temp)):
                    return 1.0
        return 0.0


class Check_second_density:
    '''
    Fresh oil: One density Score = 0.5
    '''
    max_score = 0.5

    def __call__(self, oil):
        '''
        Fresh oil: Second density separated by temperature.

        Score = deltaT/40 but not greater than 0.5

        maxDeltaT: The difference between the lowest and highest
        measurement in the set.
        '''
        if len(oil.sub_samples) > 0:
            ss = oil.sub_samples[0]
            densities = ss.physical_properties.densities
            temps = [d.ref_temp.converted_to('C').value
                     for d in densities
                     if d.ref_temp is not None]

            if len(temps) >= 2:
                t1, *_, t2 = sorted([t for t in temps if t is not None])
                delta_t = t2 - t1

                if delta_t > 0.0:
                    return min(delta_t / 40.0, 0.5)

        return 0.0


class Check_viscosity:

    max_score = 0.5

    def __call__(self, oil):
        '''
        Fresh oil: One viscosity. Score = 0.5
        '''
        if len(oil.sub_samples) > 0:
            ss = oil.sub_samples[0]
            kvis = ss.physical_properties.kinematic_viscosities
            dvis = ss.physical_properties.dynamic_viscosities

            for v in kvis:
                if (is_measurement_good(v.viscosity)
                        and is_measurement_good(v.ref_temp)):
                    return 0.5

            for v in dvis:
                if (is_measurement_good(v.viscosity)
                        and is_measurement_good(v.ref_temp)):
                    return 0.5

        return 0.0


class Check_second_viscosity:

    max_score = 0.5

    def __call__(self, oil):
        '''
        Fresh oil: Second viscosity at a different temperature.

        Score = maxDeltaT/40, but not greater than 0.5

        maxDeltaT: The difference between the lowest and highest
        measurement in the set.
        '''
        if len(oil.sub_samples) > 0:
            ss = oil.sub_samples[0]
            kvis = ss.physical_properties.kinematic_viscosities
            dvis = ss.physical_properties.dynamic_viscosities

            temps = []
            for v_i in (kvis, dvis):
                temps.extend([v.ref_temp.converted_to('C').value
                              for v in v_i
                              if v.ref_temp is not None])

            if len(temps) >= 2:
                t1, *_, t2 = sorted([t for t in temps if t is not None])
                delta_t = t2 - t1

                if delta_t > 0.0:
                    return min(delta_t / 40.0, 0.5)

        return 0.0


class Check_distillation:

    max_score = 6

    def __call__(self, oil):
        '''
        Two Distillation cuts separated by mass or volume fraction.
          Score = 3*maxDeltaFraction

        Fraction recovered =1.  Score = 2.
        Fraction recovered <1. Score = 1.

        '''
        score = 0.0
        if len(oil.sub_samples) > 0:
            dist_data = oil.sub_samples[0].distillation_data
            cuts = dist_data.cuts

            fractions = [c.fraction.converted_to('fraction').value for c in cuts]

            if len(fractions) >= 2:
                fractions = sorted((f for f in fractions if f is not None))

                score = 3.0 * (fractions[-1] - fractions[0])

            if dist_data.fraction_recovered is None:
                pass
            elif dist_data.fraction_recovered == 1.0:
                score += 2.0
            elif dist_data.fraction_recovered < 1.0:
                score += 1.0
        return score


def get_evaporated_subsample(oil):
    """
    return the first evaporated sub_sample if there is one:
    """
    for ss in oil.sub_samples:
        if ss.metadata.fraction_evaporated is None:
            continue
        fe = ss.metadata.fraction_evaporated.converted_to('fraction').value
        if 0 < fe < 1.0:
            return ss
    return None


class Check_weathered_density:

    max_score = 1

    def __call__(self, oil):
        '''
        One Evaporated oil: Density. Score = 1
        '''
        ss = get_evaporated_subsample(oil)
        if ss is not None:
            densities = ss.physical_properties.densities

            if (len(densities) > 0
                    and is_measurement_good(densities[0].density)
                    and is_measurement_good(densities[0].ref_temp)):
                return 1.0

        return 0.0


class Check_weathered_viscosity:

    max_score = 1

    def __call__(self, oil):
        '''
            One Evaporated oil: Viscosity. Score = 1
        '''
        ss = get_evaporated_subsample(oil)
        if ss is not None:
            kvis = ss.physical_properties.kinematic_viscosities
            dvis = ss.physical_properties.dynamic_viscosities

            if (len(kvis) > 0
                    and is_measurement_good(kvis[0].viscosity)
                    and is_measurement_good(kvis[0].ref_temp)):
                return 1.0

            if (len(dvis) > 0
                    and is_measurement_good(dvis[0].viscosity)
                    and is_measurement_good(dvis[0].ref_temp)):
                return 1.0

        return 0.0


def is_measurement_good(measurement):
    return not any([(getattr(measurement, a, None) is None)
                    for a in ('value', 'unit', 'unit_type')])


# build a list of all the check function:
CHECKS = [val() for name, val in vars().items() if name.startswith("Check_")]

# compute the max possible score:
MAX_SCORE = sum(check.max_score for check in CHECKS)

