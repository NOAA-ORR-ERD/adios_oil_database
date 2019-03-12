#
# PyMODM Model class definitions for our imported records that come from
# the Filemaker database.
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (CharField,
                           BooleanField,
                           FloatField,
                           EmbeddedDocumentListField)

from .common_props import Synonym, Density, KVis, DVis, Cut, Toxicity


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

    custom = BooleanField(default=False)
    location = CharField(max_length=64, blank=True)
    field_name = CharField(max_length=64)
    reference = CharField(max_length=80 * 20, blank=True)
    reference_date = CharField(max_length=22)
    api = FloatField(blank=True)
    pour_point_min_k = FloatField(blank=True)
    pour_point_max_k = FloatField(blank=True)
    product_type = CharField(max_length=16, blank=True)
    comments = CharField(max_length=80 * 5, blank=True)
    asphaltenes = FloatField(blank=True)
    wax_content = FloatField(blank=True)
    aromatics = FloatField(blank=True)
    water_content_emulsion = FloatField(blank=True)
    emuls_constant_min = FloatField(blank=True)
    emuls_constant_max = FloatField(blank=True)
    flash_point_min_k = FloatField(blank=True)
    flash_point_max_k = FloatField(blank=True)
    oil_water_interfacial_tension_n_m = FloatField(blank=True)
    oil_water_interfacial_tension_ref_temp_k = FloatField(blank=True)
    oil_seawater_interfacial_tension_n_m = FloatField(blank=True)
    oil_seawater_interfacial_tension_ref_temp_k = FloatField(blank=True)
    cut_units = CharField(max_length=16, blank=True)
    oil_class = CharField(max_length=16, blank=True)
    adhesion = FloatField(blank=True)
    benzene = FloatField(blank=True)
    naphthenes = FloatField(blank=True)
    paraffins = FloatField(blank=True)
    polars = FloatField(blank=True)
    resins = FloatField(blank=True)
    saturates = FloatField(blank=True)
    sulphur = FloatField(blank=True)
    reid_vapor_pressure = FloatField(blank=True)
    viscosity_multiplier = FloatField(blank=True)
    nickel = FloatField(blank=True)
    vanadium = FloatField(blank=True)
    conrandson_residuum = FloatField(blank=True)
    conrandson_crude = FloatField(blank=True)
    dispersability_temp_k = FloatField(blank=True)
    preferred_oils = BooleanField(default=False)
    k0y = FloatField()

    # relationship fields
    synonyms = EmbeddedDocumentListField(Synonym, blank=True)
    densities = EmbeddedDocumentListField(Density, blank=True)
    kvis = EmbeddedDocumentListField(KVis, blank=True)
    dvis = EmbeddedDocumentListField(DVis, blank=True)
    cuts = EmbeddedDocumentListField(Cut, blank=True)
    toxicities = EmbeddedDocumentListField(Toxicity, blank=True)

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

        # It's amazing that PyMODM wouldn't do this for you automatically.
        # Basically, attributes of type EmbeddedDocumentListField kinda don't
        # exist until they are assigned a value.  You can print these
        # attributes, and they look like an empty list that you can use.
        # But try appending something to them and nothing happens.
        # The trick is you have to assign a list [] to them before they
        # can be used.
        # I have seen some projects pass in a default=[] argument to the
        # constructor of EmbeddedDocumentListField, but that's an almost
        # guaranteed source of bugs in Python.  You should almost never choose
        # a container type for a default argument to a function.  In fact,
        # I tried it and got some crazy distillation cuts on a few records.
        # So we make the inital assignment here.
        self.synonyms = []
        self.densities = []
        self.kvis = []
        self.dvis = []
        self.cuts = []
        self.toxicities = []

    def __repr__(self):
        return "<ImportedRecord('{}')>".format(self.oil_name)
