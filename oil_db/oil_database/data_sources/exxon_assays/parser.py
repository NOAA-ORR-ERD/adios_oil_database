#!/usr/bin/env python
"""
For the Exxon Assays, a Parser isn't really required

so this is just a pass-through function -- no need even for a class
"""


def ExxonRecordParser(record):
    return record






## OLd code -- I think actually a copy of the ESTS parser
# import re
# from datetime import datetime
# import logging

# from slugify import Slugify

# from pprint import PrettyPrinter
# pp = PrettyPrinter(indent=2, width=120)

# custom_slugify = Slugify(to_lower=True, separator='_')

# logger = logging.getLogger(__name__)


# class ExxonRecordParser(object):
#     ''' A specialized record class for the Environment Canada oil spreadsheet.
#         - We manage a list of properties extracted from the Excel columns
#           for an oil.  Basically this will be a list of property groups,
#           where each property group will contain a set of property values at
#           differing degrees of weathering.
#         - The raw data from the Excel file will be a two-dimensional array
#           of data, so each property group will have the same number of items.
#           If an oil contains no oil property value at a certain degree of
#           weathering, instead of being removed from the group, it will contain
#           a value of None.
#         - We also manage an index lookup table for finding a set of property
#           values by their property name.
#         - It is possible that within a property group, there are multiple
#           properties of the same name.  This could happen if multiple sets of
#           properties are represented, possibly due to multiple testing methods.
#           For this reason, the index values contained in the lookup will be
#           a list with 1 or more indexes.
#     '''
#     datetime_pattern = re.compile(
#         r'(?P<month>\d{1,2})[-/](?P<day>\d{1,2})[-/](?P<year>\d{2,4})'
#         r'(?:[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'  # Optional HH:mm
#         r'(?::(?P<second>\d{1,2})'  # Optional seconds
#         r'(?:\.(?P<microsecond>\d{1,6})0*)?)?)?'  # Optional microseconds
#         r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?\Z'  # Optional timezone
#     )

#     def __init__(self, property_indexes, values):
#         '''
#             :param property_indexes: A lookup dictionary of property index
#                                      values.
#             :type property_indexes: A dictionary with property names as keys,
#                                     and associated index values into the data.
#         '''
#         self.prop_idx = property_indexes
#         self.values = values

#     def get_props_by_category(self, category):
#         '''
#             Get all oil data properties for each column of oil data, that exist
#             within a single category.
#             - This function is intended to work on the oil data columns for a
#               single oil, but this is not enforced.
#             - the oil properties will be returned as a dictionary.
#         '''
#         ret = {}
#         cat_fields = self.prop_idx[category]

#         for f, idxs in cat_fields.items():
#             ret[f] = [self.values[i] for i in idxs]

#         return ret

#     def get_props_by_name(self, category, name):
#         '''
#             Get the oil data properties for each column of oil data,
#             referenced by their category name and oil property name.
#             - This function is intended to work on the oil data columns for a
#               single oil, but this is not enforced.
#         '''
#         return [self.values[i] for i in self.prop_idx[category][name]]

#     @property
#     def name(self):
#         '''
#             For now we will just concatenate all the names we see in the
#             list.  In the future, we will want to be a bit smarter.
#         '''
#         return ' '.join([n.strip()
#                          for n in self.get_props_by_name(None, 'oil')[0]
#                          if n is not None])

#     @property
#     def ests_codes(self):
#         return self.get_props_by_name(None,
#                                       'ests_emergencies_sciences_'
#                                       'and_technologies_code')[0]

#     @property
#     def ec_oil_id(self):
#         '''
#             We will use the ESTS codes in the record as the identifier.

#             ESTS codes are a series of numbers separated by a period '.'.
#             The first number in the series seems to identify the species of
#             the petroleum substance, and the rest identify a degree of
#             weathering.  So we will use just the first one.
#         '''
#         primary_codes = set([int(str(c).split('.')[0])
#                              for c in self.ests_codes])
#         assert len(primary_codes) == 1

#         return 'EC{:06.0f}'.format(primary_codes.pop())

#     @property
#     def weathering(self):
#         return self.get_props_by_name(None, 'weathered')[0]

#     @property
#     def reference(self):
#         '''
#             We will concatenate all the reference content we see in the
#             list, separated with a space.
#         '''
#         return ' '.join([n for n
#                          in self.get_props_by_name(None, 'reference')[0]
#                          if n is not None])

#     @property
#     def reference_date(self):
#         '''
#             We will concatenate all the reference content we see in the
#             list, separated with a space.

#             Note: Apparently there are a few records that just don't have
#                   a sample date.  So we can't really enforce the presence
#                   of a date here.

#             Note: The date formats are all over the place here.  So the default
#                   datetime parsing inside PyMODM is not sufficient.
#                   Some formats that I have seen:
#                   - MM/DD/YYYY          # most common
#                   - MM-DD-YYYY          # different separator
#                   - DD/MM/YYYY          # 7 records very clearly in this format
#                   - MM/YYYY             # 3 records do this
#                   - YYYY                # 2 records do this
#                   - <month name>, YYYY  # 3 records do this
#                   So we will:
#                   - Treat MM/DD/YYYY as the default
#                   - Allow for DD/MM/YYYY if it can be clearly determined
#                   - Fix the others in the file.
#         '''
#         dates = set([n for n in
#                      self.get_props_by_name(None, 'date_sample_received')[0]
#                      if n is not None])

#         if len(dates) > 0:
#             return self._parse_time(dates.pop())
#         else:
#             return None

#     def _parse_time(self, date_str):
#         if isinstance(date_str, datetime):
#             return date_str
#         elif isinstance(date_str, (str, unicode)):
#             match = re.match(self.datetime_pattern, date_str.strip())

#             if match is not None:
#                 tp = {k: int(v) for k, v in match.groupdict().items()
#                       if v is not None}

#                 if tp['month'] > 12:
#                     tp['month'], tp['day'] = tp['day'], tp['month']

#                 return datetime(**tp)
#             else:
#                 raise ValueError('reference_date "{}" is not parsable'
#                                  .format(date_str))

#     @property
#     def comments(self):
#         '''
#             We will concatenate all the comments we see in the list,
#             separated with a space.
#         '''
#         return ' '.join([n for n in self.get_props_by_name(None, 'comments')[0]
#                          if n is not None])

#     @property
#     def location(self):
#         '''
#             We will concatenate all the location info we see in the list,
#             separated with a space.
#         '''
#         return ' '.join([n for n
#                          in self.get_props_by_name(None, 'source')[0]
#                          if n is not None])

#     @property
#     def api(self):
#         return [n for n
#                 in self.get_props_by_name('api_gravity',
#                                           'calculated_api_gravity')[0]
#                 if n is not None]

#     @property
#     def densities(self):
#         '''
#             Getting densities out of this datasheet is more tricky than it
#             should be.  There are two categories, density at 15C, and density
#             at 0/5C.  I dunno, I would have organized the data in a more
#             orthogonal way.
#         '''
#         densities = self._get_densities_at_0c()
#         densities.extend(self._get_densities_at_5c())
#         densities.extend(self._get_densities_at_15c())

#         return densities

#     def _get_densities_at_15c(self):
#         densities = []
#         props = self.get_props_by_category('density_at_15_c_g_ml_astm_d5002')

#         for i, w in enumerate(self.weathering):
#             # we want to create a density object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'ref_temp_k': 273.15 + 15.0}
#             rename_props = {'density_15_c_g_ml': 'kg_m_3'}
#             to_kg_m_3 = {'kg_m_3'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         to_kg_m_3=to_kg_m_3)

#             densities.append(kwargs)

#         return [d for d in densities if d['kg_m_3'] not in (None, 0.0)]

#     def _get_densities_at_5c(self):
#         densities = []
#         props = self.get_props_by_category('density_at_0_5_c_g_ml_astm_d5002')

#         for i, w in enumerate(self.weathering):
#             # we want to create a density object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'ref_temp_k': 273.15 + 5.0}
#             prune_props = {'density_0_c_g_ml'}
#             rename_props = {'density_5_c_g_ml': 'kg_m_3'}
#             to_kg_m_3 = {'kg_m_3'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         to_kg_m_3=to_kg_m_3)

#             densities.append(kwargs)

#         return [d for d in densities if d['kg_m_3'] not in (None, 0.0)]

#     def _get_densities_at_0c(self):
#         densities = []
#         props = self.get_props_by_category('density_at_0_5_c_g_ml_astm_d5002')

#         for i, w in enumerate(self.weathering):
#             # we want to create a density object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'ref_temp_k': 273.15}
#             prune_props = {'density_5_c_g_ml'}
#             rename_props = {'density_0_c_g_ml': 'kg_m_3'}
#             op_and_value = {'kg_m_3'}
#             to_kg_m_3 = {'kg_m_3'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         op_and_value=op_and_value,
#                                         to_kg_m_3=to_kg_m_3)

#             densities.append(kwargs)

#         return [d for d in densities if d['kg_m_3'] not in (None, 0.0)]

#     @property
#     def viscosities(self):
#         '''
#             Getting viscosities out of this datasheet is more tricky than it
#             should be.  There are two categories, viscosity at 15C, and
#             viscosity at 0/5C.  I dunno, I would have organized the data in a
#             more orthogonal way.  Otherwise, the data is mostly what we expect,
#             with only a few deviations.

#             Note: Environment Canada measures dynamic viscosity in (mPa * s),
#                   so we need to convert to (kg / (m * s))
#             Note: Sometimes there is a greater than ('>') indication for a
#                   viscosity value.  I don't really know what else to do in
#                   this case but parse the float value and ignore the operator.
#         '''
#         viscosities = self._get_viscosities_at_0c()
#         viscosities.extend(self._get_viscosities_at_5c())
#         viscosities.extend(self._get_viscosities_at_15c())

#         self._propagate_merged_excel_cells(viscosities, ('method',))

#         return viscosities

#     def _get_viscosities_at_15c(self):
#         viscosities = []
#         props = self.get_props_by_category('viscosity_at_15_c_mpa_s')

#         for i, w in enumerate(self.weathering):
#             # we want to create a viscosity object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'ref_temp_k': 273.15 + 15.0}
#             rename_props = {'viscosity_at_15_c_mpa_s': 'kg_ms'}
#             op_and_value = {'kg_ms'}
#             to_kg_ms = {'kg_ms'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         op_and_value=op_and_value,
#                                         to_kg_ms=to_kg_ms)

#             viscosities.append(kwargs)

#         return [v for v in viscosities if v['kg_ms'] not in (None, 0.0)]

#     def _get_viscosities_at_5c(self):
#         viscosities = []
#         props = self.get_props_by_category('viscosity_at_0_5_c_mpa_s')

#         for i, w in enumerate(self.weathering):
#             # we want to create a viscosity object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'ref_temp_k': 273.15 + 5.0}
#             prune_props = {'viscosity_at_0_c_mpa_s'}
#             rename_props = {'viscosity_at_5_c_mpa_s': 'kg_ms'}
#             op_and_value = {'kg_ms'}
#             to_kg_ms = {'kg_ms'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         op_and_value=op_and_value,
#                                         to_kg_ms=to_kg_ms)

#             viscosities.append(kwargs)

#         return [v for v in viscosities if v['kg_ms'] not in (None, 0.0)]

#     def _get_viscosities_at_0c(self):
#         viscosities = []
#         props = self.get_props_by_category('viscosity_at_0_5_c_mpa_s')

#         for i, w in enumerate(self.weathering):
#             # we want to create a viscosity object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'ref_temp_k': 273.15}
#             prune_props = {'viscosity_at_5_c_mpa_s'}
#             rename_props = {'viscosity_at_0_c_mpa_s': 'kg_ms'}
#             op_and_value = {'kg_ms'}
#             to_kg_ms = {'kg_ms'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         op_and_value=op_and_value,
#                                         to_kg_ms=to_kg_ms)

#             viscosities.append(kwargs)

#         return [v for v in viscosities if v['kg_ms'] not in (None, 0.0)]

#     @property
#     def interfacial_tensions(self):
#         '''
#             Getting interfacial tensions out of this datasheet is a bit tricky,
#             but understandably so since we are dealing with a number of
#             dimensional parameters (temperature, interface, weathering).
#             There are two categories, surface/interfacial tension at 15C, and
#             surface/interfacial tension at 0/5C.
#             I still think it could have been organized more orthogonally.
#         '''
#         tensions = self._get_tensions_at_0c()
#         tensions.extend(self._get_tensions_at_5c())
#         tensions.extend(self._get_tensions_at_15c())

#         return tensions

#     def _get_tensions_at_15c(self):
#         tensions = []
#         props = self.get_props_by_category('surface_interfacial_tension_'
#                                            'at_15_c_mn_m_or_dynes_cm')

#         for i, w in enumerate(self.weathering):
#             # we want to create a viscosity object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             ref_temp_k = 273.15 + 15.0
#             labels = ('surface_tension_15_c_oil_air',
#                       'interfacial_tension_15_c_oil_water',
#                       'interfacial_tension_15_c_oil_salt_water_3_3_nacl')
#             if_types = ('air', 'water', 'seawater')

#             for label, if_type in zip(labels, if_types):
#                 add_props = {'weathering': w,
#                              'ref_temp_k': ref_temp_k,
#                              'interface': if_type}
#                 prune_props = {i for i in labels if i != label}
#                 rename_props = {label: 'n_m'}
#                 to_n_m = {'n_m'}

#                 kwargs = self._build_kwargs(props_i,
#                                             add_props=add_props,
#                                             prune_props=prune_props,
#                                             rename_props=rename_props,
#                                             to_n_m=to_n_m)

#                 tensions.append(kwargs)

#             self._propagate_merged_excel_cells(tensions, ('method',))

#         return [t for t in tensions if t['n_m'] not in (None, 0.0)]

#     def _get_tensions_at_5c(self):
#         tensions = []
#         props = self.get_props_by_category('surface_interfacial_tension_'
#                                            'at_0_5_c_mn_m_or_dynes_cm')

#         for i, w in enumerate(self.weathering):
#             # we want to create a viscosity object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             ref_temp_k = 273.15 + 5.0
#             labels = ('surface_tension_5_c_oil_air',
#                       'interfacial_tension_5_c_oil_water',
#                       'interfacial_tension_5_c_oil_salt_water_3_3_nacl')
#             xtra_labels = ('surface_tension_0_c_oil_air',
#                            'interfacial_tension_0_c_oil_water',
#                            'interfacial_tension_0_c_oil_salt_water_3_3_nacl')
#             if_types = ('air', 'water', 'seawater')

#             for label, if_type in zip(labels, if_types):
#                 add_props = {'weathering': w,
#                              'ref_temp_k': ref_temp_k,
#                              'interface': if_type}
#                 prune_props = {i for i in labels + xtra_labels
#                                if i != label}
#                 rename_props = {label: 'n_m'}
#                 to_n_m = {'n_m'}

#                 kwargs = self._build_kwargs(props_i,
#                                             add_props=add_props,
#                                             prune_props=prune_props,
#                                             rename_props=rename_props,
#                                             to_n_m=to_n_m)

#                 tensions.append(kwargs)

#             self._propagate_merged_excel_cells(tensions, ('method',))

#         return [t for t in tensions if t['n_m'] not in (None, 0.0)]

#     def _get_tensions_at_0c(self):
#         tensions = []
#         props = self.get_props_by_category('surface_interfacial_tension_'
#                                            'at_0_5_c_mn_m_or_dynes_cm')

#         for i, w in enumerate(self.weathering):
#             # we want to create a viscosity object for each weathering value
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             ref_temp_k = 273.15
#             labels = ('surface_tension_0_c_oil_air',
#                       'interfacial_tension_0_c_oil_water',
#                       'interfacial_tension_0_c_oil_salt_water_3_3_nacl')
#             xtra_labels = ('surface_tension_5_c_oil_air',
#                            'interfacial_tension_5_c_oil_water',
#                            'interfacial_tension_5_c_oil_salt_water_3_3_nacl')
#             if_types = ('air', 'water', 'seawater')

#             for label, if_type in zip(labels, if_types):
#                 add_props = {'weathering': w,
#                              'ref_temp_k': ref_temp_k,
#                              'interface': if_type}
#                 prune_props = {i for i in labels + xtra_labels
#                                if i != label}
#                 rename_props = {label: 'n_m'}
#                 to_n_m = {'n_m'}

#                 kwargs = self._build_kwargs(props_i,
#                                             add_props=add_props,
#                                             prune_props=prune_props,
#                                             rename_props=rename_props,
#                                             to_n_m=to_n_m)

#                 tensions.append(kwargs)

#             self._propagate_merged_excel_cells(tensions, ('method',))

#         return [t for t in tensions if t['n_m'] not in (None, 0.0)]

#     @property
#     def flash_points(self):
#         flash_points = []
#         props = self.get_props_by_category('flash_point_c')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             flash_point_obj = self.build_flash_point_kwargs(props_i, w)
#             flash_points.append(flash_point_obj)

#         self._propagate_merged_excel_cells(flash_points, ('method',))

#         return [f for f in flash_points
#                 if f['min_temp_k'] is not None or f['max_temp_k'] is not None]

#     @property
#     def pour_points(self):
#         '''
#             Getting the pour point is similar to Adios2 in that the values
#             contain '>' and '<' symbols.  This indicates we need to interpret
#             the content to come up with minimum and maximum values.
#             Dimensional parameters are simply (weathering).
#         '''
#         pour_points = []
#         props = self.get_props_by_category('pour_point_c')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             pour_point_obj = self._build_pour_point_kwargs(props_i, w)
#             pour_points.append(pour_point_obj)

#         self._propagate_merged_excel_cells(pour_points, ('method',))

#         return [p for p in pour_points
#                 if p['min_temp_k'] is not None or p['max_temp_k'] is not None]

#     @property
#     def distillation_cuts(self):
#         '''
#             There are two distinct sets of distillation cut data in the EC
#             spreadsheet. They are:
#             - Boiling Point: Distribution, Temperature (C).
#               Here the labels are percent values representing the fraction
#               boiled off, and the data is the temperature at which the
#               fractional value occurs.
#             - Boiling Point: Cumulative Weight Fraction (%).
#               Here the labels are temperature (C) values, and the data is the
#               fraction that is boiled off at that temperature.

#             We will try to get both sets of data and then merge them if
#             possible.  Most oils will have either one set or the other,
#             not both.  Dimensional parameters are simply (weathering).
#         '''
#         cuts = self._get_cuts_from_bp_distribution()
#         cuts.extend(self._get_cuts_from_bp_cumulative_frac())

#         return cuts

#     def _get_cuts_from_bp_distribution(self):
#         cuts = []
#         props = self.get_props_by_category('boiling_point_'
#                                            'distribution_temperature_c')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])
#             cuts_i = self._build_cuts_from_dist_data(props_i, w)

#             cuts.extend(cuts_i)

#         return [c for c in cuts if c['vapor_temp_k'] is not None]

#     def _build_cuts_from_dist_data(self, props, weathering):
#         '''
#             Build a list of EC distillation cut objects from boiling point
#             distribution data.
#             - prop_names: The list of property names
#             - values: A list of Excel cell objects representing the properties.
#             - weathering: The fractional oil weathering amount.

#             Note: The labels have a bit of a problem.  Most of them are percent
#                   value labels, which is fine, but additionally, we have
#                   'initial_boiling_point', and 'fbp'.  These are unusable
#                   because there is no indication of what fraction the initial
#                   and final boiling point has.  I could assume the initial
#                   boiling point has a fraction of 0%, but it is clear that the
#                   final boiling point is a temperature somewhere between the
#                   95% and 100% temperatures. So it is a fraction somewhere
#                   between 95% and 100%, which we don't precisely know.
#         '''
#         cuts = []
#         dist_data = props

#         # The only labels we care about are the percent value labels
#         for frac in ([(p / 100.0) for p in range(5, 100, 5)] + [1]):
#             label = custom_slugify('{:0}'.format(frac))
#             vapor_temp_c = dist_data[label]
#             cuts.append(self._build_cut_kwargs(vapor_temp_c, frac, weathering))

#         return cuts

#     def _get_cuts_from_bp_cumulative_frac(self):
#         cuts = []

#         props = self.get_props_by_category('boiling_point_'
#                                            'cumulative_weight_fraction')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])
#             cuts_i = self._build_cuts_from_cumulative_fraction(props_i, w)

#             cuts.extend(cuts_i)

#         return [c for c in cuts if c['fraction'] is not None]

#     def _build_cuts_from_cumulative_fraction(self, props, weathering):
#         '''
#             Build a list of EC distillation cut objects from cumulative weight
#             fraction data.
#             - prop_names: The list of property names
#             - values: A list of Excel cell objects representing the properties.
#             - weathering: The fractional oil weathering amount.

#             Note: The labels have a bit of a problem.  Most of them are percent
#                   value labels, which is fine, but additionally, we have
#                   'initial_boiling_point', and 'fbp'.  These are unusable
#                   because there is no indication of what fraction the initial
#                   and final boiling point has.  I could assume the initial
#                   boiling point has a fraction of 0%, but it is clear that
#                   the final boiling point is a temperature somewhere between
#                   the 95% and 100% temperatures. So it is a fraction somewhere
#                   between 95% and 100%, which we don't precisely know.
#         '''
#         cuts = []
#         frac_data = props

#         # The only labels we care about are the temperature labels
#         temp_values = [item
#                        for sublist in [range(40, 200, 20), range(200, 701, 50)]
#                        for item in sublist]

#         for temp_c in temp_values:
#             label = '{}'.format(temp_c)
#             frac = frac_data[label]
#             cuts.append(self._build_cut_kwargs(temp_c, frac, weathering))

#         return cuts

#     def _build_cut_kwargs(self, vapor_temp_c, fraction, weathering):
#         return {'vapor_temp_k': self._celcius_to_kelvin(vapor_temp_c),
#                 'fraction': fraction,
#                 'weathering': weathering}

#     @property
#     def adhesions(self):
#         '''
#             Getting the adhesion is fairly straightforward.  We simply get the
#             value in g/cm^2 and convert to kg/m^2.
#             Dimensional parameters are simply (weathering).
#         '''
#         adhesions = []
#         props = self.get_props_by_category('adhesion_g_cm2_ests_1996')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w}
#             rename_props = {'adhesion': 'kg_m_2'}
#             to_kg_m_2 = {'kg_m_2'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         to_kg_m_2=to_kg_m_2)

#             adhesions.append(kwargs)

#         return [a for a in adhesions if a['kg_m_2'] is not None]

#     @property
#     def evaporation_eqs(self):
#         '''
#             The Evironment Canada data sheet contains equations for evaporative
#             loss, along with coefficient values to be used per oil. There are
#             three equations and three possible coefficients (A, B, and
#             optionally C). We will try to capture both the algorithm and
#             the coefficients.  Dimensional parameters are simply (weathering).
#         '''
#         evaporation = self._get_evaporation_eqs_ests_1998()
#         evaporation.extend(self._get_evaporation_eqs_mass_loss1())
#         evaporation.extend(self._get_evaporation_eqs_mass_loss2())

#         return evaporation

#     def _get_evaporation_eqs_ests_1998(self):
#         evaporation_eqs = []

#         props = self.get_props_by_category('evaporation_ests_1998_1')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             evap_kwargs = self._build_evaporation_kwargs(props_i, w,
#                                                          '(A + BT) ln t',
#                                                          'for_ev_a_bt_ln_t')
#             evaporation_eqs.append(evap_kwargs)

#         return [eq for eq in evaporation_eqs
#                 if eq['a'] is not None and eq['b'] is not None]

#     def _get_evaporation_eqs_mass_loss1(self):
#         evaporation_eqs = []

#         props = self.get_props_by_category('parameters_for_'
#                                            'evaporation_equation_mass_loss')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             evap_kwargs = self._build_evaporation_kwargs(props_i, w,
#                                                          '(A + BT) sqrt(t)',
#                                                          'for_ev_a_bt_sqrt_t')
#             evaporation_eqs.append(evap_kwargs)

#         return [eq for eq in evaporation_eqs
#                 if eq['a'] is not None and eq['b'] is not None]

#     def _get_evaporation_eqs_mass_loss2(self):
#         evaporation_eqs = []

#         props = self.get_props_by_category('parameters_for_'
#                                            'evaporation_equation_mass_loss')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             evap_kwargs = self._build_evaporation_kwargs(props_i, w,
#                                                          'A + B ln (t + C)',
#                                                          'for_ev_a_b_ln_t_c')
#             evaporation_eqs.append(evap_kwargs)

#         return [eq for eq in evaporation_eqs
#                 if eq['a'] is not None and eq['b'] is not None]

#     @property
#     def emulsions(self):
#         '''
#             The Evironment Canada data sheet contains data for emulsion
#             properties, which we will try to capture.
#             Dimensional parameters are (temperature, age, weathering).
#         '''
#         emulsions = self._get_emulsion_age_0()
#         emulsions.extend(self._get_emulsion_age_7())

#         return emulsions

#     def _get_emulsion_age_0(self):
#         emulsions = []
#         props = self.get_props_by_category('emulsion_at_15_degc_'
#                                            'on_the_day_of_formation_'
#                                            'ests_1998_2')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w,
#                          'ref_temp_k': 273.15 + 15.0,
#                          'age_days': 0.0}
#             rename_props = {'water_content_w_w': 'water_content_fraction'}
#             to_fraction = {'water_content_fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             emulsions.append(kwargs)

#         return [e for e in emulsions
#                 if e['water_content_fraction'] is not None]

#     def _get_emulsion_age_7(self):
#         emulsions = []
#         props = self.get_props_by_category('emulsion_at_15_degc_'
#                                            'one_week_after_formation_'
#                                            'ests_1998b')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w,
#                          'ref_temp_k': 273.15 + 15.0,
#                          'age_days': 7.0}
#             rename_props = {'water_content_w_w': 'water_content_fraction'}
#             to_fraction = {'water_content_fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             emulsions.append(kwargs)

#         return [e for e in emulsions
#                 if e['water_content_fraction'] is not None]

#     @property
#     def sulfur_content(self):
#         '''
#             Getting the sulfur content is very straightforward.  Just get the
#             float value.
#             Dimensional parameters are (weathering).
#         '''
#         return self._get_sulfur_content_by_weathering()

#     @property
#     def water_content(self):
#         '''
#             Dimensional parameters are (weathering).
#         '''
#         return self._get_water_content_by_weathering()

#     @property
#     def wax_content(self):
#         '''
#             Dimensional parameters are (weathering).
#         '''
#         return self._get_wax_content_by_weathering()

#     @property
#     def sara_total_fractions(self):
#         '''
#             Dimensional parameters are (weathering).

#             Note: This is probably not a requirement, but It is nice to order
#                   These things in an expected way.  So we will order these
#                   fractions by weathering amount from lowest to highest.
#                   And we will order fraction groups of the same weathering
#                   amount by SARA, as the acronym implies.
#                   This will be a flat list, however.
#         '''
#         saturates = self._get_saturates_fraction_by_weathering()
#         aromatics = self._get_aromatics_fraction_by_weathering()
#         resins = self._get_resins_fraction_by_weathering()
#         asphaltenes = self._get_asphaltenes_fraction_by_weathering()

#         return [f for g in zip(saturates, aromatics, resins, asphaltenes)
#                 for f in g]

#     def _get_sulfur_content_by_weathering(self):
#         sulfur_contents = []
#         props = self.get_props_by_category('sulfur_content_astm_d4294')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w}
#             rename_props = {'sulfur_content': 'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             sulfur_contents.append(kwargs)

#         return [f for f in sulfur_contents if f['fraction'] is not None]

#     def _get_water_content_by_weathering(self):
#         water_contents = []

#         props = self.get_props_by_category('water_content_astm_e203')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w}
#             rename_props = {'water_content': 'fraction'}
#             op_and_value = {'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         op_and_value=op_and_value,
#                                         to_fraction=to_fraction)

#             water_contents.append(kwargs)

#         return [f for f in water_contents if f['fraction'] is not None]

#     def _get_wax_content_by_weathering(self):
#         wax_contents = []

#         props = self.get_props_by_category('wax_content_ests_1994')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w}
#             rename_props = {'waxes': 'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             wax_contents.append(kwargs)

#         return [f for f in wax_contents if f['fraction'] is not None]

#     def _get_saturates_fraction_by_weathering(self):
#         saturates_fractions = []

#         props = self.get_props_by_category('hydrocarbon_group_content')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'sara_type': 'Saturates'}
#             prune_props = {'aromatics', 'resin', 'asphaltene'}
#             rename_props = {'saturates': 'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             saturates_fractions.append(kwargs)

#         return [f for f in saturates_fractions
#                 if f['fraction'] is not None]

#     def _get_aromatics_fraction_by_weathering(self):
#         aromatics_fractions = []

#         props = self.get_props_by_category('hydrocarbon_group_content')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'sara_type': 'Aromatics'}
#             prune_props = {'saturates', 'resin', 'asphaltene'}
#             rename_props = {'aromatics': 'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             aromatics_fractions.append(kwargs)

#         return [f for f in aromatics_fractions
#                 if f['fraction'] is not None]

#     def _get_resins_fraction_by_weathering(self):
#         resins_fractions = []

#         props = self.get_props_by_category('hydrocarbon_group_content')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'sara_type': 'Resins'}
#             prune_props = {'saturates', 'aromatics', 'asphaltene'}
#             rename_props = {'resin': 'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             resins_fractions.append(kwargs)

#         return [f for f in resins_fractions
#                 if f['fraction'] is not None]

#     def _get_asphaltenes_fraction_by_weathering(self):
#         asphaltenes_fractions = []

#         props = self.get_props_by_category('hydrocarbon_group_content')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in props.items()])

#             add_props = {'weathering': w, 'sara_type': 'Asphaltenes'}
#             prune_props = {'saturates', 'aromatics', 'resin'}
#             rename_props = {'asphaltene': 'fraction'}
#             to_fraction = {'fraction'}

#             kwargs = self._build_kwargs(props_i,
#                                         add_props=add_props,
#                                         prune_props=prune_props,
#                                         rename_props=rename_props,
#                                         to_fraction=to_fraction)

#             asphaltenes_fractions.append(kwargs)

#         return [f for f in asphaltenes_fractions
#                 if f['fraction'] is not None]

#     @property
#     def benzene_content(self):
#         '''
#             The Evironment Canada data sheet contains data for Benzene content,
#             which we will try to capture.
#             We have 3 property groups in this case, and I think it would be ok
#             to merge them into a single object.
#             - Dimensional parameters are (weathering).
#             - Units are all ug/g as far as I can tell, which is basically the
#               same as ppm, so no conversion.
#             - We will rename the benzene amount properties all with a '_ppm'
#               suffix to indicate the units.

#             Note: One record in the datasheet had a benzene section where most
#                   of the values were 'ND'.  Not sure what this means, but for
#                   our purposes, it will be changed to a None.
#         '''
#         benzenes = []

#         benz_props = self.get_props_by_category('benzene_and_'
#                                                 'alkynated_benzene_'
#                                                 'ests_2002b')
#         btex_props = self.get_props_by_category('btex_group_ug_g_ests_2002b')
#         c4_props = self.get_props_by_category('c4_c6_alkyl_benzenes_ug_g_'
#                                               'ests_2002b')

#         for i, w in enumerate(self.weathering):
#             props_i = dict([(k, v[0][i]) for k, v in benz_props.items()])
#             kwargs = props_i

#             props_i = dict([(k, v[0][i]) for k, v in btex_props.items()])
#             kwargs.update(props_i)

#             props_i = dict([(k, v[0][i]) for k, v in c4_props.items()])
#             kwargs.update(props_i)

#             [self._rename_prop(kwargs, lbl, lbl + '_ppm')
#              for lbl in kwargs.keys()]

#             # fix the 'ND' values
#             for k, v in kwargs.items():
#                 if v == 'ND':
#                     kwargs[k] = None

#             kwargs['weathering'] = w
#             kwargs['method'] = 'ESTS 2002b'

#             benzenes.append(kwargs)

#         return benzenes

#     def _build_kwargs(self, props,
#                       add_props=None,
#                       prune_props=None,
#                       rename_props=None,
#                       op_and_value=None,
#                       to_fraction=None,
#                       to_kg_ms=None,
#                       to_n_m=None,
#                       to_kg_m_2=None,
#                       to_kg_m_3=None):
#         '''
#             Build a content properties dictionary suitable to be passed in
#             as keyword args.
#             - props: Our properties from the Excel file.
#             - add_props: A set of properties to be added.
#             - prune_props: A set of properties to be pruned.
#             - rename_props: dict containing properties to be renamed,
#             - op_and_value: A set of numeric properties that could contain an
#                             operator prefix.
#             - to_fraction: A set of properties to convert from percent to
#                            fraction.
#             - to_kg_ms: A set of properties to convert from (mPa * s) to
#                         (kg / (m * s)).
#             - to_n_m: A set of properties to convert from mN/m (dynes/cm) into
#                       N/m.
#             - to kg_m_2: A set of properties to convert from g/cm^2 to kg/m^2
#             - to kg_m_3: A set of properties to convert from g/cm^3 (g/ml)
#                          to kg/m^3

#             Note: We perform actions in a particular order.
#                   1: Add any add_props that were passed in.
#                   2: Prune any prune_props that were passed in.
#                   3: Rename any rename_props that were passed in.
#                   4: Convert any op_and_value props that may have an operator
#                      prefix.  Right now we will just throw away the operator,
#                      but in the future we could decide to keep it in its own
#                      property.  Depends upon how useful it turns out to be.
#                   5: Convert any to_fraction props that were passed in.
#                   6: Convert any to_kg_ms props that were passed in.
#                   7: Convert any to_n_m props that were passed in.
#                   8: Convert any to_kg_m_2 props that were passed in.
#                   9: Convert any to_kg_m_3 props that were passed in.

#             TODO: It is intended that any unit conversions will be handled in
#                   an exclusive way.  It is unlikely that we will be performing
#                   multiple types of conversions on a single set of kwargs, and
#                   it would in fact be wrong to perform multiple conversions
#                   on a single attribute.  We should add logic to enforce some
#                   exclusivity, at least in this function's current form.
#             TODO: It seems that we are handling two distinct things here,
#                   management of property names and unit conversion.  We might
#                   want to split this into separate functions.
#         '''
#         kwargs = props.copy()

#         if add_props is not None:
#             for k, v in add_props.items():
#                 kwargs[k] = v

#         if prune_props is not None:
#             for p in prune_props:
#                 del kwargs[p]

#         if rename_props is not None:
#             for old_prop, new_prop in rename_props.items():
#                 self._rename_prop(kwargs, old_prop, new_prop)

#         if op_and_value is not None:
#             for ov in op_and_value:
#                 _op, value = self._get_op_and_value(kwargs[ov])
#                 kwargs[ov] = value

#         if to_fraction is not None:
#             for f in to_fraction:
#                 kwargs[f] = self._percent_to_fraction(kwargs[f])

#         if to_kg_ms is not None:
#             for m in to_kg_ms:
#                 kwargs[m] = self._mpa_s_to_kg_ms(kwargs[m])

#         if to_n_m is not None:
#             for n in to_n_m:
#                 kwargs[n] = self._m_n_per_m_to_nm(kwargs[n])

#         if to_kg_m_2 is not None:
#             for k in to_kg_m_2:
#                 kwargs[k] = self._g_cm_2_to_kg_m_2(kwargs[k])

#         if to_kg_m_3 is not None:
#             for k in to_kg_m_3:
#                 kwargs[k] = self._g_cm_3_to_kg_m_3(kwargs[k])

#         return kwargs

#     def build_flash_point_kwargs(self, props, weathering):
#         '''
#             Build a flash point properties dictionary suitable to be passed in
#             as keyword args.  This is different enough from the generic
#             build_kwargs() that it gets its own function.
#             - props: a dictionary of properties
#             - weathering: The fractional oil weathering amount.
#         '''
#         fp_kwargs = props

#         fp_kwargs['weathering'] = weathering

#         fp_kwargs['min_temp_k'] = self._get_min_temp(fp_kwargs['flash_point'])
#         fp_kwargs['max_temp_k'] = self._get_max_temp(fp_kwargs['flash_point'])

#         del fp_kwargs['flash_point']

#         return fp_kwargs

#     def _build_pour_point_kwargs(self, props, weathering):
#         '''
#             Build a pour point properties dictionary suitable to be passed in
#             as keyword args.  This is different enough from the generic
#             build_kwargs() that it gets its own function.
#             - props: A dictionary of properties
#             - weathering: The fractional oil weathering amount.
#         '''
#         pp_kwargs = props

#         pp_kwargs['weathering'] = weathering

#         pp_kwargs['min_temp_k'] = self._get_min_temp(pp_kwargs['pour_point'])
#         pp_kwargs['max_temp_k'] = self._get_max_temp(pp_kwargs['pour_point'])

#         del pp_kwargs['pour_point']

#         return pp_kwargs

#     def _build_evaporation_kwargs(self, props, weathering,
#                                   equation, coeff_label):
#         '''
#             Build evaporation equation properties dictionary suitable to be
#             passed in as keyword args.  This is different enough from the
#             generic build_kwargs() that it gets its own function.
#             - props: Our properties from the Excel file.
#             - weathering: The fractional oil weathering amount.
#             - coeff_label: The property label containing our coefficients.
#                            This is a suffix that we will prepend with the
#                            coefficient we would like to get.
#         '''
#         evap_kwargs = props

#         evap_kwargs['weathering'] = weathering
#         evap_kwargs['equation'] = equation

#         evap_kwargs['a'] = evap_kwargs['a_{}'.format(coeff_label)]
#         evap_kwargs['b'] = evap_kwargs['b_{}'.format(coeff_label)]

#         del evap_kwargs['a_{}'.format(coeff_label)]
#         del evap_kwargs['b_{}'.format(coeff_label)]

#         if 'c_{}'.format(coeff_label) in evap_kwargs:
#             evap_kwargs['c'] = evap_kwargs['c_{}'.format(coeff_label)]

#             del evap_kwargs['c_{}'.format(coeff_label)]

#         return evap_kwargs

#     def _rename_prop(self, kwargs, old_prop, new_prop):
#         kwargs[new_prop] = kwargs[old_prop]
#         del kwargs[old_prop]

#     def _propagate_merged_excel_cells(self, objects, labels):
#         '''
#             Some content in the Excel file is represented in a group of
#             merged cells, in which only the first cell in our array has the
#             content.  So we would like to propagate this content to all
#             our viscosity objects.

#             Note: if we find ourselves doing this a lot, we will want to
#                   generalize this function a bit.
#         '''
#         for k in labels:
#             value = [v[k] for v in objects
#                      if k in v and v[k] is not None]
#             if len(value) > 0:
#                 value = value[0]  # first value, just to keep it simple.
#                 [v.update(((k, value),)) for v in objects]

#     def _get_op_and_value(self, value_in):
#         '''
#             Environment Canada sometimes puts a '<' or '>' in front of the
#             numeric value in a cell of the Excel spreadsheet.
#             In these cases, it is a string indicating greater than or less than
#             the float value.  So we need to split the content into an operator
#             and a float value.
#             Most of the time, it is a float value, in which we just
#             interpret it with no associated operator.
#         '''
#         op = None

#         if isinstance(value_in, (int, long, float)):
#             value = value_in
#         elif isinstance(value_in, (str, unicode)):
#             op = value_in.encode('utf8')[0]

#             if op in ('<', '>'):
#                     value = value_in[1:]
#             else:
#                 op = None
#                 value = value_in

#             try:
#                 value = float(value)
#             except ValueError:
#                 value = None
#         else:
#             value = None

#         return op, value

#     def _m_n_per_m_to_nm(self, m_n_per_m):
#         '''
#             Convert mN/m (dynes/cm) into N/m or return None value
#         '''
#         if isinstance(m_n_per_m, (int, long, float)):
#             return m_n_per_m * 1e-3
#         else:
#             return None

#     def _get_min_temp(self, temp_c):
#         '''
#             calculate the pour point minimum value from the Excel content
#             - Excel float content is in degrees Celcius

#             - if we have no preceding operater,     then min = the value.
#             - if we have a '>' preceding the float, then min = the value.
#             - if we have a '<' preceding the float, then min = None.
#             - otherwise,                                 min = None
#         '''
#         op, value = self._get_op_and_value(temp_c)

#         if op == '<':
#             value = None

#         return self._celcius_to_kelvin(value)

#     def _get_max_temp(self, temp_c):
#         '''
#             calculate the flash point minimum value from the Excel content
#             - Excel float content is in degrees Celcius

#             - if we have no preceding operater,     then max = the value.
#             - if we have a '<' preceding the float, then max = the value.
#             - if we have a '>' preceding the float, then max = None.
#             - otherwise,                                 max = None
#         '''
#         op, value = self._get_op_and_value(temp_c)

#         if op == '>':
#             value = None

#         return self._celcius_to_kelvin(value)

#     def _celcius_to_kelvin(self, temp_c):
#         if temp_c is not None:
#             temp_c += 273.15

#         return temp_c

#     def _g_cm_2_to_kg_m_2(self, g_cm_2):
#         if g_cm_2 is None:
#             kg_m_2 = None
#         else:
#             kg_m_2 = g_cm_2 * 10.0

#         return kg_m_2

#     def _g_cm_3_to_kg_m_3(self, g_cm_3):
#         if g_cm_3 is None:
#             kg_m_3 = None
#         else:
#             kg_m_3 = g_cm_3 * 1000.0

#         return kg_m_3

#     def _mpa_s_to_kg_ms(self, mpa_s):
#         '''
#             Environment Canada measures dynamic viscosity in (mPa * s), so we
#             need to convert to (kg / (m * s))
#         '''
#         if mpa_s is None:
#             kg_ms = None
#         else:
#             kg_ms = mpa_s * 1e-3

#         return kg_ms

#     def _percent_to_fraction(self, percent):
#         if percent is not None:
#             percent /= 100.0

#         return percent
