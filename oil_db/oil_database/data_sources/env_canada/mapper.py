#!/usr/bin/env python
import logging

from oil_database.models.common.float_unit import (FloatUnit,
                                                   TimeUnit,
                                                   TemperatureUnit,
                                                   DensityUnit,
                                                   DynamicViscosityUnit,
                                                   InterfacialTensionUnit,
                                                   AdhesionUnit,
                                                   ConcentrationInWaterUnit)

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

            kwargs['density'] = DensityUnit(value=kwargs['g_ml'],
                                            from_unit='g/mL', unit='kg/m^3')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_c'],
                                                 from_unit='C', unit='K')

            yield kwargs

    @property
    def dvis(self):
        for d in self.record.dvis:
            kwargs = self._get_kwargs(d)

            kwargs['viscosity'] = DynamicViscosityUnit(value=kwargs['mpa_s'],
                                                       from_unit='mPa.s',
                                                       unit='kg/(m s)')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_c'],
                                                 from_unit='C', unit='K')

            yield kwargs

    @property
    def ifts(self):
        for i in self.record.ifts:
            kwargs = self._get_kwargs(i)

            kwargs['tension'] = InterfacialTensionUnit(value=kwargs['dynes_cm'],
                                                       from_unit='dyne/cm',
                                                       unit='N/m')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_c'],
                                                 from_unit='C', unit='K')

            yield kwargs

    @property
    def flash_points(self):
        for f in self.record.flash_points:
            kwargs = self._get_kwargs(f)

            min_temp, max_temp = kwargs['min_temp_c'], kwargs['max_temp_c']

            if min_temp is not None:
                kwargs['min_temp'] = TemperatureUnit(value=min_temp,
                                                     from_unit='C', unit='K')

            if max_temp is not None:
                kwargs['max_temp'] = TemperatureUnit(value=max_temp,
                                                     from_unit='C', unit='K')

            yield kwargs

    @property
    def pour_points(self):
        for p in self.record.pour_points:
            kwargs = self._get_kwargs(p)

            min_temp, max_temp = kwargs['min_temp_c'], kwargs['max_temp_c']

            if min_temp is not None:
                kwargs['min_temp'] = TemperatureUnit(value=min_temp,
                                                     from_unit='C', unit='K')

            if max_temp is not None:
                kwargs['max_temp'] = TemperatureUnit(value=max_temp,
                                                     from_unit='C', unit='K')

            yield kwargs

    @property
    def cuts(self):
        for c in self.record.cuts:
            kwargs = self._get_kwargs(c)

            kwargs['fraction'] = FloatUnit(value=kwargs['percent'] / 100.0,
                                           unit='1')
            kwargs['vapor_temp'] = TemperatureUnit(value=kwargs['temp_c'],
                                                   from_unit='C', unit='K')

            yield kwargs

    @property
    def adhesions(self):
        for a in self.record.adhesions:
            kwargs = self._get_kwargs(a)

            kwargs['adhesion'] = AdhesionUnit(value=kwargs['g_cm_2'],
                                              from_unit='g/cm^2', unit='N/m^2')

            yield kwargs

    @property
    def evaporation_eqs(self):
        for e in self.record.evaporation_eqs:
            yield self._get_kwargs(e)

    @property
    def emulsions(self):
        for e in self.record.emulsions:
            kwargs = self._get_kwargs(e)

            kwargs['water_content'] = FloatUnit(value=kwargs['water_content_percent'] / 100.0,
                                                unit='1')
            kwargs['age'] = TimeUnit(value=kwargs['age_days'],
                                     from_unit='day', unit='s')
            kwargs['ref_temp'] = TemperatureUnit(value=kwargs['ref_temp_c'],
                                                 from_unit='C', unit='K')

            # the different modulus values have similar units of measure
            # to adhesion, so this is what we will go with
            for mod_lbl in ('complex_modulus_pa',
                            'storage_modulus_pa',
                            'loss_modulus_pa'):
                value = kwargs[mod_lbl]
                new_lbl = mod_lbl[:-3]

                if value is not None:
                    kwargs[new_lbl] = AdhesionUnit(value=value,
                                                   from_unit='Pa',
                                                   unit='N/m^2')

            for visc_lbl in ('complex_viscosity_pa_s',):
                value = kwargs[visc_lbl]
                new_lbl = visc_lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = DynamicViscosityUnit(value=value,
                                                           from_unit='Pa.s',
                                                           unit='kg/(m s)')

            yield kwargs

    @property
    def corexit(self):
        for c in self.record.corexit:
            kwargs = self._get_kwargs(c)

            kwargs['effectiveness'] = FloatUnit(value=kwargs['effectiveness_percent'] / 100.0,
                                                unit='1')

            yield kwargs

    @property
    def sulfur(self):
        for s in self.record.sulfur:
            kwargs = self._get_kwargs(s)

            kwargs['fraction'] = FloatUnit(value=kwargs['percent'] / 100.0,
                                           unit='1')

            yield kwargs

    @property
    def water(self):
        for w in self.record.water:
            kwargs = self._get_kwargs(w)

            kwargs['fraction'] = FloatUnit(value=kwargs['percent'] / 100.0,
                                           unit='1')

            yield kwargs

    @property
    def wax_content(self):
        for w in self.record.wax_content:
            kwargs = self._get_kwargs(w)

            kwargs['fraction'] = FloatUnit(value=kwargs['percent'] / 100.0,
                                           unit='1')

            yield kwargs

    @property
    def benzene(self):
        for b in self.record.benzene:
            kwargs = self._get_kwargs(b)

            for lbl in ('benzene_ug_g',
                        'toluene_ug_g',
                        'ethylbenzene_ug_g',
                        'm_p_xylene_ug_g',
                        'o_xylene_ug_g',
                        'isopropylbenzene_ug_g',
                        'propylebenzene_ug_g',
                        'isobutylbenzene_ug_g',
                        'amylbenzene_ug_g',
                        'n_hexylbenzene_ug_g',
                        '_1_2_3_trimethylbenzene_ug_g',
                        '_1_2_4_trimethylbenzene_ug_g',
                        '_1_2_dimethyl_4_ethylbenzene_ug_g',
                        '_1_3_5_trimethylbenzene_ug_g',
                        '_1_methyl_2_isopropylbenzene_ug_g',
                        '_2_ethyltoluene_ug_g',
                        '_3_4_ethyltoluene_ug_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='ug/g',
                                                               unit='ppm')

            yield kwargs

    @property
    def headspace(self):
        for h in self.record.headspace:
            kwargs = self._get_kwargs(h)

            for lbl in ('n_c5_mg_g',
                        'n_c6_mg_g',
                        'n_c7_mg_g',
                        'n_c8_mg_g',
                        'c5_group_mg_g',
                        'c6_group_mg_g',
                        'c7_group_mg_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='mg/g',
                                                               unit='ppm')

            yield kwargs

    @property
    def chromatography(self):
        for c in self.record.chromatography:
            kwargs = self._get_kwargs(c)

            for lbl in ('tph_mg_g',
                        'tsh_mg_g',
                        'tah_mg_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='mg/g',
                                                               unit='1')

            for lbl in ('tsh_tph_percent',
                        'tah_tph_percent',
                        'resolved_peaks_tph_percent'):
                value = kwargs[lbl]
                new_lbl = lbl[:-8]

                if value is not None:
                    kwargs[new_lbl] = FloatUnit(value=value / 100.0,
                                                unit='1')

            yield kwargs

    @property
    def ccme(self):
        for c in self.record.ccme:
            kwargs = self._get_kwargs(c)

            for n in range(1, 5):
                lbl, new_lbl = 'f{}_mg_g'.format(n), 'f{}'.format(n)
                value = kwargs[lbl]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='mg/g',
                                                               unit='1')

            yield kwargs

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
    def sara_total_fractions(self):
        for f in self.record.sara_total_fractions:
            kwargs = self._get_kwargs(f)

            kwargs['fraction'] = FloatUnit(value=kwargs['percent'] / 100.0,
                                           unit='1')

            yield kwargs

    @property
    def alkanes(self):
        for a in self.record.alkanes:
            kwargs = self._get_kwargs(a)

            for lbl in ('pristane_ug_g', 'phytane_ug_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='ug/g',
                                                               unit='ppm')

            for n in range(8, 45):
                lbl, new_lbl = 'c{}_ug_g'.format(n), 'c{}'.format(n)
                value = kwargs[lbl]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='ug/g',
                                                               unit='ppm')

            yield kwargs

    @property
    def alkylated_pahs(self):
        for a in self.record.alkylated_pahs:
            kwargs = self._get_kwargs(a)

            for i, g in [(i, g) for g in 'npdfbc' for i in range(5)]:
                lbl, new_lbl = ('c{}_{}_ug_g'.format(i, g),
                                'c{}_{}'.format(i, g))
                value = kwargs.get(lbl, None)

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='ug/g',
                                                               unit='ppm')

            for lbl in ('biphenyl_ug_g',
                        'acenaphthylene_ug_g',
                        'acenaphthene_ug_g',
                        'anthracene_ug_g',
                        'fluoranthene_ug_g',
                        'pyrene_ug_g',
                        'benz_a_anthracene_ug_g',
                        'benzo_b_fluoranthene_ug_g',
                        'benzo_k_fluoranthene_ug_g',
                        'benzo_e_pyrene_ug_g',
                        'benzo_a_pyrene_ug_g',
                        'perylene_ug_g',
                        'indeno_1_2_3_cd_pyrene_ug_g',
                        'dibenzo_ah_anthracene_ug_g',
                        'benzo_ghi_perylene_ug_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='ug/g',
                                                               unit='ppm')

            yield kwargs

    @property
    def biomarkers(self):
        for b in self.record.biomarkers:
            kwargs = self._get_kwargs(b)

            for lbl in ('c21_tricyclic_terpane_ug_g',
                        'c22_tricyclic_terpane_ug_g',
                        'c23_tricyclic_terpane_ug_g',
                        'c24_tricyclic_terpane_ug_g',
                        '_30_norhopane_ug_g',
                        'hopane_ug_g',
                        '_30_homohopane_22s_ug_g',
                        '_30_homohopane_22r_ug_g',
                        '_30_31_bishomohopane_22s_ug_g',
                        '_30_31_bishomohopane_22r_ug_g',
                        '_30_31_trishomohopane_22s_ug_g',
                        '_30_31_trishomohopane_22r_ug_g',
                        'tetrakishomohopane_22s_ug_g',
                        'tetrakishomohopane_22r_ug_g',
                        'pentakishomohopane_22s_ug_g',
                        'pentakishomohopane_22r_ug_g',
                        '_18a_22_29_30_trisnorneohopane_ug_g',
                        '_17a_h_22_29_30_trisnorhopane_ug_g',
                        '_14b_h_17b_h_20_cholestane_ug_g',
                        '_14b_h_17b_h_20_methylcholestane_ug_g',
                        '_14b_h_17b_h_20_ethylcholestane_ug_g'):
                value = kwargs[lbl]
                new_lbl = lbl[:-5]

                if value is not None:
                    kwargs[new_lbl] = ConcentrationInWaterUnit(value=value,
                                                               from_unit='ug/g',
                                                               unit='ppm')

            yield kwargs
