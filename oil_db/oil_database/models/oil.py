#
# PyMODM Model class definitions for our general purpose oil object
#
from pymongo.write_concern import WriteConcern
from pymongo import IndexModel, ASCENDING

from pymodm import MongoModel
from pymodm.fields import (CharField, FloatField, DictField, ReferenceField,
                           EmbeddedDocumentListField, ListField)

from .common.common_props import (Density, KVis, Cut,
                                  SARAFraction, SARADensity, MolecularWeight)
from .imported_rec import ImportedRecord
from .category import Category


class Oil(MongoModel):
    '''
        This is the main oil object that is built from an imported record.
    '''
    oil_id = CharField(max_length=16)
    name = CharField(max_length=100)

    api = FloatField(blank=True)

    oil_water_interfacial_tension_n_m = FloatField(blank=True)
    oil_water_interfacial_tension_ref_temp_k = FloatField(blank=True)
    oil_seawater_interfacial_tension_n_m = FloatField(blank=True)
    oil_seawater_interfacial_tension_ref_temp_k = FloatField(blank=True)

    pour_point_min_k = FloatField(blank=True)
    pour_point_max_k = FloatField(blank=True)

    flash_point_min_k = FloatField(blank=True)
    flash_point_max_k = FloatField(blank=True)

    adhesion_kg_m_2 = FloatField(blank=True)
    bullwinkle_time = FloatField(blank=True)
    bullwinkle_fraction = FloatField(blank=True)
    emulsion_water_fraction_max = FloatField(blank=True)
    product_type = CharField(max_length=16)
    solubility = FloatField(blank=True)
    k0y = FloatField(blank=True)

    nickel_ppm = FloatField(blank=True)
    vanadium_ppm = FloatField(blank=True)

    saturates_fraction = FloatField(blank=True)
    aromatics_fraction = FloatField(blank=True)
    resins_fraction = FloatField(blank=True)
    asphaltenes_fraction = FloatField(blank=True)

    polars_fraction = FloatField(blank=True)
    benzene_fraction = FloatField(blank=True)
    sulphur_fraction = FloatField(blank=True)
    paraffins_fraction = FloatField(blank=True)
    wax_content_fraction = FloatField(blank=True)
    naphthenes_fraction = FloatField(blank=True)

    quality_index = FloatField(blank=True)

    densities = EmbeddedDocumentListField(Density, blank=True)
    kvis = EmbeddedDocumentListField(KVis, blank=True)
    cuts = EmbeddedDocumentListField(Cut, blank=True)
    sara_fractions = EmbeddedDocumentListField(SARAFraction, blank=True)
    sara_densities = EmbeddedDocumentListField(SARADensity, blank=True)
    molecular_weights = EmbeddedDocumentListField(MolecularWeight, blank=True)

    # This attribute stores flags that a particular oil property is estimated.
    estimated = DictField(blank=True)

    categories = ListField(ReferenceField(Category), blank=True, default=[])

    imported = ReferenceField(ImportedRecord)

    class Meta:
        write_concern = WriteConcern(j=True)
        connection_alias = 'oil-db-app'
        indexes = [IndexModel([('oil_id', ASCENDING)],
                              unique=True)]

    def __init__(self, **kwargs):
        for a, _v in kwargs.items():
            if (a not in self.__class__.__dict__):
                del kwargs[a]

        super(Oil, self).__init__(**kwargs)

        self.densities = []
        self.kvis = []
        self.cuts = []
        self.sara_fractions = []
        self.sara_densities = []
        self.molecular_weights = []
        self.estimated = {}

    @classmethod
    def from_json(cls, oil_json):
        oil_obj = cls(**oil_json)
        oil_obj._add_embedded_document_list_fields(oil_json)
        # oil_obj._add_categories_from_json(oil_json)
        return oil_obj

    def _add_embedded_document_list_fields(self, oil_json):
        for dlf, model_class in self.embedded_document_list_fields:
            if dlf in oil_json:
                for kwargs in oil_json[dlf]:
                    obj = model_class(**kwargs)
                    getattr(self, dlf).append(obj)

    @property
    def embedded_document_list_fields(self):
        return [(k, v.related_model)
                for k, v in self.__class__.__dict__.iteritems()
                if isinstance(v, EmbeddedDocumentListField)]

    def __repr__(self):
        return '<Oil("{0.name}")>'.format(self)

    def __str__(self):
        return self.__repr__()
