#
# PyMODM Model class definitions for our imported records that come from
# the Filemaker database.
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (MongoBaseField, CharField, BooleanField, FloatField,
                           EmbeddedDocumentListField)

from oil_database.models.common import Synonym

from .density import NoaaFmDensity
from .kvis import NoaaFmKVis
from .dvis import NoaaFmDVis
from .cut import NoaaFmCut
from .toxicity import NoaaFmToxicity


class ImportedRecord(MongoModel):
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
    oil_id = CharField(max_length=16)
    oil_name = CharField(max_length=100)

    product_type = CharField(choices=('crude', 'refined'), blank=True)
    location = CharField(max_length=64, blank=True)
    field_name = CharField(max_length=64)
    reference = CharField(max_length=80 * 20, blank=True)
    reference_date = CharField(max_length=10, blank=True)
    comments = CharField(max_length=80 * 5, blank=True)

    api = FloatField(blank=True)

    flash_point_min_k = FloatField(blank=True)
    flash_point_max_k = FloatField(blank=True)
    pour_point_min_k = FloatField(blank=True)
    pour_point_max_k = FloatField(blank=True)
    oil_water_interfacial_tension_n_m = FloatField(blank=True)
    oil_water_interfacial_tension_ref_temp_k = FloatField(blank=True)
    oil_seawater_interfacial_tension_n_m = FloatField(blank=True)
    oil_seawater_interfacial_tension_ref_temp_k = FloatField(blank=True)

    saturates = FloatField(blank=True)
    aromatics = FloatField(blank=True)
    resins = FloatField(blank=True)
    asphaltenes = FloatField(blank=True)

    sulphur = FloatField(blank=True)
    wax_content = FloatField(blank=True)
    benzene = FloatField(blank=True)

    adhesion = FloatField(blank=True)
    emuls_constant_min = FloatField(blank=True)
    emuls_constant_max = FloatField(blank=True)
    water_content_emulsion = FloatField(blank=True)
    conrandson_residuum = FloatField(blank=True)
    conrandson_crude = FloatField(blank=True)

    # relationship fields
    synonyms = EmbeddedDocumentListField(Synonym, blank=True)
    densities = EmbeddedDocumentListField(NoaaFmDensity, blank=True)
    dvis = EmbeddedDocumentListField(NoaaFmDVis, blank=True)
    kvis = EmbeddedDocumentListField(NoaaFmKVis, blank=True)
    cuts = EmbeddedDocumentListField(NoaaFmCut, blank=True)
    toxicities = EmbeddedDocumentListField(NoaaFmToxicity, blank=True)

    #
    # these attributes haven't been mapped to the main Oil object
    #
    cut_units = CharField(choices=('weight', 'volume'), blank=True)
    oil_class = CharField(choices=('group 1', 'group 2', 'group 3', 'group 4'),
                          blank=True)
    preferred_oils = BooleanField(default=False)

    paraffins = FloatField(blank=True)
    naphthenes = FloatField(blank=True)
    polars = FloatField(blank=True)
    nickel = FloatField(blank=True)
    vanadium = FloatField(blank=True)

    dispersability_temp_k = FloatField(blank=True)
    viscosity_multiplier = FloatField(blank=True)
    reid_vapor_pressure = FloatField(blank=True)
    k0y = FloatField(blank=True)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'oil-db-app'
        indexes = [IndexModel([('oil_id', ASCENDING)],
                              unique=True),
                   IndexModel([('oil_name', ASCENDING),
                               ('location', ASCENDING),
                               ('field_name', ASCENDING),
                               ('reference_date', ASCENDING)],
                              unique=True)]

    def __init__(self, **kwargs):
        # we will fail on any arguments that are not defined members
        # of this class
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(ImportedRecord, self).__init__(**kwargs)

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

    def __repr__(self):
        return "<ImportedRecord('{}')>".format(self.oil_name)
