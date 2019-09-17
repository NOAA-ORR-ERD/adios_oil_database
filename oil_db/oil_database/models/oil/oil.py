#
# PyMODM Model class definitions for our Environment Canada imported records
# that come from the EC spreadsheet (or possibly the .csv file).
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (MongoBaseField,
                           CharField, DateTimeField,
                           ListField, EmbeddedDocumentListField,
                           ReferenceField)

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


class Oil(MongoModel):
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
    oil_id = CharField(max_length=16, primary_key=True)
    name = CharField(max_length=100, required=True)

    location = CharField(max_length=64, blank=True)

    reference = CharField(max_length=80 * 20, blank=True)
    reference_date = DateTimeField(blank=True)
    sample_date = DateTimeField(blank=True)

    comments = CharField(max_length=80 * 5, blank=True)
    product_type = CharField(max_length=16, blank=True)
    categories = ListField(ReferenceField(Category), blank=True, default=[])

    status = ListField(CharField(max_length=64), blank=True, default=[])

    synonyms = EmbeddedDocumentListField(Synonym, blank=True)

    densities = EmbeddedDocumentListField(Density, blank=True)
    apis = EmbeddedDocumentListField(ApiGravity, blank=True)

    # not sure if we are going to deal with DVis. might be KVis only
    dvis = EmbeddedDocumentListField(DVis, blank=True)
    kvis = EmbeddedDocumentListField(KVis, blank=True)

    ifts = EmbeddedDocumentListField(InterfacialTension, blank=True)

    flash_points = EmbeddedDocumentListField(FlashPoint, blank=True)
    pour_points = EmbeddedDocumentListField(PourPoint, blank=True)

    cuts = EmbeddedDocumentListField(Cut, blank=True)

    adhesions = EmbeddedDocumentListField(Adhesion, blank=True)
    evaporation_eqs = EmbeddedDocumentListField(EvaporationEq, blank=True)
    emulsions = EmbeddedDocumentListField(Emulsion, blank=True)
    chemical_dispersibility = EmbeddedDocumentListField(ChemicalDispersibility,
                                                        blank=True)

    # Note: this is how they spell sulphur in the Env Canada datasheet
    sulfur = EmbeddedDocumentListField(Sulfur, blank=True)

    water = EmbeddedDocumentListField(Water, blank=True)
    benzene = EmbeddedDocumentListField(Benzene, blank=True)
    headspace = EmbeddedDocumentListField(Headspace, blank=True)
    chromatography = EmbeddedDocumentListField(GasChromatography, blank=True)

    ccme = EmbeddedDocumentListField(CCMEFraction, blank=True)
    ccme_f1 = EmbeddedDocumentListField(CCMESaturateCxx, blank=True)
    ccme_f2 = EmbeddedDocumentListField(CCMEAromaticCxx, blank=True)
    ccme_tph = EmbeddedDocumentListField(CCMETotalPetroleumCxx, blank=True)

    alkylated_pahs = EmbeddedDocumentListField(AlkylatedTotalPAH, blank=True)

    biomarkers = EmbeddedDocumentListField(Biomarkers, blank=True)
    wax_content = EmbeddedDocumentListField(Wax, blank=True)
    alkanes = EmbeddedDocumentListField(NAlkanes, blank=True)

    sara_total_fractions = EmbeddedDocumentListField(SARAFraction, blank=True)

    # The following attributes are unique to the NOAA Filemaker records
    toxicities = EmbeddedDocumentListField(Toxicity, blank=True)
    conradson = EmbeddedDocumentListField(Conradson, blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'oil-db-app'
        indexes = [IndexModel([('name', ASCENDING),
                               ('location', ASCENDING),
                               ('reference_date', ASCENDING)],
                              unique=True)]

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a in list(kwargs.keys()):
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super().__init__(**kwargs)

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

        cls._set_scalar_properties(kwargs, parser)
        cls._set_embedded_list_properties(kwargs, parser)

        rec = cls(**kwargs)

        return rec

    @classmethod
    def _set_scalar_properties(cls, kwargs, parser):
        '''
            Here, we handle the parser properties that contain a single
            scalar value.
        '''
        parser_api = parser.get_interface_properties()

        for attr, value in cls.__dict__.items():
            if (attr in parser_api and
                    isinstance(value, MongoBaseField) and
                    not isinstance(value, EmbeddedDocumentListField)):
                kwargs[attr] = getattr(parser, attr)

    @classmethod
    def _set_embedded_list_properties(cls, kwargs, parser):
        '''
            Here, we handle the parser properties that contain a list of
            embedded documents.
        '''
        parser_api = parser.get_interface_properties()

        for attr, value in cls.__dict__.items():
            if (attr in parser_api and
                    isinstance(value, EmbeddedDocumentListField)):
                embedded_model = value.related_model

                if getattr(parser, attr) is None:
                    kwargs[attr] = None
                else:
                    kwargs[attr] = [embedded_model(**sub_kwargs)
                                    for sub_kwargs in getattr(parser, attr)]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "<Oil('{}')>".format(self.name)
