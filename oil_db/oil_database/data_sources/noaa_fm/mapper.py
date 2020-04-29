#!/usr/bin/env python
from numbers import Number
from collections import defaultdict
import logging
from math import isclose

from ..mapper import MapperBase

from oil_database.models.oil.oil import Oil

from pprint import pprint

logger = logging.getLogger(__name__)


class OilLibraryAttributeMapper(MapperBase):
    '''
        A translation/conversion layer for the NOAA Filemaker imported
        record object.
        This is intended to be used interchangeably with either a NOAA
        Filemaker record or record parser object.  Its purpose is to generate
        named attributes that are suitable for creation of a NOAA Oil Database
        record.
    '''
    oil_props = ('_id',
                 'oil_id',
                 'metadata',
                 'status',
                 'sub_samples')
    fresh_sample_props = ('environmental_behavior',
                          'SARA',
                          'distillation_data',
                          'compounds',
                          'bulk_composition')
    weathered_sample_props = ('physical_properties',)

    def __init__(self, record):
        '''
            :param property_indexes: A lookup dictionary of property index
                                     values.
            :type property_indexes: A dictionary with property names as keys,
                                    and associated index values into the data.
        '''
        self.record = record
        self.status = None
        self.labels = None

    def __getattr__(self, name):
        '''
            Handle any attributes not defined as properties in this class
            by trying them on the parser.
        '''
        try:
            ret = getattr(self.record, name)
        except Exception:
            logger.info(f'{self.__class__.__name__}.{name} not found')
            raise

        return ret

    def py_json(self):
        rec = {}

        for attr in self.oil_props:
            rec[attr] = getattr(self, attr)

        obj = Oil.from_py_json(rec)

        return obj.py_json()

    @property
    def adhesion(self):
        '''
            The parser has an adhesion attribute with a simple float, and we
            would like to reform it as a value/unit.  But we don't want to
            change its name.  So we redefined it in the mapper.

            Note: We don't really know what the adhesion units are for the
                  NOAA Filemaker records.

                  Need to ask JeffL

                  Based on the range of numbers I am seeing, it kinda looks
                  like we are dealing with Pascals (N/m^2)
        '''
        adhesion = self.record.adhesion

        if adhesion is not None:
            ret = {'value': adhesion, 'unit': 'N/m^2'}
        else:
            ret = None

        return ret

    @property
    def sub_samples(self):
        samples = []
        for w in self.weathering:
            samples.append(self.sample(w))

        return samples

    def sample(self, weathering):
        ret = self.generate_sample_id_attrs(weathering)

        for attr in self.weathered_sample_props:
            value = getattr(self, attr)(weathering)

            if value is not None:
                ret[attr] = value

        if isclose(weathering, 0.0):
            # first unweathered, get the fresh sample attrs
            for attr in self.fresh_sample_props:
                value = getattr(self, attr, None)

                if value is not None:
                    ret[attr] = value

        return ret

    def generate_sample_id_attrs(self, sample_id):
        attrs = {}

        if isinstance(sample_id, str):
            attrs['name'] = sample_id
            attrs['short_name'] = '{}...'.format(sample_id[:12])
            attrs['fraction_weathered'] = None
            attrs['boiling_point_range'] = None
        elif isclose(sample_id, 0):
            attrs['name'] = 'Fresh Oil Sample'
            attrs['short_name'] = 'Fresh Oil'
            attrs['fraction_weathered'] = {'value': sample_id, 'unit': '1'}
            attrs['boiling_point_range'] = None
        elif isinstance(sample_id, Number):
            # we will assume this is a simple fractional weathered amount
            attrs['name'] = '{}% Weathered'.format(sample_id * 100)
            attrs['short_name'] = '{}% Weathered'.format(sample_id * 100)
            attrs['fraction_weathered'] = {'value': sample_id, 'unit': '1'}
            attrs['boiling_point_range'] = None
        else:
            logger.warn("Can't generate IDs for sample: ", sample_id)

        return attrs

    @property
    def metadata(self):
        ret = {}

        for attr in ('name',
                     'source_id',
                     'location',
                     'reference',
                     # 'sample_date',  # not available in datasheet
                     'product_type',
                     'API',
                     'comments'):
            ret[attr] = getattr(self, attr)

        return ret

    @property
    def environmental_behavior(self):
        '''
            Notes:
            - there is a dispersability_temp_k, but it does not fit with the
              oil model.  sample.environmental_behavior.dispersibilites is
              for chemical dispersibility with a dispersant, and makes no
              reference to a temperature.
        '''
        ret = {}

        for attr in ('emulsions',):
            ret[attr] = getattr(self, attr, None)

        return ret

    @property
    def compounds(self):
        '''
            Tentative Compound items:
            - benzene (units=???, typical value=0.05 for gasoline,
                       just a fractional value maybe?)
            - naphthenes (units=???, typical value=0.0004 for Jet A-1)
            - ???

            Notes:
            - we need to discuss what fields in the NOAA Filemaker datasheet
              constitute compounds.
        '''
        ret = []
        for attr in ('benzene', 'naphthenes'):
            value = getattr(self, attr, None)

            if value is not None:
                ret.append(self.compound(
                    attr,
                    self.measurement(value=value, unit='1',
                                     unit_type='massfraction'),
                ))

        return ret

    @property
    def bulk_composition(self):
        '''
            Tentative Bulk Composition items:
            - Paraffins  (unit=???, 0.783 for Alberta 1992
                          0.019 for Salmon Oil & Gas)
            - Polars  (unit=1 possibly, 0.0284 for Alberta 1992)
            - Sulfur  (unit=1 possibly, 0.0104 for Alaska North Slope)
            - Nickel  (unit=ppm most likely)
            - Vanadium  (unit=ppm most likely)

            Notes:
            - we need to discuss what fields in the NOAA Filemaker datasheet
              constitute compounds.
        '''
        ret = []
        for attr, unit in (('paraffins', '1'),
                           ('polars', '1'),
                           ('sulfur', '1'),
                           ('nickel', 'ppm'),
                           ('vanadium', 'ppm')):
            value = getattr(self, attr, None)

            if value is not None:
                ret.append(self.compound(
                    attr,
                    self.measurement(value=value, unit=unit,
                                     unit_type='massfraction'),
                ))

        return ret

    def physical_properties(self, weathering):
        ret = {}

        # fresh only attributes
        if isclose(weathering, 0.0):
            for attr in ('pour_point', 'flash_point', 'interfacial_tensions'):
                value = getattr(self, attr)

                if value is not None:
                    ret[attr] = value

        # weathered attributes
        for attr in ('densities', 'dynamic_viscosities',
                     'kinematic_viscosities'):
            values = self.filter_weathered_attr(attr, weathering)

            if len(values) > 0:
                ret[attr] = values

        return ret

    def filter_weathered_attr(self, attr, weathering):
        values = getattr(self, attr, None)

        if values is None:
            return []
        else:
            values = [v for v in values
                      if isclose(v['weathering'], weathering)]
            [v.pop('weathering', None) for v in values]

            return values
