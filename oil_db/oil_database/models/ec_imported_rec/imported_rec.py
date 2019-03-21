#
# PyMODM Model class definitions for our Environment Canada imported records
# that come from the EC spreadsheet (or possibly the .csv file).
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (MongoBaseField, CharField, FloatField, ListField,
                           DateTimeField, EmbeddedDocumentListField)

from ..common.common_props import Synonym, Density, DVis, Cut, SARAFraction

from .interfacial_tension import InterfacialTension
from .flash_point import FlashPoint
from .pour_point import PourPoint
from .adhesion import Adhesion
from .evaporation_eq import EvaporationEq
from .emulsion import Emulsion
from .corexit import Corexit9500
from .sulfur import Sulfur
from .water import Water
from .benzene import Benzene
from .headspace import Headspace
from .chromatography import GasChromatography
from .ccme import (CCMEFraction,
                   CCMESaturateCxx,
                   CCMEAromaticCxx,
                   CCMETotalPetroleumCxx)
from .alkylated_pah import AlkylatedTotalPAH
from .biomarkers import Biomarkers
from .wax import Wax
from .alkanes import NAlkane

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=2, width=120)


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
              handle them when we go through our estimations.

        TODO:
        -
    '''
    oil_id = CharField(max_length=16)
    name = CharField(max_length=100)

    # EC location data is primarily in the 'source' field, with very infrequent
    # specifications of location in the 'comments' field.  It doesn't really
    # specify a field name, Just a region or sovereign state.
    location = CharField(max_length=64, blank=True)

    # EC reference field exists, and most records have a reliable sample date
    # that we could use here as a reference date.
    reference = CharField(max_length=80 * 20, blank=True)
    reference_date = DateTimeField(blank=True)

    comments = CharField(max_length=80 * 5, blank=True)

    # EC data doesn't really have a field for this, but this is kinda important
    # to know should the need arise for estimating any properties.
    product_type = CharField(max_length=16, blank=True)

    densities = EmbeddedDocumentListField(Density, blank=True)
    api = ListField(FloatField(), blank=True, default=[])

    dvis = EmbeddedDocumentListField(DVis, blank=True)

    ifts = EmbeddedDocumentListField(InterfacialTension, blank=True)

    flash_points = EmbeddedDocumentListField(FlashPoint, blank=True)
    pour_points = EmbeddedDocumentListField(PourPoint, blank=True)

    cuts = EmbeddedDocumentListField(Cut, blank=True)

    adhesions = EmbeddedDocumentListField(Adhesion, blank=True)
    evaporation_eqs = EmbeddedDocumentListField(EvaporationEq, blank=True)
    emulsions = EmbeddedDocumentListField(Emulsion, blank=True)
    corexit = EmbeddedDocumentListField(Corexit9500, blank=True)

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
    alkanes = EmbeddedDocumentListField(NAlkane, blank=True)

    sara_total_fractions = EmbeddedDocumentListField(SARAFraction, blank=True)

    # relationship fields
    synonyms = EmbeddedDocumentListField(Synonym, blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'oil-db-app'
        indexes = [IndexModel([('oil_id', ASCENDING)],
                              unique=True),
                   IndexModel([('name', ASCENDING),
                               ('location', ASCENDING),
                               ('reference_date', ASCENDING)],
                              unique=True)]

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
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

        for attr, value in cls.__dict__.iteritems():
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

        for attr, value in cls.__dict__.iteritems():
            if (attr in parser_api and
                    isinstance(value, EmbeddedDocumentListField)):
                embedded_model = value.related_model

                if getattr(parser, attr) is None:
                    kwargs[attr] = None
                else:
                    kwargs[attr] = [embedded_model(**sub_kwargs)
                                    for sub_kwargs in getattr(parser, attr)]

    @classmethod
    def from_record_parser_old(cls, parser):
        '''
            It is intended that the database object constructor need not know
            how to build properties from the raw record data coming from a
            data source.  That is the job of the record parser.

            The parser takes a set of record data and exposes a set of suitable
            properties for building our class.
        '''
        kwargs = {}
        kwargs['oil_id'] = parser.ec_oil_id
        kwargs['oil_name'] = parser.name
        kwargs['location'] = parser.location
        kwargs['reference'] = parser.reference
        kwargs['reference_date'] = parser.reference_date
        kwargs['comments'] = parser.comments

        # kwargs['product_type'] = parser.product_type

        rec = cls(**kwargs)

        rec.densities.extend([Density(**args) for args in parser.densities])
        rec.api.extend(parser.api)
        rec.dvis.extend([DVis(**args) for args in parser.viscosities])
        rec.cuts.extend([Cut(**args) for args in parser.distillation_cuts])

        rec.flash_points.extend([FlashPoint(**args)
                                 for args in parser.flash_points])
        rec.pour_points.extend([PourPoint(**args)
                                for args in parser.pour_points])

        rec.ift.extend([InterfacialTension(**args)
                        for args in parser.interfacial_tensions])

        rec.adhesions.extend([Adhesion(**args) for args in parser.adhesions])

        rec.evaporation_eqs.extend([EvaporationEq(**args)
                                    for args in parser.evaporation_eqs])

        rec.emulsions.extend([Emulsion(**args) for args in parser.emulsions])
        rec.corexit.extend([Corexit9500(**args) for args in parser.corexit])
        rec.sulphur.extend([Sulfur(**args) for args in parser.sulfur_content])
        rec.water.extend([Water(**args) for args in parser.water_content])

        rec.benzene.extend([Benzene(**args)
                            for args in parser.benzene_content])

        rec.headspace.extend([Headspace(**args) for args in parser.headspace])

        rec.chromatography.extend([GasChromatography(**args)
                                   for args in parser.chromatography])

        rec.ccme.extend([CCMEFraction(**args) for args in parser.ccme])
        rec.ccme_f1.extend([CCMESaturateCxx(**args)
                            for args in parser.ccme_f1])
        rec.ccme_f2.extend([CCMEAromaticCxx(**args)
                            for args in parser.ccme_f2])
        rec.ccme_tph.extend([CCMETotalPetroleumCxx(**args)
                            for args in parser.ccme_tph])

        rec.alkylated_pahs.extend([AlkylatedTotalPAH(**args)
                                   for args in parser.alkylated_pahs])

        rec.biomarkers.extend([Biomarkers(**args)
                               for args in parser.biomarkers])

        rec.wax_content.extend([Wax(**args) for args in parser.wax_content])
        rec.alkanes.extend([NAlkane(**args) for args in parser.alkanes])

        rec.sara_total_fractions.extend([SARAFraction(**args)
                                         for args
                                         in parser.sara_total_fractions])

        return rec

    def __repr__(self):
        return "<ImportedRecord('{}')>".format(self.oil_name)
