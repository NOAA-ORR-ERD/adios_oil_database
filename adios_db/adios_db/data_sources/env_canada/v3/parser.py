#!/usr/bin/env python
import re
import logging
from datetime import datetime
from dataclasses import dataclass, fields

from numpy import isclose

# fixme: you really shouldn't need to import UNIT_TYPES or ConvertDataUnits
#        the functionality should be in nucos already.
#        the latest version (not yet released) does have MassFraction
#        and VolumeFraction units available for getting unit type.
#        GetUnitNames and GetUnitAbbreviation should help
#        If anything else is missing, we should add it there.
from nucos.unit_conversion import ConvertDataUnits, Simplify, UNIT_TYPES

from adios_db.util import sigfigs
from adios_db.data_sources.parser import ParserBase
from adios_db.data_sources.importer_base import parse_single_datetime


logger = logging.getLogger(__name__)

UNIT_TYPES_MV = {}

for u_type in ('Volume Fraction', 'Mass Fraction'):
    # UNIT_TYPES does not include mass/volume fraction units, so we need to
    # make our own lookup table.
    # Almost every unit in these two types is common, so we need to make a
    # preference for one or the other, and we will prefer mass fraction types.
    #
    # probably no longer needed with latest nucos
    # Also: why not add to (a copy of) the UNIT_TYPES dict?
    u_dict = {u: u_type.lower().replace(' ', '')
              for u in set([i for sub in [([k] + v[1])
                                          for k, v
                                          in ConvertDataUnits[u_type].items()]
                            for i in sub])}
    UNIT_TYPES_MV.update(u_dict)


@dataclass
class ECMeasurementDataclass:
    """
    An incoming density will have the attributes:
    - value
    - unit_of_measure
    - temperature
    - condition_of_analysis
    - standard_deviation
    - replicates
    - method

    We will output an object with the attributes:
    - measurement (Measurement type)
    - method
    - ref_temp (Temperature Measurement type)
    """
    property_group: str = None
    property_name: str = None
    value: float = None
    min_value: float = None
    max_value: float = None
    unit_of_measure: str = None
    temperature: str = None
    condition_of_analysis: str = None
    standard_deviation: float = None
    replicates: float = None
    method: str = None

    def __post_init__(self):
        self.treat_any_bad_initial_values()
        self.fix_value_if_min_max()
        self.parse_temperature_string()
        self.fix_unit()
        self.determine_unit_type()

    def treat_any_bad_initial_values(self):
        for f in fields(self.__class__):
            if getattr(self, f.name) in ('N/A', 'NM', 'DNF', ''):
                setattr(self, f.name, None)

    def fix_value_if_min_max(self):
        """
        There are cases where our self.value contains a string indicating an
        interval representing a min-max.  If this is the case, fix it by
        splitting it into the self.min_value & self.max_values.

        There are a lot of various ways the interval data is represented in the
        datasheet, so here are the cases I have found:

        - Case 'N-N': Split on the '-'.  This makes it ambiguous whether the
                      second number is negative or not, but we accept
                      the data as it comes in from the data sheet.
        - Case 'N-N-N': Split on the '-'.  Take the first two items.
        - Case 'N - N': Split on the '-'. Ignore the spaces.
        - Case 'N to N': Split on the 'to'.  Ignore the spaces.
        - Case 'N, N': Split on the ','.  Ignore the spaces.

        - Case '-N': Single negative number, don't do anything.
        - Case '>N': min_value = N, max_value = None
        - Case '<N': min_value = None, max_value = N
        - Case 'N (min.)': min_value = N
        - Case 'N (max.)': max_value = N
        - Case 'N1 (min.), N2 (max.)': Split on the ','.
                                       min_value = N1, max_value = N2
        - Case 'min N1, max N2': Split on the ','.
                                 min_value = N1, max_value = N2
        """
        if isinstance(self.value, (int, float, type(None))):
            return  # nothing to do, it's already a number

        # take care of the easy cases first
        for separator in (' to ', ', ', ' - '):
            items = self.value.split(separator)
            if len(items) > 1:
                # we have a couple of possible numbers to make a range with.
                try:
                    self.set_ranged_values(*items)
                except ValueError:
                    pass

                return

        if self.value[0] in ('>', '≥'):
            # set min value
            self.set_ranged_values(self.value[1:], None)
            return

        if self.value[0] in ('<', '≤'):
            # set max value
            self.set_ranged_values(None, self.value[1:])
            return

        # take care of the case of dashes without spaces
        items = self.split_value_on_nospace_dashes()
        if items is not None and len(items) > 1:
            # we have a couple of numbers to make a range with.
            self.set_ranged_values(*items)
            return

        self.set_value(self.value)

    def set_value(self, value):
        if isinstance(value, (int, float, type(None))):
            self.value = value
        elif any([b in value for b in ('(min', '(max')]):
            # The value has a min or max annotation.
            match_obj = re.search(r'([-\.\d]+) \((min|max).\)', value)
            if match_obj is not None:
                num_val, min_max = (match_obj.groups())

                if min_max == 'min':
                    self.min_value = float(num_val)
                else:
                    self.max_value = float(num_val)
        else:
            try:
                self.value = float(value)
            except ValueError:
                # logger.warning(f'{self.property_group}.{self.property_name}:'
                #                f'\tCould not set value ({value}) to float.')
                self.value = value

    def set_ranged_values(self, min_value, max_value, *args):
        """
        - each value passed in is part of a min/max interval.
        - There are also a few cases where the min/max quality of the value
          is annotated with a ' (min.)' or a ' (max.)' suffix.
        """
        # process our min_value
        if isinstance(min_value, (int, float, type(None))):
            self.min_value = min_value
            self.value = self.max_value = None
        elif any([b in min_value for b in ('min', 'max')]):
            # Yeah, the min_value could have a min or max annotation.
            match_obj = re.search(r'([-\.\d]+) \((min|max).\)', min_value)
            if match_obj is not None:
                num_val, min_max = (match_obj.groups())
            else:
                match_obj = re.search(r'(min|max) ([-\.\d]+)', min_value)

                if match_obj is not None:
                    min_max, num_val = (match_obj.groups())

            if min_max == 'min':
                self.min_value = float(num_val)
            else:
                self.max_value = float(num_val)

            self.value = self.max_value = None
        else:
            self.min_value = float(min_value)
            self.value = self.max_value = None

        # process our max_value
        if isinstance(max_value, (int, float, type(None))):
            self.max_value = max_value
            self.value = self.min_value = None
        elif any([b in max_value for b in ('min', 'max')]):
            # Yeah, the max_value could have a min or max annotation.
            match_obj = re.search(r'([-\.\d]+) \((min|max).\)', max_value)
            if match_obj is not None:
                num_val, min_max = (match_obj.groups())
            else:
                match_obj = re.search(r'(min|max) ([-\.\d]+)', max_value)

                if match_obj is not None:
                    min_max, num_val = (match_obj.groups())

            if min_max == 'min':
                self.min_value = float(num_val)
            else:
                self.max_value = float(num_val)

            self.value = self.min_value = None
        else:
            self.max_value = float(max_value)
            self.value = self.min_value = None

    def split_value_on_nospace_dashes(self):
        """
        cases like 'N-N' and 'N-N-N' are problematic when parsed by regex
        because the '-' character is also used as a sign indicator for
        the numbers.

        A possible algorithm is to split the string on all dashes, and the
        empty items in our resulting list will indicate a dash was used
        as a sign character.

        Ex. '5-4'   -> ['5', '4']

        Ex. '-5--4' -> ['', '5', '', '4']
                         ^        ^
                        sign     sign
        Note: We will not try to turn these items into float values here, but
              we would like them to be numeric.  Otherwise, we don't have an
              interval.
        """
        ret = []
        separated = self.value.split('-')
        separated.reverse()

        try:
            [float(i) for i in separated if i != '']
        except ValueError:
            # logger.warning(f'Non-numeric sub-values found: "{self.value}"')
            return None

        if separated[0] == '':
            logger.warning(f'Badly formed value: "{self.value}"')
            return None
        else:
            for i in separated:
                if i == '':
                    if ret[-1][0] == '-':
                        ret[-1] = ret[-1][1:]
                    else:
                        ret[-1] = '-' + ret[-1]
                else:
                    ret.append(i.strip())

        ret.reverse()
        return ret[:2]

    def parse_temperature_string(self):
        """
        The temperature field can have varying content, like '15 °C'
        or simply '15', in which case we will assume it is Celsius.
        """
        if (isinstance(self.temperature, str)
                and self.temperature.lower() == 'unknown'):
            self.ref_temp = None
            self.ref_temp_unit = None
        elif isinstance(self.temperature, str) and len(self.temperature) > 0:

            match_obj = re.search(r'(\d+)[^a-zA-Z]+([a-zA-Z]+)',
                                  self.temperature)

            if match_obj is not None:
                self.ref_temp, *_, self.ref_temp_unit = match_obj.groups()
                self.ref_temp = float(self.ref_temp)
            else:
                self.ref_temp = None
                self.ref_temp_unit = None
        elif isinstance(self.temperature, (int, float)):
            self.ref_temp = self.temperature
            self.ref_temp_unit = 'C'
        else:
            self.ref_temp = None
            self.ref_temp_unit = None

    def fix_unit(self):
        """
        Some units are in the form 'X or Y'.  We will just choose the
        first one.

        Temperature units (e.g. '°C') need to be stripped of the degree
        character

        Illegible unicode for '^2' needs to be corrected.
        """
        if self.unit_of_measure:
            unit = self.unit_of_measure.split(' or ')[0]
            unit = (unit.lstrip('°').lstrip('⁰').lstrip(' ̊')
                    .lstrip('¬∞').lstrip('‚Å∞').lstrip('Ãä')
                    .lstrip('â•'))

            unit = unit.replace('¬≤', '^2').replace('²', '^2')

            self.unit_of_measure = unit

    def determine_unit_type(self):
        # check if it is a mass/volume fraction.
        # - until PyNUCOS accepts a unit of measure like '% w/w' or '% v/v',
        #   we need to change it to '%' and set the unit type explicitly
        if self.unit_of_measure is None:
            self.unit_type = 'unitless'
            return
        elif self.unit_of_measure in ('% w/w', '%w/w'):
            self.unit_of_measure = '%'
            self.unit_type = 'massfraction'
            return
        elif self.unit_of_measure in ('% v/v', '%v/v'):
            self.unit_of_measure = '%'
            self.unit_type = 'volumefraction'
            return
        elif self.unit_of_measure == 'g/m2':
            self.unit_of_measure = 'g/m^2'
            self.unit_type = None
            return

        # handle saybolt viscosity unit string
        if ('saybolt' in self.unit_of_measure.lower() or
                'sus' in self.unit_of_measure.lower()):
            self.unit_of_measure = 'sus'

        unit = Simplify(self.unit_of_measure)

        try:
            self.unit_type = UNIT_TYPES[unit]
        except KeyError:
            try:
                self.unit_type = UNIT_TYPES_MV[unit]
            except KeyError:
                self.unit_type = None


class ECMeasurement(ECMeasurementDataclass):
    value_attr = 'measurement'
    ref_temp_attr = 'ref_temp'

    @classmethod
    def from_obj(cls, obj):
        class_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in obj.items() if k in class_fields})

    def py_json(self):
        ret = {
            self.value_attr: {
                'unit': self.unit_of_measure,
                'unit_type': self.unit_type,
            },
        }

        # only set these values if they are not None
        if self.standard_deviation is not None:
            ret[self.value_attr]['standard_deviation'] = self.standard_deviation

        if self.replicates is not None:
            ret[self.value_attr]['replicates'] = self.replicates

        if self.method is not None:
            ret['method'] = self.method

        if self.min_value is not None or self.max_value is not None:
            ret[self.value_attr]['min_value'] = self.min_value
            ret[self.value_attr]['max_value'] = self.max_value
        else:
            ret[self.value_attr]['value'] = self.value

        if self.ref_temp is not None:
            ret[self.ref_temp_attr] = {
                'value': self.ref_temp,
                'unit': self.ref_temp_unit,
                'unit_type': 'temperature',
            }

        return ret


class ECValueOnly(ECMeasurement):
    def py_json(self):
        ret = super().py_json()

        ret.pop(self.ref_temp_attr, None)

        return ret


class ECDensity(ECMeasurement):
    value_attr = 'density'

    def __post_init__(self):
        if self.unit_of_measure == 'N/A':
            # For ECCC, I think we can default to g/mL on the few cases where
            # we don't have a good unit of measure for density.
            self.unit_of_measure = 'g/mL'

        super().__post_init__()


class ECViscosity(ECMeasurement):
    value_attr = 'viscosity'

    def py_json(self):
        """
        What do we do when the value is 'Too Viscous'?
        """
        ret = super().py_json()

        try:
            value, unit = self.condition_of_analysis.split()[-2:]
        except AttributeError:
            value, unit = None, None

        if unit == '1/s':
            try:
                value = float(value.split('=')[1])
            except IndexError:
                value = float(value)

            ret['shear_rate'] = {'value': value, 'unit': unit,
                                 'unit_type': 'angularvelocity'}

        return ret


class ECInterfacialTension(ECMeasurement):
    value_attr = 'tension'

    def py_json(self):
        """
        What do we do when the value is 'Too Viscous'?
        """
        ret = super().py_json()

        if 'oil/salt water' in self.condition_of_analysis.lower():
            ret['interface'] = 'seawater'
        elif 'oil/ air' in self.condition_of_analysis.lower():
            ret['interface'] = 'air'
        else:
            ret['interface'] = 'water'

        return ret


class ECAdhesion(ECValueOnly):
    value_attr = 'adhesion'


class BPTemperatureDistribution(ECMeasurement):
    value_attr = 'fraction'
    ref_temp_attr = 'vapor_temp'
    final_bp = False

    def __post_init__(self):
        super().__post_init__()

        # For this type, we need to swap value into temperature
        # Convert it to float if we can, otherwise just use whatever is there
        # - There are some records that have min-max values which get converted
        #   to self.min_value & self.max_value, but for this type of
        #   measurement, we really need just a single temperature.
        try:
            self.ref_temp = None if self.value is None else float(self.value)
        except (TypeError, ValueError):
            # Sometimes there is a 'N (max.)' or 'N (min.)' value.
            # in this the case, for distillation, we will just take the value
            match_obj = re.search(r'([-\.\d]+) \((min\.|max\.|estimated)\)',
                                  self.value)
            if match_obj is not None:
                num_val, min_max = (match_obj.groups())

                if min_max == 'min':
                    self.min_value = float(num_val)
                else:
                    self.max_value = float(num_val)
            else:
                self.ref_temp = self.value

        self.ref_temp_unit = self.unit_of_measure

        # for this type, we need to take the property name as the fraction
        if self.condition_of_analysis.lower() == 'initial boiling point':
            self.value = 0.0
        elif self.condition_of_analysis.lower() == 'final boiling point':
            self.value = 100.0
            self.final_bp = True
        else:
            self.value = float(self.condition_of_analysis
                               .split('%')[0].strip())

        self.min_value = self.max_value = None
        self.unit_type = 'massfraction'
        self.unit_of_measure = '%'

    def py_json(self):
        ret = super().py_json()

        if self.final_bp:
            ret['final_bp'] = self.final_bp

        return ret


class BPCumulativeWeightFraction(ECMeasurement):
    value_attr = 'fraction'
    ref_temp_attr = 'vapor_temp'


class ECEvaporationEq(ECMeasurement):
    def py_json(self):
        ret = super().py_json()
        ret['equation'] = self.property_name
        ret['measurement'] = ret['measurement']['value']

        return ret


class ECEmulsion(ECMeasurement):
    def py_json(self):
        ret = super().py_json()

        try:
            condition = self.condition_of_analysis.lower()
            if condition == 'one week after formation':
                ret['age'] = {'unit': 'day', 'unit_type': 'time', 'value': 7}
            elif condition == 'on the day of formation':
                ret['age'] = {'unit': 'day', 'unit_type': 'time', 'value': 0}
            else:
                logger.warning('ECEmulsion: Can not determine emulsion age')
        except AttributeError:
            # We already have a validation method for emulsion.  If we want to
            # check for age, we can do it there.
            # logger.warning('ECEmulsion: Condition of Analysis not set')
            pass

        return ret


class ECDispersibility(ECValueOnly):
    value_attr = 'effectiveness'

    def py_json(self):
        ret = super().py_json()
        ret['dispersant'] = self.condition_of_analysis

        return ret


class ECCompoundUngrouped(ECMeasurement):
    def determine_unit_type(self):
        # check if it is a mass/volume fraction.
        # - until PyNUCOS accepts a unit of measure like '% w/w' or '% v/v',
        #   we need to change it to '%' and set the unit type explicitly
        # - If it is None, we will default to massfraction
        if self.unit_of_measure in ('% w/w', '%w/w', None):
            self.unit_of_measure = '%'
            self.unit_type = 'massfraction'
            return
        elif self.unit_of_measure in ('% v/v', '%v/v'):
            self.unit_of_measure = '%'
            self.unit_type = 'volumefraction'
            return

        unit = Simplify(self.unit_of_measure)

        try:
            self.unit_type = UNIT_TYPES[unit]
        except KeyError:
            try:
                self.unit_type = UNIT_TYPES_MV[unit]
            except KeyError:
                self.unit_type = None

    def py_json(self):
        ret = super().py_json()

        if self.property_name is not None:
            ret['name'] = self.property_name

        return ret


class ECCompound(ECCompoundUngrouped):
    def py_json(self):
        ret = super().py_json()
        ret['groups'] = [self.property_group]

        return ret


class SeparatorString(str):
    """
    This is simply a way to specify a custom separator into our mapping list
    items that are of type str.
    """
    sep = '|'
    pass


mapping_list = [
    # ('property', 'mapped_property', 'to_type', 'scope'),
    ('oil_name', 'metadata.name', str, 'oil'),
    ('oil_index', 'metadata.source_id', str, 'oil'),
    ('synonyms', 'metadata.alternate_names.+', str, 'oil'),
    ('origin', 'metadata.location', str, 'oil'),
    ('date_sample_received', 'metadata.sample_date', datetime, 'oil'),
    ('comments', 'metadata.comments', str, 'oil'),
    ('referenceID', 'metadata.reference', SeparatorString, 'oil'),
    #
    # The following mappings deal with a measurement row packaged into an obj
    #
    ('Density.Density', 'physical_properties.densities.+',
     ECDensity, 'sample'),
    ('Dynamic Viscosity.Dynamic Viscosity',
     'physical_properties.dynamic_viscosities.+', ECViscosity, 'sample'),
    ('Kinematic Viscosity.Kinematic Viscosity',
     'physical_properties.kinematic_viscosities.+', ECViscosity, 'sample'),
    ('Saybolt Viscosity.Saybolt Viscosity',
     'physical_properties.kinematic_viscosities.+', ECViscosity, 'sample'),

    ('Surface Tension/ Interfacial tension.Surface Tension',
     'physical_properties.interfacial_tension_air.+', ECInterfacialTension,
     'sample'),
    ('Surface Tension/ Interfacial tension.Interfacial Tension',
     'physical_properties.interfacial_tension.+', ECInterfacialTension,
     'sample'),

    ('Colour.Colour', 'physical_properties.appearance', ECValueOnly, 'sample'),

    ('Flammability Limits in Air.Flammability Limits in Air',
     'industry_properties.???', ECValueOnly, 'sample'),
    ('Ignition Temperature.Ignition Temperature',
     'industry_properties.???', ECValueOnly, 'sample'),

    ('Flash Point.Flash Point', 'physical_properties.flash_point',
     ECValueOnly, 'sample'),
    ('Pour Point.Pour Point', 'physical_properties.pour_point',
     ECValueOnly, 'sample'),
    # ('Vapor Pressure.Vapor Pressure', '????', ECVaporPressure, 'sample'),

    ('Boiling Point Cumulative Weight Fraction.Boiling Point Cumulative Weight Fraction',
     'distillation_data.cwf_cuts.+', BPCumulativeWeightFraction, 'sample'),
    ('Boiling Point Temperature Cut Off.Boiling Point Temperature Cut Off',
     'distillation_data.tco_cuts.+', BPTemperatureDistribution, 'sample'),

    ('Adhesion.Adhesion', 'environmental_behavior.adhesion',
     ECAdhesion, 'sample'),
    # Note: ESTS Evaporation is better handled as a list if we choose to do it
    #       here.  But for now we will make it look exactly like it was before,
    #       and the way we will do it is by re-mapping these parts in the
    #       mapper.
    ('Evaporation Equation.A For %Ev = (A +B) Ln T',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    ('Evaporation Equation.B For %Ev = (A +B) Ln T',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    ('Evaporation Equation.A For %Ev = (A + B) Sqrt (T)',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    ('Evaporation Equation.B For %Ev = (A + B) Sqrt (T)',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    ('Evaporation Equation.A For %Ev= A+ B Ln (t+C)',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    ('Evaporation Equation.B For %Ev= A+ B Ln (t+C)',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    ('Evaporation Equation.C For %Ev= A+ B Ln (t+C)',
     'environmental_behavior.ests_evaporation_test.+',
     ECEvaporationEq, 'sample'),
    # Todo: Pan evaporation is something new.  Need to discuss.
    # ('Pan Evaporation (% Mass Loss).0h', 'environmental_behavior.????',
    # ECPanEvaporation, 'sample'),
    ('Emulsion.Emulsion formation/Visual Stability',
     'environmental_behavior.emulsions.+.visual_stability',
     ECEmulsion, 'sample'),
    ('Emulsion.Viscosity',
     'environmental_behavior.emulsions.-1.complex_viscosity',
     ECEmulsion, 'sample'),
    ('Emulsion.Complex Modulus',
     'environmental_behavior.emulsions.-1.complex_modulus',
     ECEmulsion, 'sample'),
    ('Emulsion.Water Content',
     'environmental_behavior.emulsions.-1.water_content',
     ECEmulsion, 'sample'),
    ('Chemical Dispersibility.Dispersant Effectiveness',
     'environmental_behavior.dispersibilities.+',
     ECDispersibility, 'sample'),
    ('Sulfur Content.Sulfur Content', 'bulk_composition.+',
     ECCompoundUngrouped, 'sample'),
    ('Sulphur Content.Sulphur Content', 'bulk_composition.+',
     ECCompoundUngrouped, 'sample'),
    ('Water Content.Water Content', 'bulk_composition.+',
     ECCompoundUngrouped, 'sample'),
    ('Wax Content.Waxes', 'bulk_composition.+',
     ECCompoundUngrouped, 'sample'),

    ('Metals.Aluminum', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Arsenic', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Barium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Cadmium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Calcium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Chromium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Cobalt', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Copper', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Iron', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Lead', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Magnesium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Manganese', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Mercury', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Molybdenum', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Nickel', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Potassium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Selenium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Silicon', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Sodium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Strontium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Tin', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Titanium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Vanadium', 'bulk_composition.+', ECCompound, 'sample'),
    ('Metals.Zinc', 'bulk_composition.+', ECCompound, 'sample'),

    ('Other Elements.Carbon', 'bulk_composition.+', ECCompoundUngrouped,
     'sample'),
    ('Other Elements.Chlorine', 'bulk_composition.+', ECCompoundUngrouped,
     'sample'),
    ('Other Elements.Hydrogen', 'bulk_composition.+', ECCompoundUngrouped,
     'sample'),
    ('Other Elements.Nitrogen', 'bulk_composition.+', ECCompoundUngrouped,
     'sample'),
    ('Other Elements.Oxygen', 'bulk_composition.+', ECCompoundUngrouped,
     'sample'),
    ('Other Elements.Phosphorous', 'bulk_composition.+', ECCompoundUngrouped,
     'sample'),

    ('Volatile Organic Compounds (VOCs).Benzene', 'compounds.+',
     ECCompound, 'sample'),
    ('Volatile Organic Compounds (VOCs).Toluene', 'compounds.+',
     ECCompound, 'sample'),
    ('Volatile Organic Compounds (VOCs).Ethylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('Volatile Organic Compounds (VOCs).Xylenes', 'compounds.+',
     ECCompound, 'sample'),
    ('Volatile Organic Compounds (VOCs).C3-Benzenes', 'compounds.+',
     ECCompound, 'sample'),
    ('Volatile Organic Compounds (VOCs).Total BTEX', 'compounds.+',
     ECCompound, 'sample'),
    ('Volatile Organic Compounds (VOCs).Total BTEX+ C3-Benzens', 'compounds.+',
     ECCompound, 'sample'),

    ('C3-C6 Alkyl Benzenes.Isopropylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.Propylebenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.3&4-Ethyltoluene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.1,3,5-Trimethylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.2-Ethyltoluene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.1,2,4-Trimethylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.1,2,3-Trimethylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.Isobutylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.1-Methyl-2-isopropylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.1,2-Dimethyl-4-ethylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.Amylbenzene', 'compounds.+', ECCompound, 'sample'),
    ('C3-C6 Alkyl Benzenes.n-Hexylbenzene', 'compounds.+',
     ECCompound, 'sample'),
    ('GC-Detected Petroleum Hydrocarbon Content'
     '.Gas Chromatography-Total Petroleum Hydrocarbon (GC-TPH)',
     'bulk_composition.+', ECCompound, 'sample'),
    ('GC-Detected Petroleum Hydrocarbon Content'
     '.Gas Chromatography-Total Saturate Hydrocarbon (GC-TSH)',
     'bulk_composition.+', ECCompound, 'sample'),
    ('GC-Detected Petroleum Hydrocarbon Content'
     '.Gas Chromatography-Total Aromatic Hydrocarbon (GC-TAH)',
     'bulk_composition.+', ECCompound, 'sample'),
    ('GC-Detected Petroleum Hydrocarbon Content.GC-TSH/GC-TPH',
     'bulk_composition.+', ECCompound, 'sample'),
    ('GC-Detected Petroleum Hydrocarbon Content.GC-TAH/GC-TPH',
     'bulk_composition.+', ECCompound, 'sample'),
    ('GC-Detected Petroleum Hydrocarbon Content.Resolved Peaks/TPH',
     'bulk_composition.+', ECCompound, 'sample'),

    ('Hydrocarbon Groups Content.Saturates',
     'SARA.saturates', ECValueOnly, 'sample'),
    ('Hydrocarbon Groups Content.Aromatics',
     'SARA.aromatics', ECValueOnly, 'sample'),
    ('Hydrocarbon Groups Content.Resins',
     'SARA.resins', ECValueOnly, 'sample'),
    ('Hydrocarbon Groups Content.Asphaltenes',
     'SARA.asphaltenes', ECValueOnly, 'sample'),
    ('n-Alkanes.n-C8', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C9', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C10', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C11', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C12', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C13', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C14', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C15', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C16', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C17', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.Pristane', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C18', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.Phytane', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C19', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C20', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C21', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C22', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C23', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C24', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C25', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C26', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C27', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C28', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C29', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C30', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C31', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C32', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C33', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C34', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C35', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C36', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C37', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C38', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C39', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C40', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C41', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C42', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C43', 'compounds.+', ECCompound, 'sample'),
    ('n-Alkanes.n-C44', 'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C0-Naphthalene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C1-Naphthalene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C2-Naphthalene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C3-Naphthalene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C4-Naphthalene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C0-Phenanthrene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C1-Phenanthrene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C2-Phenanthrene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C3-Phenanthrene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C4-Phenanthrene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C0-Dibenzothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C1-Dibenzothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C2-Dibenzothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C3-Dibenzothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C0-Fluorene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C1-Fluorene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C2-Fluorene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C3-Fluorene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C0-Fluoranthene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C1-Fluoranthene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C2-Fluoranthene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C3-Fluoranthene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C4-Fluoranthene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)'
     '.C0-Benzonaphthothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)'
     '.C1-Benzonaphthothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)'
     '.C2-Benzonaphthothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)'
     '.C3-Benzonaphthothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs)'
     '.C4-Benzonaphthothiophene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C0-Chrysene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C1-Chrysene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C2-Chrysene',
     'compounds.+', ECCompound, 'sample'),
    ('Alkylated Polycyclic Aromatic Hydrocarbons (PAHs).C3-Chrysene',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Biphenyl (Bph)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Acenaphthylene (Acl)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Acenaphthene (Ace)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Anthracene (An)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Fluoranthene (Fl)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Pyrene (Py)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Benz(a)anthracene (BaA)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Benzo(b)fluoranthene (BbF)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Benzo(k)fluoranthene (BkF)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Benzo(e)pyrene (BeP)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Benzo(a)pyrene (BaP)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Perylene (Pe)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Indeno(1,2,3-cd)pyrene (IP)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Dibenzo(ah)anthracene (DA)',
     'compounds.+', ECCompound, 'sample'),
    ('Other Priority PAHs.Benzo(ghi)perylene (BgP)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.C21 Tricyclic Terpane (C21T)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.C22 Tricyclic Terpane (C22T)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.C23 Tricyclic Terpane (C23T)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.C24 Tricyclic Terpane (C24T)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.18A,22,29,30-Trisnorneohopane (C27Ts)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.17a(H)-22,29,30-Trisnorhopane (C27Tm)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30-Norhopane (H29)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.Hopane (H30)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30-Homohopane-22S (H31S)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30-Homohopane-22R (H31R)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30,31-Bishomohopane-22S (H32S)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30,31-Bishomohopane-22R (H32R)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30,31-Trishomohopane-22S (H33S)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.30,31-Trishomohopane-22R (H33R)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.Tetrakishomohopane-22S (H34S)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.Tetrakishomohopane-22R (H34R)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.Pentakishomohopane-22S (H35S)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.Pentakishomohopane-22R (H35R)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.14ß(H),17ß(H)-20-Cholestane (C27aßß)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.20-Méthyl-14ß(H),17ß(H)-Cholestane (C28aßß)',
     'compounds.+', ECCompound, 'sample'),
    ('Biomarkers.20-Éthyl-14ß(H),17ß(H)-Cholestane (C29aßß)',
     'compounds.+', ECCompound, 'sample'),
]

property_map = {p: m for p, m, t, s in mapping_list}
property_type_map = {p: t for p, m, t, s in mapping_list}
property_scope_map = {p: s for p, m, t, s in mapping_list}


class EnvCanadaCsvRecordParser1999(ParserBase):
    """
    A record class for the Env. Canada .csv flat data file.
    This is intended to be used with a set of data representing a single
    oil record from the data file.  This set is in the form of a list
    containing dict objects, each representing a single measurement for
    the oil we are processing.

    * There are a number of reference fields, i.e. fields that associate
      a particular measurement to an oil.  They are:

        * oil_id: ID of an oil record.  This appears to be the camelcase
          name of the oil joined by an underscore with the ECCC
          oil ID.  There is one common value per oil, but there are
          redundant copies of this field in every measurement.

        * oil_index: ID of an oil record with one or more sub-samples.
          Similar to the ests field in the other EC data set.  There is one
          common value per oil, but there are redundant copies of this field
          in every measurement.

    * There are also a number of fields that would not normally be used to
      link a measurement to an oil, but are clearly oil general
      properties. There is usually one actual field value per oil, but
      there are redundant copies in every measurement.  Sometimes though,
      there are multiple names that show up in the measurements for an oil.
      Biodiesel records are an example of this.

        * oil_name
        * referenceID: A code to be used to look up the reference title in the
                       EC Reference document "References-Catalogue_of_Crude_Oil_and_Oil_Product_Properties_(1999)-Revised_2022_En_and_Fr.pdf"
        * sample_reference: The name of the reference.  This almost always
                            matches the lookup value correlated with the
                            referenceID, so there is some redundancy here.
        * reference: Would have expected something like the title of a document
                     here, but mostly this contains a 'N/A' value.  The fields
                     that are actually filled in contain the same referenceID
                     code.
        * comments:
        * origin: The location where the oil originates.
        * synonyms

    * There are a number of fields that would intuitively seem to
      associated a measurement with a sub-sample.  There is usually
      one common value per sub-sample, but there are redundant copies in
      every measurement.

        * index_id: ID of an oil sample.  This appears to be the concatenation
                    of the oil_index and a sample number separated by a period
                    ".".
        * weathering_fraction: This appears to be a percentage value in the
                               range 0-100.
        * grade

    * And finally, we have a set of fields that are used uniquely for the
      measurement

        * property_name
        * property_group
        * property_id
        * value
        * value_id
        * unit_of_measure
        * temperature
        * condition_of_analysis
        * note

    """
    oil_common_props = ('oil_name', 'oil_index', 'synonyms', 'origin',
                        'referenceID', 'comments')
    sample_id_field_name = 'index_id'

    def __init__(self, values):
        """
        :param values: A list of dictionary objects containing property
                       values.  Each object contains information about a
                       single measurement.
        :type values: A list of dictionary structures with raw property
                      names as keys, and associated values.
        """
        super().__init__(self.prune_incoming(values))

        self.set_aggregate_oil_props()
        self.set_aggregate_subsample_props()
        self.set_measurement_props()

    def prune_incoming(self, values):
        """
        The Incoming objects contain some unwanted garbage from the
        spreadsheet that would be better handled before we start parsing
        anything.
        """
        if len(values) == 0:
            return  # nothing to prune

        keys = set(values[0].keys())
        valid_keys = {k for k in keys if k not in ('',)}
        bad_keys = keys.difference(valid_keys)

        for obj in values:
            [obj.pop(k, None) for k in bad_keys]

        return values

    def set_aggregate_oil_props(self):
        """
        These are properties commonly associated with an oil.

        There is a copy of this information inside every measurement,
        so we need to reconcile them in order to come up with an
        aggregate value with which to set the oil properties.
        """
        for attr in self.oil_common_props:
            self.set_aggregate_oil_property(attr)

        # product_type needs special treatment
        self.deep_set(self.oil_obj, 'metadata.product_type', self.product_type)

        # API needs special treatment
        if self.API:
            self.deep_set(self.oil_obj, 'metadata.API', self.API)

        oil_id = f'CC{self.oil_obj["metadata"]["source_id"]:>05}'
        self.oil_obj['oil_id'] = oil_id

    def set_aggregate_oil_property(self, attr):
        """
        Oil scoped properties are redundantly stored in each measurement
        object in our list, so they need to be accumulated and treated in
        some way depending on the type of data we would like to set in the
        model.

        * Attributes to be treated as strings will have their values
          accumulated in a unique set to prune the redundant information,
          and then the unique strings in the set will be concatenated into
          a single string.

        * Attributes to be treated as integers will also be accumulated
          in a unique set to prune the redundant values.  But multiple
          ints can not be stored in another int the same way a string can.
          So we issue a warning and then use the first one in the set.
          This isn't perfect, but there are only a handful of oil scoped
          attributes and we can make an exception if there is an obvious
          problem.
        """
        to_type = property_type_map.get(attr, None)

        if to_type is SeparatorString:
            value = to_type.sep.join({str(v[attr]) for v in self.src_values
                                      if v[attr] is not None
                                      and v[attr] != 'None'})

            value = None if len(value) == 0 else value
        elif to_type is str:
            value = ' '.join({str(v[attr]) for v in self.src_values
                             if v[attr] is not None and v[attr] != 'None'})

            value = None if len(value) == 0 else value
        elif to_type is int:
            value = {int(v[attr]) for v in self.src_values
                     if v[attr] is not None}

            if len(value) > 1:
                # This is a problem, but not big enough to stop everything
                logger.warning(f'ESTS #{self.src_values[0]["ests"]}: '
                               f'More than 1 integer value found for {attr}')

            value = list(value)[0] if len(value) >= 1 else None
        elif to_type is datetime:
            value = {v[attr] for v in self.src_values if v[attr] is not None}
            value = [parse_single_datetime(v) for v in value]

            if len(value) > 1:
                # This is a problem, but not big enough to stop everything
                logger.warning(f'ESTS #{self.src_values[0]["ests"]}: '
                               f'More than 1 datetime value found for {attr}')

            value = value[0].strftime('%Y-%m-%d') if len(value) >= 1 else None
        else:
            logger.error(f'unimplemented type for {attr}')
            value = None

        if value:
            try:
                self.deep_set(self.oil_obj, property_map[attr], value)
            except KeyError:
                logger.error(f'No property mapping for {attr}')
                raise

    def set_aggregate_subsample_props(self):
        """
        These are properties commonly associated with a sub-sample.
        There is a copy of this information inside every measurement,
        so we need to reconcile them to determine the identifying
        properties of each sub-sample.

        Sub-sample properties:

        - ests_id: One common value per sub-sample.  This could be numeric,
                   so we force it to be a string.

        - weathering_fraction: One value per sub-sample.  These values
                               look like some kind of code that EC uses.
                               Probably not useful to us.

        - weathering_percent: One common value per sub-sample.  These
                              values are mostly a string in the format
                              'N.N%'.  We will convert to a structure
                              suitable for a Measurement type.

        - weathering_method: One common value per sub-sample.  This is
                             information that might be good to save, but
                             it doesn't fit into the Adios oil model.
        """
        first_objs = [v for v in self.src_values
                      if v['property_id'] == 'Density_0']

        first_sample_ids = [o[self.sample_id_field_name] for o in first_objs]
        if not self.sample_ids == first_sample_ids:
            raise ValueError(f'duplicate sample_ids: {first_sample_ids}')

        for idx, o in enumerate(first_objs):
            name = None
            sample_id = str(o[self.sample_id_field_name])
            weathering_percent = o['weathering_fraction']

            if weathering_percent in (None, 'None'):
                weathering_percent = None
            elif weathering_percent == 'Environmental Sample':
                name = 'Environmental Sample'
                short_name = 'Env. Sample'
                weathering_percent = {
                    'min_value': 0.0, 'max_value': None, 'unit': '%'
                }
            elif weathering_percent == 'New':
                name = 'Fresh Oil Sample'
                short_name = 'Fresh Oil'
                weathering_percent = {
                    'value': 0.0, 'unit': '%'
                }
            elif weathering_percent in ('Used', 'Weathered'):
                # We can't tell how much the sample is weathered,
                # but it is more than 0%
                name = f'{weathering_percent} (unknown weathered amount)'
                short_name = f'{weathering_percent}'
                weathering_percent = {
                    'min_value': 1.0, 'max_value': None, 'unit': '%'
                }
            else:
                try:
                    weathering_percent = weathering_percent.rstrip('%')
                except AttributeError:
                    pass

                # sigfigs doesn't fail out, but returns the original value
                # so we need to explicitly check that it's a number before
                # modifying it into a measurement
                try:
                    float(weathering_percent)  # just to test it
                    weathering_percent = {
                        'value': sigfigs(weathering_percent, sig=5),
                        'unit': '%'
                    }
                except ValueError:
                    pass

            if name is not None:
                pass
            elif (weathering_percent is not None and
                    'value' in weathering_percent and
                    isinstance(weathering_percent['value'], (int, float))):
                if isclose(weathering_percent['value'], 0.0):
                    name = 'Fresh Oil Sample'
                    short_name = 'Fresh Oil'
                else:
                    name = f'{weathering_percent["value"]}% Evaporated'
                    short_name = f'{weathering_percent["value"]}% Evaporated'
            else:
                name = f'{o["weathering_fraction"]}'
                short_name = f'{o["weathering_fraction"]}'[:12]

            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.sample_id', sample_id)
            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.name', name)
            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.short_name', short_name)
            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.fraction_weathered',
                          weathering_percent)

    @property
    def API(self):
        """
        API Gravity needs to be stored as an oil property, but it is
        in fact a sub-sample scoped property.  So we need to figure out
        the fresh sample ID and get that specific API gravity property.

        Note: API for Biodiesels shows a weathering value of 'None',
              but clearly it is the "fresh sample".  We need to allow it.
        """
        api_obj = [v for v in self.src_values
                   if v[self.sample_id_field_name] == self.fresh_sample_id
                   and v['property_group'] == 'API Gravity'
                   and v['property_name'] == 'API Gravity']
        api_obj = api_obj[0] if len(api_obj) > 0 else {}

        weathering = api_obj.get('weathering_fraction', None)

        try:
            weathering = float(weathering.rstrip('%'))
        except (AttributeError, ValueError):
            pass

        if weathering not in ('None', 0.0):
            # first sample is not fresh, we need to get API from the
            # fresh sample
            return None

        if weathering == 'Environmental Sample':
            # All we can know about this type of sample is that the weathering
            # is >0, so it is not a fresh sample.
            return None

        return api_obj['value']

    def set_measurement_props(self):
        """
        All objects in the incoming list have the primary function of
        describing a particular measurement of an oil.  Here we iterate
        over these objects.
        """
        for obj in self.src_values:
            self.set_measurement_property(obj)

    def set_measurement_property(self, obj_in):
        """
        Set a single measurement from an incoming measurement object

        Basically we need to decide how to apply the property to our record

        - oil scoped properties are applied to the oil object.
        - sample scoped properties can are applied to a particular
          sub-sample determined by the object

        The properties that describe the measurement are:

        - value_id: This is a concatenation of the ests and property_id
                    fields delimited with underscores '_'.
        - property_id: This is a concatenation of the camel cased
                       property_name and, as far as I can tell, the index
                       value of the sequence in which the property appears.
        - property_group: This is the name of a group or category with
                          which a set of measurements might be associated.
        - property_name: The prose name of the property that is measured.
        - unit_of_measure: The units for which the measurement describes
                           a quantity.
        - temperature: The temperature at which the measurement was taken.
        - condition_of_analysis: A reasonably free-form line of text that
                                 describes some special condition of the
                                 measurement, such as a prerequisite for
                                 measurement, a specification on the type
                                 of measurement, or its result.
        - value: A number representing the quantity of the measurement
        - standard_deviation: The amount of variation in the set of
                              measurements taken.
        - replicates: A number representing the quantity of repeated
                      experiments where measurements were taken.
        - method: A line of text showing the name of the testing method.
        """
        always_add = ('Emulsion Visual Stability',)

        if (self.value_is_invalid(obj_in['value']) and
                obj_in['property_name'] not in always_add):
            return  # not a valid measurement

        try:
            attr = f'{obj_in["property_group"]}.{obj_in["property_name"]}'
            mapped_attr = property_map[attr]
            to_type = property_type_map[attr]
            scope = property_scope_map[attr]
        except KeyError:
            # logger.error(f'Unmapped property path: {attr}')
            return

        if scope == 'oil':
            obj = self.oil_obj
        elif scope == 'sample':
            obj = self.get_subsample(obj_in[self.sample_id_field_name])
        else:
            logger.error(f'measurement record has unknown scope: {scope}')

        # destination type is a datatype or a class
        if hasattr(to_type, 'from_obj') and hasattr(to_type, 'py_json'):
            value = to_type.from_obj(obj_in).py_json()
        else:
            value = "Value Not Set"

        self.deep_set(obj, mapped_attr, value)

    @property
    def fresh_sample_id(self):
        return self.sample_ids[0]

    @property
    def sample_ids(self):
        """
        This function relies on dict having keys ordered by the sequence
        of insertion into the dict.  This is true of Python 3.6, but could
        break in the future.
        """
        sample_ids = {v[self.sample_id_field_name]: None
                      for v in self.src_values}
        return list(sample_ids.keys())

    def get_subsample(self, sample_id):
        samples = [s for s in self.oil_obj['sub_samples']
                   if s['metadata']['sample_id'] == str(sample_id)]

        if len(samples) == 1:
            return samples[0]
        else:
            return None

    @property
    def product_type(self):
        if self._product_type_is_probably_refined():
            return 'Refined Product NOS'
        else:
            return 'Crude Oil NOS'

    def _product_type_is_probably_refined(self):
        """
        We don't have a lot of options determining what product type the
        Env Canada records are.  The Source, Comments, and Reference fields
        might be used, but they are pretty unreliable.

        But we might be able to make some guesses based on the name of the
        product.  This is definitely not a great way to do it, but we need
        to make a determination somehow.
        """
        name = ' '.join({v['oil_name'] for v in self.src_values
                         if v['oil_name'] is not None
                         and v['oil_name'] != 'None'})
        words = name.lower().split()

        for word in words:
            # if these words appear anywhere in the name, we will assume
            # it is refined
            if word in ('fuel', 'diesel', 'biodiesel',
                        'ifo', 'hfo', 'lube'):
                return True

        # check for specific n-grams of size 2
        for token in zip(words, words[1:]):
            if token in (('bunker', 'c'),
                         ('swepco', '737')):
                return True

        return False

    def value_is_invalid(self, value):
        return value in (None, 'N/A', 'No Flash')
