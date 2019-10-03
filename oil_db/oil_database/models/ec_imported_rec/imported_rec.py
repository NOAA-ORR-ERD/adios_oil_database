#
# Model class definitions for our Environment Canada imported records
# that come from the EC spreadsheet (or possibly the .csv file).
#
from datetime import datetime
from pydantic import constr
from typing import List

from oil_database.models.common import MongoBaseModel, Synonym

from oil_database.models.oil import (EvaporationEq,
                                     CCMESaturateCxx,
                                     CCMEAromaticCxx,
                                     CCMETotalPetroleumCxx)

from .density import ECDensity
from .api import ECApiGravity
from .dvis import ECDVis
from .cut import ECCut
from .interfacial_tension import ECInterfacialTension
from .flash_point import ECFlashPoint
from .pour_point import ECPourPoint
from .adhesion import ECAdhesion
from .emulsion import ECEmulsion
from .corexit import ECCorexit9500
from .sulfur import ECSulfur
from .water import ECWater
from .wax import ECWax
from .benzene import ECBenzene
from .headspace import ECHeadspace
from .chromatography import ECGasChromatography
from .ccme import EcCCMEFraction
from .alkylated_pah import ECAlkylatedTotalPAH
from .sara_fraction import ECSARAFraction
from .biomarkers import ECBiomarkers
from .alkanes import ECNAlkanes


class ECImportedRecord(MongoBaseModel):
    '''
        This class, and its related objects, represents a single record inside
        the Environment Canada source data spreadsheet.

        The EC source data is a two dimensional tabular spreadsheet, but it
        contains an implied third dimension, that of weathering.  So for each
        record, most properties will be lists of properties indexed by their
        associated weathered amount.

        Note: There are fields here that should probably be required, such as:
              - reference
              - product_type
              - densities/API
              - viscosities
              - cuts
              But we will go ahead and accept the record for import, and then
              handle them when we are ready to load it into the main Oil table.
    '''
    oil_id: constr(max_length=16)
    name: constr(max_length=100)

    # EC location data is primarily in the 'source' field, with very infrequent
    # specifications of location in the 'comments' field.  It doesn't really
    # specify a field name, Just a region or sovereign state.
    location: constr(max_length=64) = None

    reference: constr(max_length=80 * 20) = None
    reference_date: datetime = None
    sample_date: datetime = None

    comments: constr(max_length=80 * 5) = None

    # EC data doesn't really have a field for this, but this is kinda important
    # to know should the need arise for estimating any properties.
    product_type: constr(max_length=16) = None

    densities: List[ECDensity] = None
    apis: List[ECApiGravity] = None

    dvis: List[ECDVis] = None

    ifts: List[ECInterfacialTension] = None

    flash_points: List[ECFlashPoint] = None
    pour_points: List[ECPourPoint] = None

    cuts: List[ECCut] = None

    adhesions: List[ECAdhesion] = None
    evaporation_eqs: List[EvaporationEq] = None
    emulsions: List[ECEmulsion] = None
    corexit: List[ECCorexit9500] = None

    # Note: this is how they spell sulphur in the Env Canada datasheet
    sulfur: List[ECSulfur] = None

    water: List[ECWater] = None
    benzene: List[ECBenzene] = None
    headspace: List[ECHeadspace] = None
    chromatography: List[ECGasChromatography] = None

    ccme: List[EcCCMEFraction] = None
    ccme_f1: List[CCMESaturateCxx] = None
    ccme_f2: List[CCMEAromaticCxx] = None
    ccme_tph: List[CCMETotalPetroleumCxx] = None

    alkylated_pahs: List[ECAlkylatedTotalPAH] = None

    biomarkers: List[ECBiomarkers] = None
    wax_content: List[ECWax] = None
    alkanes: List[ECNAlkanes] = None

    sara_total_fractions: List[ECSARAFraction] = None

    # relationship fields
    synonyms: List[Synonym] = None

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
        return "<ECImportedRecord('{}')>".format(self.name)
