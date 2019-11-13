'''
    These are functions to be used primarily for estimating oil
    properties that are contained within an oil record that has been
    queried from the oil database.
'''
from importlib import import_module

import numpy as np
from scipy.optimize import curve_fit

from oil_database.util import estimations as est
from oil_database.util.json import ObjFromDict

from oil_database.models.common.float_unit import (TemperatureUnit,
                                                   DensityUnit,
                                                   DynamicViscosityUnit,
                                                   KinematicViscosityUnit)

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)


def _linear_curve(x, a, b):
    '''
        Here we describe the form of a linear function for the purpose of
        curve-fitting measured data points.
    '''
    return (a * x + b)


def _inverse_linear_curve(y, a, b, M, zeta=0.12):
    y_c = clamp(y, M, zeta)

    return (y_c - b) / a


def clamp(x, M, zeta=0.03):
    '''
        We make use of a generalized logistic function or Richard's curve
        to generate a linear function that is clamped at x == M.
        We make use of a zeta value to tune the parameters nu, resulting in a
        smooth transition as we cross the M boundary.
    '''
    return (x -
            (x / (1.0 + np.e ** (-15 * (x - M))) ** (1.0 / (1 + zeta))) +
            (M / (1.0 + np.e ** (-15 * (x - M))) ** (1.0 / (1 - zeta))))


class OilEstimation(object):
    '''
        In order to provide minimal overhead, we will be setting this up as a
        group of interface classes that can be used a la carte.
        There will of course be some dependency between these, which we will
        attempt to document.

        All interfaces assume a self.record member, which is the contained
        oil object.
    '''
    def __init__(self, imported_rec):
        if hasattr(imported_rec, 'dict'):
            # we are dealing with a mapper object, convert to data object
            self.record = imported_rec.dict()
        else:
            self.record = imported_rec

        # convert our record dict into an obj with attributes
        self.record = ObjFromDict(self._add_float_units(self.record))

        try:
            self.record.name  # simply access the name to see if it is there
        except Exception as e:
            try:
                self.record.oil_name
            except Exception:
                raise ValueError(e)

    def __repr__(self):
        try:
            return ('<{0}({1.name})>'
                    .format(self.__class__.__name__, self.record))
        except Exception:
            return ('<{0}({1.oil_name})>'
                    .format(self.__class__.__name__, self.record))

    def _add_float_units(self, data):
        if isinstance(data, (tuple, list, set, frozenset)):
            return type(data)([self._add_float_units(v) for v in data])
        if (isinstance(data, dict) and
                '_cls' in data and
                any([(k in data)
                     for k in ('value', 'max_value', 'min_value')])):
            # create a FloatUnit type from our struct
            class_name = data['_cls']
            del data['_cls']
            py_class = self.py_class_from_name(class_name)
            return py_class(**data)
        elif isinstance(data, dict):
            return dict([(k, self._add_float_units(v))
                         for k, v in data.items()])
        else:
            return data

    def py_class_from_name(self, fully_qualified_name):
        name, scope = self.fq_name_to_name_and_scope(fully_qualified_name)
        module = import_module(scope)

        return getattr(module, name)

    def fq_name_to_name_and_scope(self, fully_qualified_name):
        fqn = fully_qualified_name

        return (list(reversed(fqn.rsplit('.', 1)))
                if fqn.find('.') >= 0
                else [fqn, ''])

    def __getattr__(self, name):
        return getattr(self.record, name, None)

    def get_sample(self, sample_id='w=0.0'):
        '''
            sample_id will normally indicate a weathering amount, but
            there will be cases where it will indicate something else,
            such as distiallate fraction.
            We will default to a weathering amount of 0.0 (fresh)

            There will most likely not be multiple fresh samples, but in this
            case we just choose the first one.
        '''
        try:
            samples = [s for s in self.record.samples
                       if s.sample_id == sample_id]
        except Exception:
            return None

        return OilSampleEstimation(samples[0]) if len(samples) > 0 else None


class OilSampleEstimation(object):
    def __init__(self, sample):
        '''
            We expect a sample that has already been treated by our
            OilEstimation class
        '''
        self.record = sample
        self._k_v2 = None

    def __getattr__(self, name):
        return getattr(self.record, name, None)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.record == other.record
        else:
            return False

    @classmethod
    def lowest_temperature(cls, obj_list):
        '''
            General utility function.

            From a list of objects containing a ref_temp attribute,
            return the object that has the lowest temperature
        '''
        try:
            return sorted(obj_list, key=lambda d: d.ref_temp.value)[0]
        except (AttributeError, IndexError):
            return None

    @classmethod
    def closest_to_temperature(cls, obj_list, temperature, num=1):
        '''
            General Utility Function

            From a list of objects containing a ref_temp attribute,
            return the object(s) that are closest to the specified
            temperature(s)

            We accept only a scalar temperature or a sequence of temperatures
            We expect temperatures in Kelvin
        '''
        if hasattr(temperature, '__iter__'):
            # we like to deal with numpy arrays as opposed to simple iterables
            temp_k = np.array(temperature)
        else:
            temp_k = temperature

        # our requested number of objs can have a range [0 ... listsize-1]
        if num >= len(obj_list):
            num = len(obj_list) - 1

        temp_diffs = np.array([abs(obj.ref_temp.to_unit('K').value - temp_k)
                               for obj in obj_list]).T

        if len(obj_list) <= 1:
            return obj_list
        else:
            # we probably don't really need this for such a short list,
            # but we use a numpy 'introselect' partial sort method for speed
            try:
                # temp_diffs for sequence of temps
                closest_idx = np.argpartition(temp_diffs, num)[:, :num]
            except IndexError:
                # temp_diffs for single temp
                closest_idx = np.argpartition(temp_diffs, num)[:num]

            try:
                # sequence of temperatures result
                closest = [sorted([obj_list[i] for i in r],
                                  key=lambda x: x.ref_temp.to_unit('K').value)
                           for r in closest_idx]
            except TypeError:
                # single temperature result
                closest = sorted([obj_list[i] for i in closest_idx],
                                 key=lambda x: x.ref_temp.to_unit('K').value)

            return closest

    @classmethod
    def bounding_temperatures(cls, obj_list, temperature):
        '''
            General Utility Function

            From a list of objects containing a ref_temp attribute,
            return the object(s) that are closest to the specified
            temperature(s)
            specifically:
            - we want the ones that immediately bound our temperature.
            - if our temperature is high and out of bounds of the temperatures
              in our obj_list, then we return a range containing only the
              highest temperature.
            - if our temperature is low and out of bounds of the temperatures
              in our obj_list, then we return a range containing only the
              lowest temperature.

            We accept only a scalar temperature or a sequence of temperatures
            We expect temperatures in Kelvin
        '''
        temperature = np.array(temperature).reshape(-1, 1)

        if len(obj_list) <= 1:
            # range where the lowest and highest are basically the same.
            obj_list *= 2

        geq_temps = temperature >= [obj.ref_temp.to_unit('K').value
                                    for obj in obj_list]

        if geq_temps.shape[-1] == 0:
            return []

        high_and_oob = np.all(geq_temps, axis=1)
        low_and_oob = np.all(geq_temps ^ True, axis=1)

        rho_idxs0 = np.argmin(geq_temps, axis=1)
        rho_idxs0[rho_idxs0 > 0] -= 1
        rho_idxs0[high_and_oob] = len(obj_list) - 1

        rho_idxs1 = (rho_idxs0 + 1).clip(0, len(obj_list) - 1)
        rho_idxs1[low_and_oob] = 0

        return list(zip([obj_list[i] for i in rho_idxs0],
                        [obj_list[i] for i in rho_idxs1]))

    def pour_point(self, estimate_if_none=True):
        '''
            Note: there is a catch-22 which puts us in an infinite loop
                  in some cases:
                  - to estimate pour point, we need viscosities
                  - if we need to convert dynamic viscosities to
                    kinematic, we need density at 15C
                  - to estimate density at temp, we need to estimate pour point
                  - ...and then we recurse

                  For this case we need to make an exception.  I think we can
                  add a flag here to bypass estimation and just give the
                  data values.  This flag will default to True, since most
                  users will want to estimate values if none are present.
                  But internally, we will want the option to turn estimation
                  off.
        '''
        min_k = max_k = None

        try:
            pp_temp = self.record.pour_points[0].ref_temp.to_unit('K')

            if hasattr(pp_temp, 'min_value') and pp_temp.min_value is not None:
                min_k = pp_temp.min_value
            else:
                min_k = pp_temp.value

            if hasattr(pp_temp, 'max_value') and pp_temp.max_value is not None:
                max_k = pp_temp.max_value
            else:
                max_k = pp_temp.value
        except AttributeError:
            pass

        if (min_k is None and max_k is None and estimate_if_none is True):
            lowest_kvis = self.lowest_temperature(self.aggregate_kvis())
            if lowest_kvis is not None:
                kvis, temp_k = (lowest_kvis.viscosity.to_unit('m^2/s').value,
                                lowest_kvis.ref_temp.to_unit('K').value)
                max_k = est.pour_point_from_kvis(kvis, temp_k)

        return min_k, max_k

    def flash_point(self):
        min_k = max_k = None

        try:
            fp_temp = self.record.flash_points[0].ref_temp.to_unit('K')

            min_k = fp_temp.min_value
            max_k = fp_temp.max_value
        except Exception:
            pass

        if min_k is None and max_k is None:
            max_k = self.flash_point_from_bp()

            if max_k is None:
                max_k = self.flash_point_from_api()

        return min_k, max_k

    def flash_point_from_bp(self):
        if hasattr(self.record, 'cuts') and len(self.record.cuts) > 2:
            cut_temps = self.get_cut_temps()
            return est.flash_point_from_bp(cut_temps[0])
        else:
            return None

    def flash_point_from_api(self):
        if hasattr(self.record, 'apis') and len(self.record.apis) > 0:
            return est.flash_point_from_api(self.get_api().gravity)
        if hasattr(self.record, 'densities') and len(self.get_densities()) > 0:
            est_api = est.api_from_density(self.density_at_temp(273.15 + 15))
            return est.flash_point_from_api(est_api)
        else:
            return None

    def get_api(self):
        '''
            There should only be a single API value per weathered sample.
            We return the object, not just the value
        '''
        try:
            apis = self.record.apis
        except AttributeError:
            apis = []

        return apis[0] if len(apis) > 0 else None

    def get_api_from_densities(self):
        if len(self.get_densities()) > 0:
            return est.api_from_density(self.density_at_temp(273.15 + 15))
        else:
            return None

    def get_densities(self):
        '''
            return a list of densities for the oil sample.
            We include the API as a density if:
            - the culled list of densities does not contain a measurement
              at 15C
        '''
        try:
            densities = self.record.densities
        except AttributeError:
            densities = []

        api = self.get_api()

        if (api is not None and
                len([d for d in densities
                     if np.isclose(d.ref_temp.value, 288.0, atol=1.0)]) == 0):
            kg_m_3, ref_temp_k = est.density_from_api(api.gravity)

            densities.append(ObjFromDict({
                'density': DensityUnit(value=kg_m_3, unit='kg/m^3'),
                'ref_temp': TemperatureUnit(value=ref_temp_k, unit='K')
            }))

        return sorted(densities, key=lambda d: d.ref_temp.value)

    def density_at_temp(self, temperature=288.15):
        '''
            Get the oil density at a temperature or temperatures.

            Note: there is a catch-22 which prevents us from getting
                  the min_temp in all casees:
                  - to estimate pour point, we need viscosities
                  - if we need to convert dynamic viscosities to
                    kinematic, we need density at 15C
                  - to estimate density at temp, we need to estimate pour point
                  - ...and then we recurse
                  For this case we need to make an exception.  I think we can
                  add a flag to self.pour_point() to bypass estimation and just
                  give the data values.
            Note: If we have a pour point that is higher than one or more
                  of our reference temperatures, then the lowest reference
                  temperature will become our minimum temperature.
        '''
        shape = None
        densities = self.get_densities()

        if len(densities) == 0:
            return None

        pp_min_k, pp_max_k = self.pour_point(estimate_if_none=False)

        # set the minimum temperature to be the oil's pour point
        if pp_min_k is not None or pp_max_k is not None:
            min_k = np.min([d.ref_temp.to_unit('K').value
                            for d in densities] +
                           [pp for pp in (pp_min_k, pp_max_k)
                            if pp is not None])
        elif (hasattr(self.record, 'dvis') and len(self.record.dvis) > 0):
            min_k = 0.0  # effectively no restriction
        else:
            min_k = 0.0  # effectively no restriction

        if hasattr(temperature, '__iter__'):
            temperature = np.clip(temperature, min_k, 1000.0)
            shape = temperature.shape
            temperature = temperature.reshape(-1)
        else:
            temperature = min_k if temperature < min_k else temperature

        ref_density, ref_temp_k = self._get_reference_densities(densities,
                                                                temperature)
        k_rho_t = self._vol_expansion_coeff(densities, temperature)

        rho_t = est.density_at_temp(ref_density, ref_temp_k,
                                    temperature, k_rho_t)

        if len(rho_t) == 1:
            return rho_t[0]
        elif shape is not None:
            return rho_t.reshape(shape)
        else:
            return rho_t

    @property
    def standard_density(self):
        '''
            Standard density is simply the density at 15C, which is the
            default temperature for density_at_temp()
        '''
        return self.density_at_temp()

    def _vol_expansion_coeff(self, densities, temperature):
        closest_densities = self.bounding_temperatures(densities, temperature)

        temperature = np.array(temperature)
        closest_values = np.array([[(d.density.to_unit('kg/m^3').value,
                                     d.ref_temp.to_unit('K').value)
                                    for d in r]
                                   for r in closest_densities])

        args_list = [[t for d in v for t in d]
                     for v in closest_values]
        k_rho_t = np.array([est.vol_expansion_coeff(*args)
                            for args in args_list])

        greater_than = np.all((temperature > closest_values[:, :, 1].T).T,
                              axis=1)
        less_than = np.all((temperature < closest_values[:, :, 1].T).T,
                           axis=1)

        api = self.get_api()

        if api is not None and api.gravity > 30:
            k_rho_default = 0.0009
        else:
            k_rho_default = 0.0008

        k_rho_t[greater_than | less_than] = k_rho_default

        if k_rho_t.shape[0] == 1:
            return k_rho_t[0]
        else:
            return k_rho_t

    def _get_reference_densities(self, densities, temperature):
        '''
            Given a temperature, we return the best measured density,
            and its reference temperature, to be used in calculation.

            For our purposes, it is the density closest to the given
            temperature.
        '''
        closest_densities = self.bounding_temperatures(densities, temperature)

        try:
            # sequence of ranges
            densities = np.array([[d.density.to_unit('kg/m^3').value
                                   for d in r]
                                  for r in closest_densities])
            ref_temps = np.array([[d.ref_temp.to_unit('K').value
                                   for d in r]
                                  for r in closest_densities])

            greater_than = np.all((temperature > ref_temps.T).T, axis=1)

            densities[greater_than, 0] = densities[greater_than, 1]
            ref_temps[greater_than, 0] = ref_temps[greater_than, 1]

            return densities[:, 0], ref_temps[:, 0]
        except TypeError:
            # single range
            densities = np.array([d.density.to_unit('kg/m^3').value
                                  for d in closest_densities])
            ref_temps = np.array([d.ref_temp.to_unit('K').value
                                  for d in closest_densities])

            if np.all(temperature > ref_temps):
                return densities[1], ref_temps[1]
            else:
                return densities[0], ref_temps[0]

    def non_redundant_dvis(self):
        if hasattr(self.record, 'kvis') and self.record.kvis is not None:
            kvis_dict = dict([(k.ref_temp.to_unit('K').value,
                               k.viscosity.to_unit('m^2/s').value)
                              for k in self.record.kvis])
        else:
            kvis_dict = {}

        if hasattr(self.record, 'dvis') and self.record.dvis is not None:
            dvis_dict = dict([(d.ref_temp.to_unit('K').value,
                               d.viscosity.to_unit('kg/(m s)').value)
                              for d in self.record.dvis])
        else:
            dvis_dict = {}

        non_redundant_keys = set(dvis_dict.keys()).difference(kvis_dict.keys())

        for k in sorted(non_redundant_keys):
            yield ObjFromDict({
                'ref_temp': TemperatureUnit(value=k, unit='K'),
                'viscosity': DynamicViscosityUnit(value=dvis_dict[k],
                                                  unit='kg/(m s)')
            })

    def dvis_to_kvis(self, kg_ms, ref_temp_k):
        density = self.density_at_temp(ref_temp_k)

        if density is None:
            return None
        else:
            return kg_ms / density

    @classmethod
    def dvis_obj_to_kvis_obj(cls, dvis_obj, density):
        viscosity = est.dvis_to_kvis(dvis_obj.kg_ms, density)

        return {'viscosity': KinematicViscosityUnit(value=viscosity,
                                                    unit='m^2/s'),
                'ref_temp': dvis_obj.ref_temp}

    def aggregate_kvis(self):
        if hasattr(self.record, 'kvis') and self.record.kvis is not None:
            kvis_list = [(k.ref_temp.to_unit('K').value,
                          k.viscosity.to_unit('m^2/s').value)
                         for k in self.record.kvis]
        else:
            kvis_list = []

        dvis_list = []
        if hasattr(self.record, 'dvis') and self.record.dvis is not None:
            for d in self.non_redundant_dvis():
                ref_temp = d.ref_temp.to_unit('K').value
                viscosity = d.viscosity.to_unit('kg/(m s)').value
                density = self.density_at_temp(temperature=ref_temp)

                if all(v is not None for v in (ref_temp, viscosity, density)):
                    dvis_list.append(
                        (ref_temp, est.dvis_to_kvis(viscosity, density))
                    )

        agg = dict(dvis_list)
        agg.update(kvis_list)

        return [ObjFromDict({'viscosity': KinematicViscosityUnit(value=k,
                                                                 unit='m^2/s'),
                             'ref_temp': TemperatureUnit(value=t, unit='K')
                             })
                for t, k in sorted(agg.items())]

    def kvis_at_temp(self, temp_k=288.15):
        shape = None

        if hasattr(temp_k, '__iter__'):
            # we like to deal with numpy arrays as opposed to simple iterables
            temp_k = np.array(temp_k)
            shape = temp_k.shape
            temp_k = temp_k.reshape(-1)

        kvis_list = self.aggregate_kvis()

        if len(kvis_list) == 0:
            return None

        closest_kvis = self.closest_to_temperature(kvis_list, temp_k)

        if closest_kvis is not None:
            try:
                # treat as a list
                ref_kvis, ref_temp_k = zip(*[(kv.viscosity.to_unit('m^2/s'),
                                              kv.ref_temp.to_unit('K'))
                                             for kv in closest_kvis])
                if len(closest_kvis) > 1:
                    ref_kvis = np.array(ref_kvis).reshape(temp_k.shape)
                    ref_temp_k = np.array(ref_temp_k).reshape(temp_k.shape)
                else:
                    ref_kvis, ref_temp_k = ref_kvis[0], ref_temp_k[0]
            except TypeError:
                # treat as a scalar
                ref_kvis = closest_kvis.viscosity.to_unit('m^2/s')
                ref_temp_k = closest_kvis.ref_temp.to_unit('K')
        else:
            return None

        if self._k_v2 is None:
            self.determine_k_v2()

        kvis_t = est.kvis_at_temp(ref_kvis.value,
                                  ref_temp_k.value,
                                  temp_k, self._k_v2)

        if shape is not None:
            return kvis_t.reshape(shape)
        else:
            return kvis_t

    def determine_k_v2(self, kvis_list=None):
        '''
            The value k_v2 is the coefficient of exponential decay used
            when calculating kinematic viscosity as a function of
            temperature.
            - If the oil contains two or more viscosity measurements, then
              we will make an attempt at determining k_v2 using a least
              squares fit.
            - Otherwise we will need to choose a reasonable average default
              value.  Bill's most recent viscosity document, and an
              analysis of the multi-KVis oils in our oil library suggest that
              a value of 2416.0 (Abu Eishah 1999) would be a good default
              value.
        '''
        self._k_v2 = 2416.0

        def exp_func(temp_k, a, k_v2):
            return a * np.exp(k_v2 / temp_k)

        if kvis_list is None:
            kvis_list = self.aggregate_kvis()

        if len(kvis_list) < 2:
            return

        ref_temp_k, ref_kvis = zip(*[(k.ref_temp.to_unit('K').value,
                                      k.viscosity.to_unit('m^2/s').value)
                                     for k in kvis_list])

        for k in np.logspace(3.6, 4.5, num=8):
            # k = log range from about 5000-32000
            a_coeff = ref_kvis[0] * np.exp(-k / ref_temp_k[0])

            try:
                popt, pcov = curve_fit(exp_func, ref_temp_k, ref_kvis,
                                       p0=(a_coeff, k), maxfev=2000)

                # - we want our covariance to be a reasonably small number,
                #   but it can get into the thousands even for a good fit.
                #   So we will only check for inf values.
                # - for sample sizes < 3, the covariance is unreliable.
                if len(ref_kvis) > 2 and np.any(pcov == np.inf):
                    print('covariance too high.')
                    continue

                if popt[1] <= 1.0:
                    continue

                self._k_v2 = popt[1]
                break
            except (ValueError, RuntimeError):
                continue

    #
    # Oil Distillation Fractional Properties
    #
    def inert_fractions(self):
        f_res = f_asph = None

        for f in self.record.sara_total_fractions:
            if f.sara_type.lower() == 'resins':
                f_res = f.fraction.value

            if f.sara_type.lower() == 'asphaltenes':
                f_asph = f.fraction.value

        if f_res is None or f_asph is None:
            density = self.density_at_temp(288.15)
            viscosity = self.kvis_at_temp(288.15)

        if f_res is None:
            f_res = est.resin_fraction(density, viscosity)

        if f_asph is None:
            f_asph = est.asphaltene_fraction(density, viscosity, f_res)

        return f_res, f_asph

    def volatile_fractions(self):
        try:
            f_sat, f_arom = self.record.saturates, self.record.aromatics
        except AttributeError:
            f_sat, f_arom = (self.record.saturates_fraction,
                             self.record.aromatics_fraction)

        estimated_sat = estimated_arom = False

        if f_sat is not None and f_arom is not None:
            return f_sat, f_arom, estimated_sat, estimated_arom
        else:
            density = self.density_at_temp(288.15)
            viscosity = self.kvis_at_temp(288.15)

        if f_sat is None:
            f_sat = est.saturates_fraction(density, viscosity)
            estimated_sat = True

        f_res, f_asph, _estimated_res, _estimated_asph = self.inert_fractions()
        if f_arom is None:
            f_arom = est.aromatics_fraction(f_res, f_asph, f_sat)
            estimated_arom = True

        return f_sat, f_arom, estimated_sat, estimated_arom

    def normalized_cut_values(self, N=10):
        f_res, f_asph = self.inert_fractions()
        cuts = list(self.record.cuts)

        if len(cuts) == 0:
            if self.record.api is not None:
                oil_api = self.record.api
            else:
                oil_rho = self.density_at_temp(288.15)
                oil_api = est.api_from_density(oil_rho)

            BP_i = est.cut_temps_from_api(oil_api)
            fevap_i = np.cumsum(est.fmasses_flat_dist(f_res, f_asph))
        else:
            BP_i, fevap_i = zip(*[(c.vapor_temp.to_unit('K').value,
                                   c.fraction.value)
                                  for c in cuts])

        popt, _pcov = curve_fit(_linear_curve, BP_i, fevap_i)
        f_cutoff = _linear_curve(732.0, *popt)  # center of asymptote (< 739)
        popt = popt.tolist() + [f_cutoff]

        fevap_i = np.linspace(0.0, 1.0 - f_res - f_asph, (N * 2) + 1)[1:]
        T_i = _inverse_linear_curve(fevap_i, *popt)

        fevap_i = fevap_i.reshape(-1, 2)[:, 1]
        T_i = T_i.reshape(-1, 2)[:, 0]

        above_zero = T_i > 0.0
        T_i = T_i[above_zero]
        fevap_i = fevap_i[above_zero]

        return T_i, fevap_i

    def get_cut_temps(self, N=10):
        cut_temps, _f_evap_i = self.normalized_cut_values(N)

        return cut_temps

    def get_cut_fmasses(self, N=10):
        _cut_temps, f_evap_i = self.normalized_cut_values(N)

        return est.fmasses_from_cuts(f_evap_i)

    def get_cut_temps_fmasses(self, N=10):
        cut_temps, f_evap_i = self.normalized_cut_values(N)

        return cut_temps, est.fmasses_from_cuts(f_evap_i)

    def component_temps(self, N=10):
        cut_temps = self.get_cut_temps(N)

        component_temps = np.append([1015.0, 1015.0],
                                    zip(cut_temps, cut_temps))

        return np.roll(component_temps, -2)

    def component_types(self, N=10):
        T_i = self.component_temps(N)

        types_out = ['Saturates', 'Aromatics'] * (len(T_i) / 2 - 1)
        types_out += ['Resins', 'Asphaltenes']

        return types_out

    def component_mol_wt(self, N=10):
        cut_temps = self.get_cut_temps(N)

        return self.estimate_component_mol_wt(cut_temps)

    @classmethod
    def estimate_component_mol_wt(cls, boiling_points):
        mw_list = np.append([est.resin_mol_wt(boiling_points),
                             est.asphaltene_mol_wt(boiling_points)],
                            zip(est.saturate_mol_wt(boiling_points),
                                est.aromatic_mol_wt(boiling_points)))

        return np.roll(mw_list, -2)

    def component_densities(self, N=10):
        cut_temps = self.get_cut_temps(N)

        return self.estimate_component_densities(cut_temps)

    @classmethod
    def estimate_component_densities(cls, boiling_points):
        rho_list = np.append([est.resin_densities(boiling_points),
                              est.asphaltene_densities(boiling_points)],
                             zip(est.saturate_densities(boiling_points),
                                 est.aromatic_densities(boiling_points)))

        return np.roll(rho_list, -2)

    def component_specific_gravity(self, N=10):
        rho_list = self.component_densities(N)

        return est.specific_gravity(rho_list)

    def component_mass_fractions(self):
        return self.component_mass_fractions_riazi()

    def component_mass_fractions_riazi(self):
        f_res, f_asph, _estimated_res, _estimated_asph = self.inert_fractions()
        cut_temps, fmass_i = self.get_cut_temps_fmasses()

        f_sat_i = fmass_i / 2.0
        f_arom_i = fmass_i / 2.0

        for _i in range(20):
            f_sat_i, f_arom_i = self.verify_cut_fractional_masses(fmass_i,
                                                                  cut_temps,
                                                                  f_sat_i,
                                                                  f_arom_i)

        mf_list = np.append([f_res, f_asph],
                            zip(f_sat_i, f_arom_i))

        return np.roll(mf_list, -2)

    @classmethod
    def verify_cut_fractional_masses(cls, fmass_i, T_i, f_sat_i, f_arom_i,
                                     prev_f_sat_i=None):
        '''
            Assuming a distillate mass with a boiling point T_i,
            We propose what the component fractional masses might be.

            We calculate what the molecular weights and specific gravities
            likely are for saturates and aromatics at that temperature.

            Then we use these values, in combination with our proposed
            component fractional masses, to produce a proposed average
            molecular weight and specific gravity for the distillate.

            We then use Riazi's formulas (3.77 and 3.78) to obtain the
            saturate and aromatic fractional masses that represent our
            averaged molecular weight and specific gravity.

            If our proposed component mass fractions were correct (or at least
            consistent with Riazi's findings), then our computed component
            mass fractions should match.

            If they don't match, then the computed component fractions should
            at least be a closer approximation to that which is consistent
            with Riazi.

            It is intended that we run this function iteratively to obtain a
            successively approximated value for f_sat_i and f_arom_i.
        '''
        assert np.allclose(fmass_i, f_sat_i + f_arom_i)

        M_w_sat_i = est.saturate_mol_wt(T_i)
        M_w_arom_i = est.aromatic_mol_wt(T_i)

        M_w_avg_i = (M_w_sat_i * f_sat_i / fmass_i +
                     M_w_arom_i * f_arom_i / fmass_i)

        # estimate specific gravity
        rho_sat_i = est.saturate_densities(T_i)
        SG_sat_i = est.specific_gravity(rho_sat_i)

        rho_arom_i = est.aromatic_densities(T_i)
        SG_arom_i = est.specific_gravity(rho_arom_i)

        SG_avg_i = (SG_sat_i * f_sat_i / fmass_i +
                    SG_arom_i * f_arom_i / fmass_i)

        f_sat_i = est.saturate_mass_fraction(fmass_i, M_w_avg_i, SG_avg_i, T_i)
        f_arom_i = fmass_i - f_sat_i

        # Note: Riazi states that eqs. 3.77 and 3.78 only work with
        #       molecular weights less than 200. In those cases,
        #       Chris would like to use the last fraction in which the
        #       molecular weight was less than 200 instead of just guessing
        #       50/50
        # TODO: In the future we might be able to figure out how
        #       to implement CPPF eqs. 3.81 and 3.82, which take
        #       care of cases where molecular weight is greater
        #       than 200.
        above_200 = M_w_avg_i > 200.0
        try:
            if np.any(above_200):
                if np.all(above_200):
                    # once in awhile we get a record where all molecular
                    # weights are over 200, In this case, we have no
                    # choice but to use the 50/50 scale
                    scale_sat_i = 0.5
                else:
                    last_good_sat_i = f_sat_i[above_200 ^ True][-1]
                    last_good_fmass_i = fmass_i[above_200 ^ True][-1]

                    scale_sat_i = last_good_sat_i / last_good_fmass_i

                f_sat_i[above_200] = fmass_i[above_200] * scale_sat_i
                f_arom_i[above_200] = fmass_i[above_200] * (1.0 - scale_sat_i)
        except TypeError:
            # numpy array assignment failed, try a scalar assignment
            if above_200:
                # for a scalar, the only way to determine the last
                # successfully computed f_sat_i is to pass it in
                if prev_f_sat_i is None:
                    scale_sat_i = 0.5
                else:
                    scale_sat_i = prev_f_sat_i / fmass_i

                f_sat_i = fmass_i * scale_sat_i
                f_arom_i = fmass_i * (1.0 - scale_sat_i)

        return f_sat_i, f_arom_i

    def oil_water_surface_tension(self):
        if all([v is not None for v in
                (self.record.oil_water_interfacial_tension_n_m,
                 self.record.oil_water_interfacial_tension_ref_temp_k)]):
            ow_st = self.record.oil_water_interfacial_tension_n_m
            ref_temp_k = self.record.oil_water_interfacial_tension_ref_temp_k

            return ow_st, ref_temp_k, False
        elif self.record.api is not None:
            ow_st = est.oil_water_surface_tension_from_api(self.record.api)

            return ow_st, 273.15 + 15, True
        else:
            est_api = est.api_from_density(self.density_at_temp(288.15))
            ow_st = est.oil_water_surface_tension_from_api(est_api)

            return ow_st, 273.15 + 15, True

    def oil_seawater_surface_tension(self):
        if all([v is not None for v in
                (self.record.oil_seawater_interfacial_tension_n_m,
                 self.record.oil_seawater_interfacial_tension_ref_temp_k)]):
            osw_st = self.record.oil_seawater_interfacial_tension_n_m
            ref_temp_k = self.record.oil_seawater_interfacial_tension_ref_temp_k

            return osw_st, ref_temp_k, False
        else:
            # we currently don't have an estimation for this one.
            return None, None, False

    def max_water_fraction_emulsion(self):
        if self.record.product_type == 'Crude':
            return 0.9
        else:
            return 0.0

    def bullwinkle_fraction(self):
        return self._adios2_bullwinkle_fraction()

    def _adios3_bullwinkle_fraction(self):
        '''
            This is the algorithm described in Bill's Oil Properties
            Estimation document.  In the document, I think it was intended
            to be the same as what Adios2 uses.  However the Adios2 c++ file
            OilInitialize.cpp contains steps that are missing here and in the
            document.
        '''
        _f_res, f_asph = self.inert_fractions()

        if f_asph > 0.0:
            return est.bullwinkle_fraction_from_asph(f_asph)
        else:
            return est.bullwinkle_fraction_from_api(self.get_api())

    def _adios2_bullwinkle_fraction(self):
        '''
            This is the mass fraction that must evaporate or dissolve before
            stable emulsification can begin.
            - For this estimation, we depend on an oil object with a valid
              asphaltene fraction or a valid api
            - This is a scalar value calculated with a reference temperature
              of 15C
            - For right now we are referencing the Adios2 code file
              OilInitialize.cpp, function CAdiosData::Bullwinkle(void)
        '''
        estimated = False

        if self.record.product_type == "Refined":
            bullwinkle_fraction = 1.0
            estimated = True
        elif self.record.emuls_constant_max is not None:
            bullwinkle_fraction = self.record.emuls_constant_max
        else:
            # product type is crude
            Ni = (self.record.nickel
                  if self.record.nickel is not None
                  else 0.0)
            Va = (self.record.vanadium
                  if self.record.vanadium is not None
                  else 0.0)

            _f_res, f_asph = self.inert_fractions()
            oil_api = self.get_api()

            if (Ni > 0.0 and Va > 0.0 and Ni + Va > 15.0):
                bullwinkle_fraction = 0.0
            elif f_asph > 0.0:
                # Bullvalue = 0.32 - 3.59 * f_Asph
                bullwinkle_fraction = 0.20219 - 0.168 * np.log10(f_asph)
                bullwinkle_fraction = np.clip(bullwinkle_fraction, 0.0, 0.303)
            elif oil_api < 26.0:
                bullwinkle_fraction = 0.08
            elif oil_api > 50.0:
                bullwinkle_fraction = 0.303
            else:
                bullwinkle_fraction = (-1.038 -
                                       0.78935 * np.log10(1.0 / oil_api))

            bullwinkle_fraction = self._adios2_new_bull_calc(bullwinkle_fraction)
            estimated = True

        return bullwinkle_fraction, estimated

    def _adios2_new_bull_calc(self, bullwinkle_fraction):
        '''
            From the Adios2 c++ file OilInitialize.cpp, there is functionality
            inside the function CAdiosData::Bullwinkle() which is annotated
            in the code as 'new bull calc'.

            It uses the following definitions:
            - TG, Documented as the value 'dT/df - evaporation'.
                  I can only assume this is the initial fractional rate of
                  evaporation.
            - TBP, Documented as the 'ADIOS 1 liquid boiling point
                   (bubble pt)'.
            - BullAdios1, which appears to be used to scale-average the
                          initially computed bullwinkle fraction.

            Regardless, in order to approximate what Adios2 is doing, we
            need this modification of our bullwinkle fraction.
        '''
        oil_api = self.get_api()

        t_g = 1356.7 - 247.36 * np.log(oil_api)
        t_bp = 532.98 - 3.1295 * oil_api
        bull_adios1 = (483.0 - t_bp) / t_g

        bull_adios1 = np.clip(bull_adios1, 0.0, 0.4)

        return 0.5 * (bullwinkle_fraction + bull_adios1)

    def solubility(self):
        '''
            Note: imported records do not have a solubility attribute.
                  We just return a default.
        '''
        return 0.0

    def adhesion(self):
        estimated = False

        if self.record.adhesion is not None:
            omega_a = self.record.adhesion
        else:
            omega_a = 0.035
            estimated = True

        return omega_a, estimated

    def sulphur_fraction(self):
        if self.record.sulphur is not None:
            return self.record.sulphur
        else:
            return 0.0
