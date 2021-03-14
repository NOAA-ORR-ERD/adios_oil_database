#!/usr/bin/env python
import re
import logging
from datetime import datetime
from dataclasses import dataclass, fields

from numpy import isclose

from unit_conversion import UNIT_TYPES

from adios_db.util import sigfigs
from adios_db.data_sources.parser import ParserBase, parse_single_datetime

import pdb
from pprint import pprint

logger = logging.getLogger(__name__)


@dataclass
class ECMeasurementDataclass:
    '''
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
    '''
    value: float = None
    unit_of_measure: str = None
    temperature: str = None
    condition_of_analysis: str = None
    standard_deviation: float = None
    replicates: float = None
    method: str = None

    def __post_init__(self):
        self.treat_any_bad_initial_values()
        self.parse_temperature_string()
        self.determine_unit_type()

    def treat_any_bad_initial_values(self):
        if self.value == '':
            self.value = None

        if self.standard_deviation == 'N/A':
            self.standard_deviation = None

        if self.replicates == 'N/A':
            self.replicates = None

        if self.unit_of_measure is not None:
            self.unit_of_measure = self.unit_of_measure.lower()

    def parse_temperature_string(self):
        if self.temperature is not None and len(self.temperature) > 0:
            self.ref_temp, self.ref_temp_unit = re.findall(r'[\d\.]*\w+',
                                                           self.temperature)
        try:
            self.ref_temp = float(self.ref_temp)
        except Exception:
            pass

    def determine_unit_type(self):
        try:
            self.unit_type = UNIT_TYPES[self.unit_of_measure]
        except KeyError:
            self.unit_type = None


class ECMeasurement(ECMeasurementDataclass):
    value_attr = 'measurement'

    @classmethod
    def from_obj(cls, obj):
        class_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in obj.items() if k in class_fields})

    def py_json(self):
        return {
            self.value_attr: {
                "value": self.value,
                "unit": self.unit_of_measure,
                "unit_type": self.unit_type,
                "replicates": self.replicates,
                "standard_deviation": self.standard_deviation,
            },
            "method": self.method,
            "ref_temp": {
                "value": self.ref_temp,
                "unit": self.ref_temp_unit,
                "unit_type": "temperature",
            }
        }


class ECDensity(ECMeasurement):
    value_attr = 'density'


mapping_list = [
    # ('property', 'mapped_property', 'to_type', 'scope'),
    ('oil_name', 'metadata.name', str, 'oil'),
    ('ests', 'metadata.source_id', int, 'oil'),
    ('source', 'metadata.location', str, 'oil'),
    ('date_sample_received', 'metadata.sample_date', datetime, 'oil'),
    ('comments', 'metadata.comments', str, 'oil'),
    # the following mappings deal with a measurement row packaged into an obj
    ('Density.Density', 'physical_properties.densities.-1', ECDensity, 'sample'),
]

property_map = {p: m for p, m, t, s in mapping_list}
property_type_map = {p: t for p, m, t, s in mapping_list}
property_scope_map = {p: s for p, m, t, s in mapping_list}


reject_list = [
    4025,  # Marine Diesel-Burnaby BC (bad subsamples)
    1956,  # North Star (bad subsamples)
    662,   # Orimulsion 400 [2001] (bad subsamples)
]


class EnvCanadaCsvRecordParser(ParserBase):
    '''
        A record class for the Env. Canada .csv flat data file.
        This is intended to be used with a set of data representing a single
        oil record from the data file.  This set is in the form of a list
        containing dict objects, each representing a single measurement for
        the oil we are processing.

        - There are a number of reference fields, i.e. fields that associate
          a particular measurement to an oil.  They are:
            - oil_id: ID of an oil record.  This appears to be the camelcase
                      name of the oil joined by an underscore with the ESTS
                      oil ID.  There is one common value per oil, but there are
                      redundant copies of this field in every measurement.
            - ests: ESTS ID of an oil record with one or more sub-samples.
                    There is one common value per oil, but there are redundant
                    copies of this field in every measurement.

        - There are also a number of fields that would not normally be used to
          link a measurement to an oil, but are clearly oil general
          properties. There is usually one actual field value per oil, but
          there are redundant copies in every measurement.  Sometimes though,
          there are multiple names that show up in the measurements for an oil.
          Biodiesel records are an example of this.
            - oil_name
            - reference
            - date_sample_received
            - source:
            - comments:

        - There are a number of fields that would intuitively seem to
          be used to link a measurement to a sub-sample.  There is usually
          one common value per sub-sample, but there are redundant copies in
          every measurement.
            - ests_id: ESTS ID of an oil sample
            - weathering_fraction
            - weathering_percent
            - weathering_method

        - And finally, we have a set of fields that are used uniquely for the
          measurement
            - value_id
            - property_id
            - property_group
            - property_name
            - unit_of_measure
            - temperature
            - condition_of_analysis
            - value
            - standard_deviation
            - replicates
            - method
    '''
    def __init__(self, values):
        '''
            :param values: A list of dictionary objects containing property
                           values.  Each object contains information about a
                           single measurement.
            :type values: A list of dictionary structures with raw property
                          names as keys, and associated values.
        '''
        super().__init__(self.prune_incoming(values))

        self.set_aggregate_oil_props()

        if self.oil_obj['metadata']['source_id'] in reject_list:
            logger.warning('rejecting oil record: '
                           f'{self.oil_obj["metadata"]["source_id"]}')
            return

        self.set_aggregate_subsample_props()

        self.set_measurement_props()

        print('\n\noil_obj:')
        pprint(self.oil_obj)

    def prune_incoming(self, values):
        '''
            The Incoming objects contain some unwanted garbage from the
            spreadsheet that would be better handled before we start parsing
            anything.
        '''
        valid_fields = ('value_id', 'oil_id', 'ests_id', 'property_id',
                        'oil_name', 'source', 'date_sample_received',
                        'comments', 'ests', 'reference', 'weathering_fraction',
                        'weathering_percent', 'weathering_method',
                        'property_group', 'property_name', 'unit_of_measure',
                        'temperature', 'condition_of_analysis', 'value',
                        'standard_deviation', 'replicates', 'method')
        for obj in values:
            bad_keys = [k for k in obj.keys() if k not in valid_fields]
            [obj.pop(k) for k in bad_keys]

        return values

    def set_aggregate_oil_props(self):
        '''
            These are properties commonly associated with an oil.
            There is a copy of this information inside every measurement,
            so we need to reconcile them in order to come up with an
            aggregate value with which to set the oil properties.
        '''
        for attr in ('oil_name', 'ests', 'source', 'date_sample_received',
                     'comments'):
            self.set_aggregate_oil_property(attr)

        # reference needs special treatment
        self.deep_set(self.oil_obj, 'metadata.reference', {
            'reference': 'Personal communication from '
                         'Mischa Bertrand-Chetty (EC), '
                         'date: Mar 4, 2021.',
            'year': 2021
        })

        # product_type needs special treatment
        self.deep_set(self.oil_obj, 'metadata.product_type', self.product_type)

        # API needs special treatment
        if self.API:
            self.deep_set(self.oil_obj, 'metadata.API', self.API)

    def set_aggregate_oil_property(self, attr):
        '''
            Oil scoped properties are redundantly stored in each measurement
            object in our list, so they need to be accumulated and treated in
            some way depending on the type of data we would like to set in the
            model.
            - Attributes to be treated as strings will have their values
              accumulated in a unique set to prune the redundant information,
              and then the unique strings in the set will be concatenated into
              a single string.
            - Attributes to be treated as integers will also be accumulated
              in a unique set to prune the redundant values.  But multiple
              ints can not be stored in another int the same way a string can.
              So we issue a warning and then use the first one in the set.
              This isn't perfect, but there are only a handful of oil scoped
              attributes and we can make an exception if there is an obvious
              problem.
        '''
        # FIGURE OUT THE TYPE OF OBJECT TO SET
        to_type = property_type_map[attr]

        if to_type is str:
            value = ' '.join({str(v[attr]) for v in self.src_values
                             if v[attr] is not None
                             and v[attr] != 'None'})

            if len(value) == 0:
                value = None
        elif to_type is int:
            value = {int(v[attr]) for v in self.src_values
                     if v[attr] is not None}

            if len(value) > 1:
                # This is probably not a big enough problem to stop everything,
                # but we will issue a warning.
                logger.warning(f'More than 1 integer value found for {attr}')

            if len(value) >= 1:
                value = list(value)[0]
            else:
                value = None

        elif to_type is datetime:
            value = {v[attr] for v in self.src_values if v[attr] is not None}
            value = [parse_single_datetime(v) for v in value]

            if len(value) > 1:
                # This is probably not a big enough problem to stop everything,
                # but we will issue a warning.
                logger.warning(f'More than 1 datetime value found for {attr}')

            if len(value) >= 1:
                value = value[0]
            else:
                value = None
        else:
            print(f'unimplemented type for {attr}')
            value = None

        # SET THE VALUE
        if value:
            try:
                self.deep_set(self.oil_obj, property_map[attr], value)
            except KeyError:
                logger.error(f'No property mapping for {attr}')
                raise

    def set_aggregate_subsample_props(self):
        '''
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
        '''
        first_objs = [v for v in self.src_values
                      if v['property_id'] == 'Density_0']

        assert self.sample_ids == [o['ests_id'] for o in first_objs]

        for idx, o in enumerate(first_objs):
            sample_id = str(o['ests_id'])
            weathering_percent = o['weathering_percent']

            if weathering_percent is None or weathering_percent == 'None':
                weathering_percent = None
            else:
                weathering_percent = {
                    'value': sigfigs(weathering_percent.rstrip('%'),
                                     sig=5),
                    'unit': '%'
                }

            if (weathering_percent is not None and
                    isclose(weathering_percent['value'], 0.0)):
                name = 'Fresh Oil Sample'
                short_name = 'Fresh Oil'
            elif weathering_percent is not None:
                name = f'{weathering_percent["value"]}% Weathered'
                short_name = f'{weathering_percent["value"]}% Weathered'
            else:
                name = f'{o["weathering_fraction"]}'
                short_name = f'{o["weathering_fraction"]}'[:12]

            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.sample_id',
                          sample_id)
            self.deep_set(self.oil_obj, f'sub_samples.{idx}.metadata.name',
                          name)
            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.short_name',
                          short_name)
            self.deep_set(self.oil_obj,
                          f'sub_samples.{idx}.metadata.fraction_weathered',
                          weathering_percent)

    @property
    def API(self):
        '''
            API Gravity needs to be stored as an oil property, but it is
            in fact a sub-sample scoped property.  So we need to figure out
            the fresh sample ID and get that specific API gravity property.

            Note: API for Biodiesels shows a weathering value of 'None',
                  but clearly it is the "fresh sample".  We need to allow it.
        '''
        api_obj = [v for v in self.src_values
                   if v['ests_id'] == self.fresh_sample_id
                   and v['property_id'] == 'APIGravity_3']
        api_obj = api_obj[0] if len(api_obj) > 0 else {}

        weathering = api_obj['weathering_percent']
        assert (weathering == 'None' or float(weathering.rstrip('%')) == 0.0)

        return api_obj['value']

    def set_measurement_props(self):
        '''
            All objects in the incoming list have the primary function of
            describing a particular measurement of an oil.  Here we iterate
            over these objects.
        '''
        for obj in self.src_values:
            self.set_measurement_property(obj)

    def set_measurement_property(self, obj_in):
        '''
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
        '''
        try:
            attr = f'{obj_in["property_group"]}.{obj_in["property_name"]}'
            mapped_attr = property_map[attr]
            to_type = property_type_map[attr]
            scope = property_scope_map[attr]
        except KeyError:
            #logger.error(f'Unmapped property path: {attr}')
            return

        if scope == 'oil':
            obj = self.oil_obj
        elif scope == 'sample':
            obj = self.get_subsample(obj_in['ests_id'])
        else:
            logger.error(f'measurement record has unknown scope: {scope}')

        # destination type is a datatype or a class
        if hasattr(to_type, 'from_obj') and hasattr(to_type, 'py_json'):
            print(f'to_type = {to_type}')
            value = to_type.from_obj(obj_in).py_json()
        else:
            value = "Value Not Set"

        self.deep_set(obj, mapped_attr, value)

    @property
    def fresh_sample_id(self):
        return self.sample_ids[0]

    @property
    def sample_ids(self):
        '''
            This function relies on dict having keys ordered by the sequence
            of insertion into the dict.  This is true of Python 3.6, but could
            break in the future.
        '''
        sample_ids = {v['ests_id']: None for v in self.src_values}
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
        '''
            We don't have a lot of options determining what product type the
            Env Canada records are.  The Source, Comments, and Reference fields
            might be used, but they are pretty unreliable.

            But we might be able to make some guesses based on the name of the
            product.  This is definitely not a great way to do it, but we need
            to make a determination somehow.
        '''
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

    @property
    def metadata(self):
        ret = {}

        for attr in ('name',
                     'source_id',
                     'location',
                     'reference',
                     'sample_date',
                     'product_type',
                     'API',
                     'comments'):
            ret[attr] = getattr(self, attr)

        return ret

    def dict(self):
        ret = {}

        for attr in ('oil_id',
                     'metadata'):
            ret[attr] = getattr(self, attr)

        ret['sub_samples'] = list(self.sub_samples)

        return ret









