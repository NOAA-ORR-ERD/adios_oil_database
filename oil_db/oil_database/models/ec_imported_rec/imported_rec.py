#
# PyMODM Model class definitions for our Environment Canada imported records
# that come from the EC spreadsheet (or possibly the .csv file).
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (MongoBaseField, CharField, DateTimeField,
                           EmbeddedDocumentListField)

from oil_database.models.common import Synonym
from oil_database.models.oil import EvaporationEq
from oil_database.models.oil import (CCMESaturateCxx,
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


class ECImportedRecord(MongoModel):
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
    oil_id = CharField(max_length=16, primary_key=True)
    name = CharField(max_length=100)

    # EC location data is primarily in the 'source' field, with very infrequent
    # specifications of location in the 'comments' field.  It doesn't really
    # specify a field name, Just a region or sovereign state.
    location = CharField(max_length=64, blank=True)

    reference = CharField(max_length=80 * 20, blank=True)
    reference_date = DateTimeField(blank=True)
    sample_date = DateTimeField(blank=True)

    comments = CharField(max_length=80 * 5, blank=True)

    # EC data doesn't really have a field for this, but this is kinda important
    # to know should the need arise for estimating any properties.
    product_type = CharField(max_length=16, blank=True)

    densities = EmbeddedDocumentListField(ECDensity, blank=True)
    apis = EmbeddedDocumentListField(ECApiGravity, blank=True)

    dvis = EmbeddedDocumentListField(ECDVis, blank=True)

    ifts = EmbeddedDocumentListField(ECInterfacialTension, blank=True)

    flash_points = EmbeddedDocumentListField(ECFlashPoint, blank=True)
    pour_points = EmbeddedDocumentListField(ECPourPoint, blank=True)

    cuts = EmbeddedDocumentListField(ECCut, blank=True)

    adhesions = EmbeddedDocumentListField(ECAdhesion, blank=True)
    evaporation_eqs = EmbeddedDocumentListField(EvaporationEq, blank=True)
    emulsions = EmbeddedDocumentListField(ECEmulsion, blank=True)
    corexit = EmbeddedDocumentListField(ECCorexit9500, blank=True)

    # Note: this is how they spell sulphur in the Env Canada datasheet
    sulfur = EmbeddedDocumentListField(ECSulfur, blank=True)

    water = EmbeddedDocumentListField(ECWater, blank=True)
    benzene = EmbeddedDocumentListField(ECBenzene, blank=True)
    headspace = EmbeddedDocumentListField(ECHeadspace, blank=True)
    chromatography = EmbeddedDocumentListField(ECGasChromatography, blank=True)

    ccme = EmbeddedDocumentListField(EcCCMEFraction, blank=True)
    ccme_f1 = EmbeddedDocumentListField(CCMESaturateCxx, blank=True)
    ccme_f2 = EmbeddedDocumentListField(CCMEAromaticCxx, blank=True)
    ccme_tph = EmbeddedDocumentListField(CCMETotalPetroleumCxx, blank=True)

    alkylated_pahs = EmbeddedDocumentListField(ECAlkylatedTotalPAH, blank=True)

    biomarkers = EmbeddedDocumentListField(ECBiomarkers, blank=True)
    wax_content = EmbeddedDocumentListField(ECWax, blank=True)
    alkanes = EmbeddedDocumentListField(ECNAlkanes, blank=True)

    sara_total_fractions = EmbeddedDocumentListField(ECSARAFraction,
                                                     blank=True)

    # relationship fields
    synonyms = EmbeddedDocumentListField(Synonym, blank=True)

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

        super(ECImportedRecord, self).__init__(**kwargs)

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
        return "<ImportedRecord('{}')>".format(self.name)
