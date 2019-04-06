#!/usr/bin/env python
import logging
from datetime import date

from oil_database.models.common.float_unit import (FloatUnit,
                                                   TimeUnit,
                                                   TemperatureUnit,
                                                   DensityUnit,
                                                   DynamicViscosityUnit,
                                                   KinematicViscosityUnit,
                                                   InterfacialTensionUnit,
                                                   AdhesionUnit,
                                                   ConcentrationInWaterUnit)

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

    def _get_kwargs(self, obj):
        '''
            Since we want to interchangeably use a parser or a record for our
            source object, a common operation will be to guarantee that we are
            always working with a kwargs struct.
        '''
        if isinstance(obj, dict):
            return obj
        else:
            return obj.to_son().to_dict()

    def _get_record_attr(self, attr):
        try:
            return getattr(self.record, attr)
        except Exception:
            return self.record.get(attr, None)

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
            return date(year=int(self.record.reference_date),
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
            yield {'gravity': self.record.api}

    @property
    def densities(self):
        for d in self.record.densities:
            kwargs = self._get_kwargs(d)

            kwargs['density'] = DensityUnit(value=kwargs['kg_m_3'],
                                            unit='kg/m^3')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_k'],
                                                 unit='K')

            yield kwargs

    @property
    def dvis(self):
        for d in self.record.dvis:
            kwargs = self._get_kwargs(d)

            kwargs['viscosity'] = DynamicViscosityUnit(value=kwargs['kg_ms'],
                                                       unit='kg/(m s)')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_k'],
                                                 unit='K')

            yield kwargs

    @property
    def kvis(self):
        for k in self.record.kvis:
            kwargs = self._get_kwargs(k)

            kwargs['viscosity'] = KinematicViscosityUnit(value=kwargs['m_2_s'],
                                                         unit='m^2/s')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_k'],
                                                 unit='K')

            yield kwargs

    @property
    def ifts(self):
        for interface in ('water', 'seawater'):
            lbl = 'oil_{}_interfacial_tension'.format(interface)

            tension = self._get_record_attr('{}_n_m'.format(lbl))
            ref_temp = self._get_record_attr('{}_ref_temp_k'.format(lbl))

            if all([v is not None for v in (tension, ref_temp)]):
                kwargs = {}

                kwargs['tension'] = InterfacialTensionUnit(value=tension,
                                                           unit='N/m')
                kwargs['ref_temp'] = TemperatureUnit(value=ref_temp, unit='K')
                kwargs['interface'] = interface

                yield kwargs

    @property
    def flash_points(self):
        min_temp = self._get_record_attr('flash_point_min_k')
        max_temp = self._get_record_attr('flash_point_max_k')

        if any([v is not None for v in (min_temp, max_temp)]):
            kwargs = {}

            if min_temp is not None:
                kwargs['min_temp'] = TemperatureUnit(value=min_temp, unit='K')

            if max_temp is not None:
                kwargs['max_temp'] = TemperatureUnit(value=max_temp, unit='K')

            yield kwargs

    @property
    def pour_points(self):
        min_temp = self._get_record_attr('pour_point_min_k')
        max_temp = self._get_record_attr('pour_point_max_k')

        if any([v is not None for v in (min_temp, max_temp)]):
            kwargs = {}

            if min_temp is not None:
                kwargs['min_temp'] = TemperatureUnit(value=min_temp, unit='K')

            if max_temp is not None:
                kwargs['max_temp'] = TemperatureUnit(value=max_temp, unit='K')

            yield kwargs

    @property
    def cuts(self):
        for c in self.record.cuts:
            kwargs = self._get_kwargs(c)

            liquid_temp = kwargs.get('liquid_temp_k', None)
            vapor_temp = kwargs.get('vapor_temp_k', None)
            fraction = kwargs.get('fraction', None)

            kwargs['fraction'] = FloatUnit(value=fraction, unit='1')
            kwargs['vapor_temp'] = TemperatureUnit(value=vapor_temp, unit='K')

            if liquid_temp is not None:
                kwargs['liquid_temp'] = TemperatureUnit(value=liquid_temp,
                                                        unit='K')

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

            kwargs['adhesion'] = AdhesionUnit(value=adhesion, unit='N/m^2')

            yield kwargs

    @property
    def evaporation_eqs(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

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

            kwargs['water_content'] = FloatUnit(value=water_content, unit='1')
            kwargs['age'] = TimeUnit(value=0.0, unit='s')
            kwargs['ref_temp'] = TemperatureUnit(value=15.0,
                                                 from_unit='C', unit='K')

            yield kwargs

    @property
    def corexit(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def sulfur(self):
        sulfur = self._get_record_attr('sulphur')

        if sulfur is not None:
            kwargs = {}

            kwargs['fraction'] = FloatUnit(value=sulfur,
                                           unit='1')

            yield kwargs

    @property
    def water(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def wax_content(self):
        wax = self._get_record_attr('wax_content')

        if wax is not None:
            kwargs = {}

            kwargs['fraction'] = FloatUnit(value=wax, unit='1')

            yield kwargs

    @property
    def benzene(self):
        benzene_content = self._get_record_attr('benzene')

        if benzene_content is not None:
            kwargs = {}

            kwargs['benzene'] = ConcentrationInWaterUnit(value=benzene_content,
                                                         unit='1')

            yield kwargs

    @property
    def headspace(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def chromatography(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def ccme(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def ccme_f1(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def ccme_f2(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def ccme_tph(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def sara_total_fractions(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def alkanes(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def alkylated_pahs(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass

    @property
    def biomarkers(self):
        '''
            N/A. Oil Library records don't have this.
        '''
        pass
