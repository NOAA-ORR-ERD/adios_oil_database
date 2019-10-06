#!/usr/bin/env python
import logging
from datetime import datetime

from oil_database.models.common.float_unit import (FloatUnit,
                                                   TemperatureUnit,
                                                   TimeUnit,
                                                   DensityUnit,
                                                   KinematicViscosityUnit,
                                                   DynamicViscosityUnit,
                                                   InterfacialTensionUnit,
                                                   AdhesionUnit)

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
    def __init__(self, record):
        '''
            :param property_indexes: A lookup dictionary of property index
                                     values.
            :type property_indexes: A dictionary with property names as keys,
                                    and associated index values into the data.
        '''
        self.record = record
        self._status = None
        self._categories = None

    def get_interface_properties(self):
        '''
            These are all the property names that define the data in an
            NOAA Oil Database record.
            Our source data cannot be directly mapped to our object dict, so
            we don't directly map any data items.  We will simply roll up
            all the defined properties.
        '''
        props = set([p for p in dir(self.__class__)
                     if isinstance(getattr(self.__class__, p),
                                   property)])

        return props

    def dict(self):
        items = []

        for p in self.get_interface_properties():
            k, v = p, getattr(self, p)

            if hasattr(v, '__iter__') and not hasattr(v, '__len__'):
                v = list(v)

            items.append((k, v))

        return dict(items)

    def _class_path(self, class_obj):
        return '{}.{}'.format(class_obj.__module__, class_obj.__name__)

    def _get_kwargs(self, obj):
        '''
            Since we want to interchangeably use a parser or a record for our
            source object, a common operation will be to guarantee that we are
            always working with a kwargs struct.
        '''
        if isinstance(obj, dict):
            return obj
        else:
            return obj.dict()

    def _get_record_attr(self, attr):
        try:
            return getattr(self.record, attr)
        except Exception:
            return self.record.get(attr)

    @property
    def status(self):
        '''
            The parser does not have this, but we will want to get/set
            this property.
        '''
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def categories(self):
        '''
            The parser does not have this, but we will want to get/set
            this property.
        '''
        return self._categories

    @categories.setter
    def categories(self, value):
        self._categories = value

    @property
    def name(self):
        '''
            Nothing special to do here.
        '''
        return self.record.oil_name

    @property
    def oil_id(self):
        '''
            Nothing special to do here.
        '''
        return self.record.oil_id

    @property
    def _id(self):
        '''
            Nothing special to do here.
        '''
        return self.oil_id

    @property
    def reference(self):
        '''
            Nothing special to do here.
        '''
        return self.record.reference

    @property
    def reference_date(self):
        '''
            Basically, our the oil library parser returns a four digit year.
            This needs to be turned into a DateTimeField somehow.
            We will choose Jan 1 of the year specified.
        '''
        rd = self.record.reference_date

        if rd is not None:
            return datetime(year=int(self.record.reference_date),
                            month=1, day=1)

    @property
    def comments(self):
        '''
            Nothing special to do here.
        '''
        return self.record.comments

    @property
    def location(self):
        '''
            Nothing special to do here.
        '''
        return self.record.location

    @property
    def product_type(self):
        '''
            Nothing special to do here.
        '''
        return self.record.product_type

    @property
    def apis(self):
        '''
            NOAA Filemaker has only one api value, and it is just a float
        '''
        if self.record.api is not None:
            yield {'gravity': float(self.record.api), 'weathering': 0.0}

    @property
    def densities(self):
        for d in self.record.densities:
            kwargs = self._get_kwargs(d)

            kwargs['density'] = {'value': kwargs['kg_m_3'],
                                 'unit': 'kg/m^3',
                                 '_cls': self._class_path(DensityUnit)}
            kwargs['ref_temp'] = {'value': kwargs['ref_temp_k'],
                                  'unit': 'K',
                                  '_cls': self._class_path(TemperatureUnit)}
            kwargs['weathering'] = float(kwargs.get('weathering', 0.0))

            del kwargs['kg_m_3'],
            del kwargs['ref_temp_k'],

            yield kwargs

    @property
    def dvis(self):
        for d in self.record.dvis:
            kwargs = self._get_kwargs(d)

            kwargs['viscosity'] = {
                'value': kwargs['kg_ms'],
                'unit': 'kg/(m s)',
                '_cls': self._class_path(DynamicViscosityUnit)}
            kwargs['ref_temp'] = {
                'value': kwargs['ref_temp_k'],
                'unit': 'K',
                '_cls': self._class_path(TemperatureUnit)}
            kwargs['weathering'] = float(kwargs.get('weathering', 0.0))

            del kwargs['kg_ms']
            del kwargs['ref_temp_k']

            yield kwargs

    @property
    def kvis(self):
        for k in self.record.kvis:
            kwargs = self._get_kwargs(k)

            kwargs['viscosity'] = {
                'value': kwargs['m_2_s'],
                'unit': 'm^2/s',
                '_cls': self._class_path(KinematicViscosityUnit)}
            kwargs['ref_temp'] = {
                'value': kwargs['ref_temp_k'],
                'unit': 'K',
                '_cls': self._class_path(TemperatureUnit)}
            kwargs['weathering'] = float(kwargs.get('weathering', 0.0))

            del kwargs['m_2_s']
            del kwargs['ref_temp_k']

            yield kwargs

    @property
    def ifts(self):
        for interface in ('water', 'seawater'):
            lbl = 'oil_{}_interfacial_tension'.format(interface)

            tension = self._get_record_attr('{}_n_m'.format(lbl))
            ref_temp = self._get_record_attr('{}_ref_temp_k'.format(lbl))

            if all([v is not None for v in (tension, ref_temp)]):
                kwargs = {}

                kwargs['tension'] = {
                    'value': tension, 'unit': 'N/m',
                    '_cls': self._class_path(InterfacialTensionUnit)}
                kwargs['ref_temp'] = {
                    'value': ref_temp, 'unit': 'K',
                    '_cls': self._class_path(TemperatureUnit)}
                kwargs['interface'] = interface

                yield kwargs

    @property
    def flash_points(self):
        min_temp = self._get_record_attr('flash_point_min_k')
        max_temp = self._get_record_attr('flash_point_max_k')

        kwargs = {}
        if (min_temp is not None and min_temp == max_temp):
            kwargs['ref_temp'] = {'value': min_temp, 'unit': 'K',
                                  '_cls': self._class_path(TemperatureUnit)}
        elif any([v is not None for v in (min_temp, max_temp)]):
            kwargs['ref_temp'] = {'min_value': min_temp, 'max_value': max_temp,
                                  'unit': 'K',
                                  '_cls': self._class_path(TemperatureUnit)}
        kwargs['weathering'] = 0.0

        if len(kwargs.keys()) > 0:
            yield kwargs

    @property
    def pour_points(self):
        min_temp = self._get_record_attr('pour_point_min_k')
        max_temp = self._get_record_attr('pour_point_max_k')

        kwargs = {}
        if (min_temp is not None and min_temp == max_temp):
            kwargs['ref_temp'] = {'value': min_temp, 'unit': 'K',
                                  '_cls': self._class_path(TemperatureUnit)}
        elif any([v is not None for v in (min_temp, max_temp)]):
            kwargs['ref_temp'] = {'min_value': min_temp, 'max_value': max_temp,
                                  'unit': 'K',
                                  '_cls': self._class_path(TemperatureUnit)}
        kwargs['weathering'] = 0.0

        if len(kwargs.keys()) > 0:
            yield kwargs

    @property
    def cuts(self):
        for c in self.record.cuts:
            kwargs = self._get_kwargs(c)

            liquid_temp = kwargs.get('liquid_temp_k')
            vapor_temp = kwargs.get('vapor_temp_k')
            fraction = kwargs.get('fraction')

            kwargs['fraction'] = {'value': fraction, 'unit': 'fraction',
                                  '_cls': self._class_path(FloatUnit)}
            kwargs['vapor_temp'] = {'value': vapor_temp, 'unit': 'K',
                                    '_cls': self._class_path(TemperatureUnit)}

            if liquid_temp is not None:
                kwargs['liquid_temp'] = {'value': liquid_temp, 'unit': 'K'}

            yield kwargs

    @property
    def adhesions(self):
        '''
            Note: We don't really know what the adhesion units are for the
                  NOAA Filemaker records.

                  Need to ask JeffL

                  Based on the range of numbers I am seeing, it kinda looks
                  like we are dealing with Pascals (N/m^2)
        '''
        adhesion = self._get_record_attr('adhesion')

        if adhesion is not None:
            kwargs = {}

            kwargs['adhesion'] = {'value': adhesion, 'unit': 'N/m^2',
                                  '_cls': self._class_path(AdhesionUnit)}

            yield kwargs

    @property
    def evaporation_eqs(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def emulsions(self):
        '''
            Oil Library records do have some attributes related to emulsions:
            - emuls_constant_min (???)
            - emuls_constant_max (???)
            - water_content_emulsion (probably maps to water_content)

            But it is not clear how to map this information to our emulsion
            object.  Basically we will just use the water content for now.

            - Age will be set to the day of formation
            - Temperature will be set to 15C (288.15K)
        '''
        water_content = self._get_record_attr('water_content_emulsion')

        if water_content is not None:
            kwargs = {}

            kwargs['water_content'] = {'value': water_content,
                                       'unit': 'fraction',
                                       '_cls': self._class_path(FloatUnit)}
            kwargs['age'] = {'value': 0.0, 'unit': 's',
                             '_cls': self._class_path(TimeUnit)}
            kwargs['ref_temp'] = {'value': 15.0,
                                  'from_unit': 'C', 'unit': 'K',
                                  '_cls': self._class_path(TemperatureUnit)}

            yield kwargs

    @property
    def chemical_dispersibility(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def sulfur(self):
        sulfur = self._get_record_attr('sulphur')

        if sulfur is not None:
            kwargs = {}

            kwargs['fraction'] = {'value': sulfur, 'unit': 'fraction',
                                  '_cls': self._class_path(FloatUnit)}

            yield kwargs

    @property
    def water(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def wax_content(self):
        wax = self._get_record_attr('wax_content')

        if wax is not None:
            kwargs = {}

            kwargs['fraction'] = {'value': wax, 'unit': 'fraction',
                                  '_cls': self._class_path(FloatUnit)}

            yield kwargs

    @property
    def benzene(self):
        benzene_content = self._get_record_attr('benzene')

        if benzene_content is not None:
            kwargs = {}

            kwargs['benzene'] = {'value': benzene_content, 'unit': 'fraction',
                                 '_cls': self._class_path(FloatUnit)}

            yield kwargs

    @property
    def headspace(self):
        '''
            N/A. Oil Library records don't have this.  So we form a generator
            function that returns an empty iterator
        '''
        if False:
            yield None

    @property
    def chromatography(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def ccme(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def ccme_f1(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def ccme_f2(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def ccme_tph(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def sara_total_fractions(self):
        for sara_type in ('Saturates', 'Aromatics', 'Resins', 'Asphaltenes'):
            fraction = self._get_record_attr(sara_type.lower())

            if fraction is not None:
                kwargs = {}

                kwargs['fraction'] = {'value': fraction, 'unit': 'fraction',
                                      '_cls': self._class_path(FloatUnit)}
                kwargs['sara_type'] = sara_type

                yield kwargs

    @property
    def alkanes(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def alkylated_pahs(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def biomarkers(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        if False:
            yield None

    @property
    def toxicities(self):
        '''
            This is unique to the NOAA Filemaker records
        '''
        for tox in self.record.toxicities:
            kwargs = self._get_kwargs(tox)

            # Note: we will maybe want to specify the units of concentration,
            #       but I am not sure what the units are.  PPM maybe?
            #       For now, we will just store the numbers.

            after_24h = kwargs.get('after_24h')
            after_48h = kwargs.get('after_48h')
            after_96h = kwargs.get('after_96h')

            if any([c is not None
                    for c in (after_24h, after_48h, after_96h)]):
                yield kwargs

    @property
    def conradson(self):
        '''
            This is unique to the NOAA Filemaker records
        '''
        residue = self._get_record_attr('conrandson_residuum')
        crude = self._get_record_attr('conrandson_crude')

        if any([a is not None for a in (residue, crude)]):
            kwargs = {}
            if residue is not None:
                kwargs['residue'] = {'value': residue, 'unit': 'fraction',
                                     '_cls': self._class_path(FloatUnit)}

            if crude is not None:
                kwargs['crude'] = {'value': crude, 'unit': 'fraction',
                                   '_cls': self._class_path(FloatUnit)}

            yield kwargs
