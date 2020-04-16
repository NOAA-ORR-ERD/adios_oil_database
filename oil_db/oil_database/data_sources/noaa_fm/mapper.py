#!/usr/bin/env python
from numbers import Number
from datetime import datetime
from collections import defaultdict
import logging
from math import isclose

from oil_database.models.common.float_unit import (AdhesionUnit)

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


class OilLibraryAttributeMapper(object):
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
                 'name',
                 'location',
                 'reference',
                 # 'sample_date',  # not found in the datasheet
                 'comments',
                 'labels',
                 'status',
                 'product_type',
                 'API',
                 #'sub_samples',
                 )
    fresh_sample_props = ('enivironmental_behavior',
                          'SARA',
                          'distillation_data',
                          'compounds',
                          'bulk_composition',
                          'headspace_analysis',
                          'CCME')
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

    def dict(self):
        rec = {}

        for attr in self.oil_properties:
            rec[attr] = getattr(self, attr)

    def dict_old(self):
        rec = {}
        samples = defaultdict(dict)

        for p in self.get_interface_properties():
            k, v = p, getattr(self, p)

            if k in self.top_record_properties:
                rec[k] = v
            elif hasattr(v, '__iter__') and not hasattr(v, '__len__'):
                # we have a sequence of items
                for i in v:
                    w = i.get('weathering', 0.0)
                    i.pop('weathering', None)

                    try:
                        samples[w][k].append(i)
                    except KeyError:
                        samples[w][k] = []
                        samples[w][k].append(i)
            else:
                # - assume a weathering of 0
                # - if the attribute is None, we don't add it.
                if v is not None:
                    samples[0.0][k] = v

        for k, v in samples.items():
            v.update(self.generate_sample_id_attrs(k))

        rec['samples'] = self.sort_samples(samples.values())

        return rec

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
            attrs['fraction_weathered'] = sample_id
            attrs['boiling_point_range'] = None
        elif isinstance(sample_id, Number):
            # we will assume this is a simple fractional weathered amount
            attrs['name'] = '{}% Weathered'.format(sample_id * 100)
            attrs['short_name'] = '{}% Weathered'.format(sample_id * 100)
            attrs['fraction_weathered'] = sample_id
            attrs['boiling_point_range'] = None
        else:
            logger.warn("Can't generate IDs for sample: ", sample_id)

        return attrs

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











