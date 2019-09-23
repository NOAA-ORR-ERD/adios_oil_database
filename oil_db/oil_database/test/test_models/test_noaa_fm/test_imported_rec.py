'''
    Test our NOAA Filemaker imported record model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.noaa_fm import ImportedRecord
from _pylief import NONE


class TestNoaaImportedRecord():
    @pytest.mark.parametrize('oil_id, oil_name, field_name',
                             [
                              ('AD00001', 'Oil Name', 'Field Name'),
                              pytest.param(
                                  None, None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, None, 'Field Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 'Oil Name', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 'Oil Name', 'Field Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'AD00001', None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'AD00001', None, 'Field Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'AD00001', 'Oil Name', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'OilIDIsMuchTooLong', 'Oil Name', 'Field Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'AD00001',
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 ',
                                  None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'AD00001', 'Oil Name',
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, oil_id, oil_name, field_name):
        if oil_id is None and oil_name is None and field_name is None:
            obj = ImportedRecord()
        elif oil_name is None and field_name is None:
            obj = ImportedRecord(oil_id=oil_id)
        elif oil_id is None and field_name is None:
            obj = ImportedRecord(oil_name=oil_name)
        elif oil_id is None and oil_name is None:
            obj = ImportedRecord(field_name=field_name)
        elif oil_id is None:
            obj = ImportedRecord(oil_name=oil_name, field_name=field_name)
        elif oil_name is None:
            obj = ImportedRecord(oil_id=oil_id, field_name=field_name)
        elif field_name is None:
            obj = ImportedRecord(oil_id=oil_id, oil_name=oil_name)
        else:
            obj = ImportedRecord(oil_id=oil_id, oil_name=oil_name,
                                 field_name=field_name)

        assert obj.oil_id == oil_id
        assert obj.oil_name == oil_name
        assert obj.field_name == field_name

    def test_init_defaults(self):
        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name')

        assert obj.product_type is None
        assert obj.location is None
        assert obj.reference is None
        assert obj.reference_date is None
        assert obj.comments is None

        assert obj.api is None

        assert obj.flash_point_min_k is None
        assert obj.flash_point_max_k is None
        assert obj.pour_point_min_k is None
        assert obj.pour_point_max_k is None

        assert obj.oil_water_interfacial_tension_n_m is None
        assert obj.oil_water_interfacial_tension_ref_temp_k is None
        assert obj.oil_seawater_interfacial_tension_n_m is None
        assert obj.oil_seawater_interfacial_tension_ref_temp_k is None

        assert obj.saturates is None
        assert obj.aromatics is None
        assert obj.resins is None
        assert obj.asphaltenes is None

        assert obj.sulphur is None
        assert obj.wax_content is None
        assert obj.benzene is None

        assert obj.adhesion is None
        assert obj.emuls_constant_min is None
        assert obj.emuls_constant_max is None
        assert obj.water_content_emulsion is None
        assert obj.conrandson_residuum is None
        assert obj.conrandson_crude is None

        assert obj.synonyms is None
        assert obj.densities is None
        assert obj.dvis is None
        assert obj.kvis is None
        assert obj.cuts is None
        assert obj.toxicities is None

        assert obj.cut_units is None
        assert obj.oil_class is None
        assert obj.preferred_oils is False
        assert obj.paraffins is None
        assert obj.naphthenes is None
        assert obj.polars is None
        assert obj.nickel is None
        assert obj.vanadium is None
        assert obj.dispersability_temp_k is None
        assert obj.viscosity_multiplier is None
        assert obj.reid_vapor_pressure is None
        assert obj.k0y is None

    @pytest.mark.parametrize('product_type, location, '
                             'reference, reference_date, comments',
                             [
                              ('crude', 'The Location',
                               'A Reference', '01011970', 'A comment'),
                              pytest.param(
                                  'InvalidProductType', 'The Location',
                                  'A Reference', '01011970', 'A comment',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'crude',
                                  'A long Location field '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 ',
                                  'A Reference', '01011970', 'A comment',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'crude', 'The Location',
                                  'A really long Reference'
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 ',
                                  '01011970', 'A comment',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'crude', 'The Location', 'A Reference',
                                  'January 1, 1970',
                                  'A comment',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'crude', 'The Location', 'A Reference',
                                  '01011970',
                                  'A long comment'
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, product_type, location,
                           reference, reference_date, comments):
        # We won't probably hit all the optional attributes,
        # just the ones with special constraints.
        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             product_type=product_type,
                             location=location,
                             reference=reference,
                             reference_date=reference_date,
                             comments=comments)

        assert obj.product_type == str(product_type)
        assert obj.location == str(location)
        assert obj.reference == str(reference)
        assert obj.reference_date == str(reference_date)
        assert obj.comments == str(comments)

    def test_init_synonyms(self):
        synonyms = ('Syn1', 'Syn2', 'Syn3')

        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             synonyms=[{'name': nm}
                                       for nm in synonyms])

        for i, nm in enumerate(synonyms):
            assert obj.synonyms[i].name == nm

    def test_init_densities(self):
        densities = [{'kg_m_3': v, 'ref_temp_k': t}
                     for v, t in zip((1000.0, 900.0, 800.0),
                                     (273.15, 288.15, 303.15))]

        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             densities=densities)

        for i, d in enumerate(densities):
            assert obj.densities[i].kg_m_3 == d['kg_m_3']
            assert obj.densities[i].ref_temp_k == d['ref_temp_k']
            assert obj.densities[i].weathering == 0.0

    def test_init_dvis(self):
        dvis = [{'kg_ms': v, 'ref_temp_k': t}
                for v, t in zip((1000.0, 900.0, 800.0),
                                (273.15, 288.15, 303.15))]

        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             dvis=dvis)

        for i, d in enumerate(dvis):
            assert obj.dvis[i].kg_ms == d['kg_ms']
            assert obj.dvis[i].ref_temp_k == d['ref_temp_k']
            assert obj.dvis[i].weathering == 0.0
            assert obj.dvis[i].replicates is None
            assert obj.dvis[i].standard_deviation is None
            assert obj.dvis[i].method is None

    def test_init_kvis(self):
        kvis = [{'m_2_s': v, 'ref_temp_k': t}
                for v, t in zip((1000.0, 900.0, 800.0),
                                (273.15, 288.15, 303.15))]

        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             kvis=kvis)

        for i, k in enumerate(kvis):
            assert obj.kvis[i].m_2_s == k['m_2_s']
            assert obj.kvis[i].ref_temp_k == k['ref_temp_k']
            assert obj.kvis[i].weathering == 0.0

    def test_init_cuts(self):
        cuts = [{'fraction': v, 'vapor_temp_k': t}
                for v, t in zip((0.1, 0.2, 0.3),
                                (273.15, 288.15, 303.15))]

        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             cuts=cuts)

        for i, c in enumerate(cuts):
            assert obj.cuts[i].fraction == c['fraction']
            assert obj.cuts[i].vapor_temp_k == c['vapor_temp_k']
            assert obj.cuts[i].liquid_temp_k is None
            assert obj.cuts[i].weathering == 0.0

    def test_init_toxicities(self):
        toxicities = [{'tox_type': v, 'species': t}
                      for v, t in zip(('EC', 'LC', 'EC', 'LC'),
                                      ('Species1', 'Species1',
                                       'Species2', 'Species2'))]

        obj = ImportedRecord(oil_id='AD00001', oil_name='Oil Name',
                             field_name='Field Name',
                             toxicities=toxicities)

        for i, t in enumerate(toxicities):
            assert obj.toxicities[i].tox_type == t['tox_type']
            assert obj.toxicities[i].species == t['species']
            assert obj.toxicities[i].after_24h is None
            assert obj.toxicities[i].after_48h is None
            assert obj.toxicities[i].after_96h is None








