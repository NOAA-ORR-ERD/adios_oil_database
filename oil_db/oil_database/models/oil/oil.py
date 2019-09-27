#
# PyMODM Model class definitions for our Environment Canada imported records
# that come from the EC spreadsheet (or possibly the .csv file).
#
from datetime import datetime
from pydantic import BaseModel, constr
from typing import List

from oil_database.models.common import Synonym
from oil_database.models.common import Category

from .density import Density
from .api import ApiGravity
from .dvis import DVis
from .kvis import KVis
from .cut import Cut
from .interfacial_tension import InterfacialTension
from .flash_point import FlashPoint
from .pour_point import PourPoint
from .adhesion import Adhesion
from .evaporation_eq import EvaporationEq
from .emulsion import Emulsion
from .dispersibility import ChemicalDispersibility
from .sulfur import Sulfur
from .water import Water
from .wax import Wax
from .benzene import Benzene
from .headspace import Headspace
from .chromatography import GasChromatography
from .ccme import (CCMEFraction,
                   CCMESaturateCxx,
                   CCMEAromaticCxx,
                   CCMETotalPetroleumCxx)
from .alkylated_pah import AlkylatedTotalPAH
from .sara_fraction import SARAFraction
from .alkanes import NAlkanes
from .biomarkers import Biomarkers
from .toxicity import Toxicity
from .conradson import Conradson


class Oil(BaseModel):
    '''
        This class, and its related objects, represents a single record inside
        the NOAA oil database.

        It is modeled with a similar structure as the Environment Canada
        source data, it having the richest set of attributes.  But it is
        intended to support other sources, such as the NOAA Filemaker oil
        library, and the Exxon oil assays.

        There are a few fields that are required in order to be accepted into
        the NOAA oil database:
        - unique identifier
        - oil name
        - reference (not sure how strict we should be about this)
        - reference_date
        - product_type
        - densities/API
        - viscosities
        - distillation cuts
    '''
    oil_id: constr(max_length=16)
    name: constr(max_length=100)

    location: constr(max_length=64) = None

    reference: constr(max_length=80 * 20) = None
    reference_date: datetime = None
    sample_date: datetime = None

    comments: constr(max_length=80 * 5) = None
    product_type: constr(max_length=16) = None

    categories: List[Category] = None

    status: List[constr(max_length=64)] = None

    synonyms: List[Synonym] = None

    densities: List[Density] = None
    apis: List[ApiGravity] = None

    # not sure if we are going to deal with DVis. might be KVis only
    dvis: List[DVis] = None
    kvis: List[KVis] = None

    ifts: List[InterfacialTension] = None

    flash_points: List[FlashPoint] = None
    pour_points: List[PourPoint] = None

    cuts: List[Cut] = None

    adhesions: List[Adhesion] = None
    evaporation_eqs: List[EvaporationEq] = None
    emulsions: List[Emulsion] = None
    chemical_dispersibility: List[ChemicalDispersibility] = None

    # Note: this is how they spell sulphur in the Env Canada datasheet
    sulfur: List[Sulfur] = None

    water: List[Water] = None
    benzene: List[Benzene] = None
    headspace: List[Headspace] = None
    chromatography: List[GasChromatography] = None

    ccme: List[CCMEFraction] = None
    ccme_f1: List[CCMESaturateCxx] = None
    ccme_f2: List[CCMEAromaticCxx] = None
    ccme_tph: List[CCMETotalPetroleumCxx] = None

    alkylated_pahs: List[AlkylatedTotalPAH] = None

    biomarkers: List[Biomarkers] = None
    wax_content: List[Wax] = None
    alkanes: List[NAlkanes] = None

    sara_total_fractions: List[SARAFraction] = None

    # The following attributes are unique to the NOAA Filemaker records
    toxicities: List[Toxicity] = None
    conradson: List[Conradson] = None

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
        return "<Oil('{}')>".format(self.name)
