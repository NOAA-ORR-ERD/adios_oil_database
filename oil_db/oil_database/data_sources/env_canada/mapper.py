#!/usr/bin/env python
import logging

from oil_database.models.common.float_unit import TemperatureUnit, DensityUnit

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)

logger = logging.getLogger(__name__)


class EnvCanadaAttributeMapper(object):
    '''
        A translation/conversion layer for the Environment Canada imported
        record object.
        This is intended to be used interchangeably with either an Environment
        Canada record or record parser object.  Its purpose is to generate
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

    @property
    def name(self):
        '''
            Nothing special to do here.
        '''
        return self.record.name

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
            Nothing special to do here.
        '''
        return self.record.reference_date

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
        for a in self.record.apis:
            yield self._get_kwargs(a)

    @property
    def densities(self):
        for d in self.record.densities:
            kwargs = self._get_kwargs(d)
            print 'kwargs: ', kwargs
            kwargs['density'] = DensityUnit(value=kwargs['g_ml'],
                                            unit='kg/m^3', from_unit='g/mL')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_c'],
                                                 unit='K', from_unit='C')

            yield kwargs

    @property
    def dvis(self):
        for d in self.record.dvis:
            yield self._get_kwargs(d)

    @property
    def ifts(self):
        for i in self.record.ifts:
            yield self._get_kwargs(i)

    @property
    def flash_points(self):
        for f in self.record.flash_points:
            yield self._get_kwargs(f)

    @property
    def pour_points(self):
        for p in self.record.pour_points:
            yield self._get_kwargs(p)

    @property
    def cuts(self):
        for c in self.record.cuts:
            yield self._get_kwargs(c)

    @property
    def adhesions(self):
        for a in self.record.adhesions:
            yield self._get_kwargs(a)

    @property
    def evaporation_eqs(self):
        for e in self.record.evaporation_eqs:
            yield self._get_kwargs(e)

    @property
    def emulsions(self):
        for e in self.record.emulsions:
            yield self._get_kwargs(e)

    @property
    def corexit(self):
        for c in self.record.corexit:
            yield self._get_kwargs(c)

    @property
    def sulfur(self):
        for s in self.record.sulfur:
            yield self._get_kwargs(s)

    @property
    def water(self):
        for w in self.record.water:
            yield self._get_kwargs(w)

    @property
    def wax_content(self):
        for w in self.record.wax_content:
            yield self._get_kwargs(w)

    @property
    def sara_total_fractions(self):
        for f in self.record.sara_total_fractions:
            yield self._get_kwargs(f)

    @property
    def benzene(self):
        for b in self.record.benzene:
            yield self._get_kwargs(b)

    @property
    def headspace(self):
        for h in self.record.headspace:
            yield self._get_kwargs(h)

    @property
    def chromatography(self):
        for c in self.record.chromatography:
            yield self._get_kwargs(c)

    @property
    def ccme(self):
        for c in self.record.ccme:
            yield self._get_kwargs(c)

    @property
    def ccme_f1(self):
        for c in self.record.ccme_f1:
            yield self._get_kwargs(c)

    @property
    def ccme_f2(self):
        for c in self.record.ccme_f2:
            yield self._get_kwargs(c)

    @property
    def ccme_tph(self):
        for c in self.record.ccme_tph:
            yield self._get_kwargs(c)

    @property
    def alkylated_pahs(self):
        for a in self.record.alkylated_pahs:
            yield self._get_kwargs(a)

    @property
    def alkanes(self):
        for a in self.record.alkanes:
            yield self._get_kwargs(a)

    @property
    def biomarkers(self):
        for b in self.record.biomarkers:
            yield self._get_kwargs(b)
