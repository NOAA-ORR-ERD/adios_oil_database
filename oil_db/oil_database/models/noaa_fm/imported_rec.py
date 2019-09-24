#
# Model class definitions for our imported records that come from
# the Filemaker database.
#

from enum import Enum
from pydantic import BaseModel, constr
from typing import List

from oil_database.models.common import Synonym
from oil_database.models.common.enum_types import ProductTypeEnum

from .density import NoaaFmDensity
from .kvis import NoaaFmKVis
from .dvis import NoaaFmDVis
from .cut import NoaaFmCut
from .toxicity import NoaaFmToxicity


class CutUnitEnum(str, Enum):
    weight = 'weight'
    volume = 'volume'


class OilClassEnum(str, Enum):
    group_1 = 'group 1'
    group_2 = 'group 2'
    group_3 = 'group 3'
    group_4 = 'group 4'


class ImportedRecord(BaseModel):
    '''
        This object, and its related objects, is created from a
        single record inside the OilLib flat file.  The OilLib flat file
        is itself created from a filemaker export process, and is in two
        dimensional tabular format.

        Note: There are fields here that should probably be required, such as:
              - reference
              - product_type
              - densities/API
              - viscosities
              - cuts
              But we will go ahead and accept the record for import, and then
              handle them when we go through our estimations.
    '''
    oil_id: constr(max_length=16)  # primary key
    oil_name: constr(max_length=100)
    field_name: constr(max_length=64)

    product_type: ProductTypeEnum = None
    location: constr(max_length=64) = None
    reference: constr(max_length=80 * 20) = None
    reference_date: constr(max_length=10) = None  # should this be a datetime?
    comments: constr(max_length=80 * 5) = None

    api: float = None

    flash_point_min_k: float = None
    flash_point_max_k: float = None
    pour_point_min_k: float = None
    pour_point_max_k: float = None
    oil_water_interfacial_tension_n_m: float = None
    oil_water_interfacial_tension_ref_temp_k: float = None
    oil_seawater_interfacial_tension_n_m: float = None
    oil_seawater_interfacial_tension_ref_temp_k: float = None

    saturates: float = None
    aromatics: float = None
    resins: float = None
    asphaltenes: float = None

    sulphur: float = None
    wax_content: float = None
    benzene: float = None

    adhesion: float = None
    emuls_constant_min: float = None
    emuls_constant_max: float = None
    water_content_emulsion: float = None
    conrandson_residuum: float = None
    conrandson_crude: float = None

    # relationship fields
    synonyms: List[Synonym] = None
    densities: List[NoaaFmDensity] = None
    dvis: List[NoaaFmDVis] = None
    kvis: List[NoaaFmKVis] = None
    cuts: List[NoaaFmCut] = None
    toxicities: List[NoaaFmToxicity] = None

    #
    # these attributes haven't been mapped to the main Oil object
    #
    cut_units: CutUnitEnum = None
    oil_class: OilClassEnum = None
    preferred_oils: bool = False

    paraffins: float = None
    naphthenes: float = None
    polars: float = None
    nickel: float = None
    vanadium: float = None

    dispersability_temp_k: float = None
    viscosity_multiplier: float = None
    reid_vapor_pressure: float = None
    k0y: float = None

    @classmethod
    def from_record_parser(cls, parser):
        '''
            It is intended that the database object constructor need not know
            how to build properties from the raw record data coming from a
            data source.  That is the job of the record parser.

            The parser takes a set of record data and exposes a set of suitable
            properties for building our class.
        '''
        kwargs = {}

        cls._set_properties(kwargs, parser)

        rec = cls(**kwargs)

        return rec

    @classmethod
    def _set_properties(cls, kwargs, parser):
        '''
            Here, we handle the parser properties.
        '''
        parser_api = parser.get_interface_properties()

        for attr in cls.__fields__.keys():
            if attr in parser_api:
                kwargs[attr] = getattr(parser, attr)

    def __repr__(self):
        return "<ImportedRecord('{}')>".format(self.oil_name)
