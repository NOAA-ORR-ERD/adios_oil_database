'''
    Test our Environment Canada Imported Record model class
'''
from datetime import datetime, timezone

import pytest

from pydantic import ValidationError

from oil_database.models.ec_imported_rec import ECImportedRecord


class TestECImportedRecord():
    @pytest.mark.parametrize('oil_id, name',
                             [
                              ('EC000001', 'Oil Name'),
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 'Oil Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'EC000001', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'EC345678901234567', 'Oil Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'EC000001',
                                  'Long Oil Name'
                                  '123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 ',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_required(self, oil_id, name):
        if oil_id is None and name is None:
            obj = ECImportedRecord()
        elif name is None:
            obj = ECImportedRecord(oil_id=oil_id)
        elif oil_id is None:
            obj = ECImportedRecord(name=name)
        else:
            obj = ECImportedRecord(oil_id=oil_id, name=name)

        assert obj.oil_id == str(oil_id)
        assert obj.name == str(name)

    def test_init_defaults(self):
        # everything has a default
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name')

        assert obj.location is None
        assert obj.reference is None
        assert obj.reference_date is None
        assert obj.sample_date is None
        assert obj.comments is None
        assert obj.product_type is None

    @pytest.mark.parametrize('location, reference, comments',
                             [
                              ('Location', 'Reference', 'Comments'),
                              pytest.param(
                                  'Location'
                                  '123456789 123456789 123456789 '
                                  '123456789 123456789 123456789 ',
                                  'Reference', 'Comments',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Location',
                                  'Reference'
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
                                  'Comments',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'Location', 'Reference',
                                  'Comments'
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
    def test_init_optional(self, location, reference, comments):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               location=location,
                               reference=reference,
                               comments=comments)

        assert obj.location == str(location)
        assert obj.reference == str(reference)
        assert obj.comments == str(comments)

    @pytest.mark.parametrize('reference_date, sample_date',
                             [
                              (0, 0),
                              ('0', '0'),
                              ('1970-01-01T00:00:00', '1970-01-01T00:00:00'),
                              ('1970-01-01 00:00:00', '1970-01-01 00:00:00'),
                              ('1970-01-01 00:00', '1970-01-01 00:00'),
                              pytest.param(
                                  '1970-01-01', '1970-01-01',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  '1970/01/01 00:00', '1970/01/01 00:00',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_datetimes(self, reference_date, sample_date):
        # it looks like the date parsing is limited to either a timestamp
        # or an ISO 8601 string
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               reference_date=reference_date,
                               sample_date=sample_date)

        try:
            int(reference_date)
            assert obj.reference_date == datetime.fromtimestamp(int(reference_date),
                                                                tz=timezone.utc)
        except Exception:
            print((obj.reference_date,))
            print((datetime.fromisoformat(reference_date),))

            assert obj.reference_date == datetime.fromisoformat(reference_date)

        try:
            int(sample_date)
            assert obj.sample_date == datetime.fromtimestamp(int(sample_date),
                                                             tz=timezone.utc)
        except Exception:
            assert obj.sample_date == datetime.fromisoformat(sample_date)

    @pytest.mark.parametrize('densities',
                             [
                              [{'g_ml': 1.0, 'ref_temp_c': 0.0}],
                              pytest.param(
                                  '1.0',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_densities(self, densities):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               densities=densities)

        assert obj.densities[0].g_ml == densities[0]['g_ml']
        assert obj.densities[0].ref_temp_c == densities[0]['ref_temp_c']

    @pytest.mark.parametrize('apis',
                             [
                              [{'gravity': 10.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_apis(self, apis):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               apis=apis)

        assert obj.apis[0].gravity == apis[0]['gravity']

    @pytest.mark.parametrize('dvis',
                             [
                              [{'mpa_s': {'value': 10.0, 'unit': 'mPa s'},
                                'ref_temp_c': 0.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_dvis(self, dvis):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               dvis=dvis)

        assert obj.dvis[0].mpa_s.value == dvis[0]['mpa_s']['value']
        assert obj.dvis[0].mpa_s.unit == dvis[0]['mpa_s']['unit']
        assert obj.dvis[0].ref_temp_c == dvis[0]['ref_temp_c']

    @pytest.mark.parametrize('ifts',
                             [
                              [{'dynes_cm': 10.0,
                                'ref_temp_c': 0.0,
                                'interface': 'water'}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ifts(self, ifts):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               ifts=ifts)

        assert obj.ifts[0].dynes_cm == ifts[0]['dynes_cm']
        assert obj.ifts[0].ref_temp_c == ifts[0]['ref_temp_c']
        assert obj.ifts[0].interface == ifts[0]['interface']

    @pytest.mark.parametrize('flash_points',
                             [
                              [{'ref_temp': {'value': 0.0, 'unit': 'C'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_flash_points(self, flash_points):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               flash_points=flash_points)

        assert obj.flash_points[0].ref_temp.value == flash_points[0]['ref_temp']['value']
        assert obj.flash_points[0].ref_temp.unit == flash_points[0]['ref_temp']['unit']

    @pytest.mark.parametrize('pour_points',
                             [
                              [{'ref_temp': {'value': 0.0, 'unit': 'C'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_pour_points(self, pour_points):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               pour_points=pour_points)

        assert obj.pour_points[0].ref_temp.value == pour_points[0]['ref_temp']['value']
        assert obj.pour_points[0].ref_temp.unit == pour_points[0]['ref_temp']['unit']

    @pytest.mark.parametrize('cuts',
                             [
                              [{'percent': 0.1, 'temp_c': 0.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_cuts(self, cuts):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               cuts=cuts)

        assert obj.cuts[0].percent == cuts[0]['percent']
        assert obj.cuts[0].temp_c == cuts[0]['temp_c']

    @pytest.mark.parametrize('adhesions',
                             [
                              [{'g_cm_2': 1.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_adhesions(self, adhesions):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               adhesions=adhesions)

        assert obj.adhesions[0].g_cm_2 == adhesions[0]['g_cm_2']

    @pytest.mark.parametrize('evaporation_eqs',
                             [
                              [{'a': 1.0, 'b': 2.0, 'c': 3.0,
                                'equation': '(A + BT) ln t'}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_evaporation_eqs(self, evaporation_eqs):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               evaporation_eqs=evaporation_eqs)

        assert obj.evaporation_eqs[0].a == evaporation_eqs[0]['a']
        assert obj.evaporation_eqs[0].b == evaporation_eqs[0]['b']
        assert obj.evaporation_eqs[0].c == evaporation_eqs[0]['c']
        assert obj.evaporation_eqs[0].equation == evaporation_eqs[0]['equation']

    @pytest.mark.parametrize('emulsions',
                             [
                              [{'water_content_percent': 10.0,
                                'ref_temp_c': 0.0,
                                'age_days': 7.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_emulsions(self, emulsions):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               emulsions=emulsions)

        assert obj.emulsions[0].water_content_percent == emulsions[0]['water_content_percent']
        assert obj.emulsions[0].ref_temp_c == emulsions[0]['ref_temp_c']
        assert obj.emulsions[0].age_days == emulsions[0]['age_days']

    @pytest.mark.parametrize('corexit',
                             [
                              [{'dispersant_effectiveness': {'value': 0.1, 'unit': '1'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_corexit(self, corexit):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               corexit=corexit)

        assert obj.corexit[0].dispersant_effectiveness.value == corexit[0]['dispersant_effectiveness']['value']
        assert obj.corexit[0].dispersant_effectiveness.unit == corexit[0]['dispersant_effectiveness']['unit']

    @pytest.mark.parametrize('sulfur',
                             [
                              [{'percent': 10.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_sulfur(self, sulfur):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               sulfur=sulfur)

        assert obj.sulfur[0].percent == sulfur[0]['percent']

    @pytest.mark.parametrize('water',
                             [
                              [{'percent': {'value': 10.0, 'unit': '%'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_water(self, water):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               water=water)

        assert obj.water[0].percent.value == water[0]['percent']['value']
        assert obj.water[0].percent.unit == water[0]['percent']['unit']

    @pytest.mark.parametrize('benzene',
                             [
                              [{'benzene_ug_g': 10.0,
                                'toluene_ug_g': 15.0,
                                'x2_ethyltoluene_ug_g': 20.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_benzene(self, benzene):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               benzene=benzene)

        assert obj.benzene[0].benzene_ug_g == benzene[0]['benzene_ug_g']
        assert obj.benzene[0].toluene_ug_g == benzene[0]['toluene_ug_g']
        assert obj.benzene[0].x2_ethyltoluene_ug_g == benzene[0]['x2_ethyltoluene_ug_g']

    @pytest.mark.parametrize('headspace',
                             [
                              [{'n_c5_mg_g': 5.0, 'n_c6_mg_g': 6.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_headspace(self, headspace):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               headspace=headspace)

        assert obj.headspace[0].n_c5_mg_g == headspace[0]['n_c5_mg_g']
        assert obj.headspace[0].n_c6_mg_g == headspace[0]['n_c6_mg_g']

    @pytest.mark.parametrize('chromatography',
                             [
                              [{'tph_mg_g': 10.0, 'tsh_mg_g': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_chromatography(self, chromatography):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               chromatography=chromatography)

        assert obj.chromatography[0].tph_mg_g == chromatography[0]['tph_mg_g']
        assert obj.chromatography[0].tsh_mg_g == chromatography[0]['tsh_mg_g']

    @pytest.mark.parametrize('ccme',
                             [
                              [{'f1_mg_g': 10.0, 'f2_mg_g': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ccme(self, ccme):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               ccme=ccme)

        assert obj.ccme[0].f1_mg_g == ccme[0]['f1_mg_g']
        assert obj.ccme[0].f2_mg_g == ccme[0]['f2_mg_g']

    @pytest.mark.parametrize('ccme_f1',
                             [
                              [{'n_c8_to_n_c10': 10.0,
                                'n_c10_to_n_c12': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ccme_f1(self, ccme_f1):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               ccme_f1=ccme_f1)

        assert obj.ccme_f1[0].n_c8_to_n_c10 == ccme_f1[0]['n_c8_to_n_c10']
        assert obj.ccme_f1[0].n_c10_to_n_c12 == ccme_f1[0]['n_c10_to_n_c12']

    @pytest.mark.parametrize('ccme_f2',
                             [
                              [{'n_c8_to_n_c10': 10.0,
                                'n_c10_to_n_c12': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ccme_f2(self, ccme_f2):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               ccme_f2=ccme_f2)

        assert obj.ccme_f2[0].n_c8_to_n_c10 == ccme_f2[0]['n_c8_to_n_c10']
        assert obj.ccme_f2[0].n_c10_to_n_c12 == ccme_f2[0]['n_c10_to_n_c12']

    @pytest.mark.parametrize('ccme_tph',
                             [
                              [{'n_c8_to_n_c10': 10.0,
                                'n_c10_to_n_c12': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ccme_tph(self, ccme_tph):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               ccme_tph=ccme_tph)

        assert obj.ccme_tph[0].n_c8_to_n_c10 == ccme_tph[0]['n_c8_to_n_c10']
        assert obj.ccme_tph[0].n_c10_to_n_c12 == ccme_tph[0]['n_c10_to_n_c12']

    @pytest.mark.parametrize('alkylated_pahs',
                             [
                              [{'c0_n_ug_g': 10.0,
                                'c1_n_ug_g': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_alkylated_pahs(self, alkylated_pahs):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               alkylated_pahs=alkylated_pahs)

        assert obj.alkylated_pahs[0].c0_n_ug_g == alkylated_pahs[0]['c0_n_ug_g']
        assert obj.alkylated_pahs[0].c1_n_ug_g == alkylated_pahs[0]['c1_n_ug_g']

    @pytest.mark.parametrize('biomarkers',
                             [
                              [{'x30_norhopane_ug_g': 10.0,
                                'hopane_ug_g': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_biomarkers(self, biomarkers):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               biomarkers=biomarkers)

        assert obj.biomarkers[0].x30_norhopane_ug_g == biomarkers[0]['x30_norhopane_ug_g']
        assert obj.biomarkers[0].hopane_ug_g == biomarkers[0]['hopane_ug_g']

    @pytest.mark.parametrize('wax_content',
                             [
                              [{'percent': 10.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_wax_content(self, wax_content):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               wax_content=wax_content)

        assert obj.wax_content[0].percent == wax_content[0]['percent']

    @pytest.mark.parametrize('alkanes',
                             [
                              [{'pristane_ug_g': 10.0,
                                'phytane_ug_g': 15.0,
                                'c8_ug_g': 20.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_alkanes(self, alkanes):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               alkanes=alkanes)

        assert obj.alkanes[0].pristane_ug_g == alkanes[0]['pristane_ug_g']
        assert obj.alkanes[0].phytane_ug_g == alkanes[0]['phytane_ug_g']
        assert obj.alkanes[0].c8_ug_g == alkanes[0]['c8_ug_g']

    @pytest.mark.parametrize('sara_total_fractions',
                             [
                              [{'sara_type': 'Saturates',
                                'percent': 10.0},
                               {'sara_type': 'Aromatics',
                                'percent': 15.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_sara_total_fractions(self, sara_total_fractions):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               sara_total_fractions=sara_total_fractions)

        assert obj.sara_total_fractions[0].sara_type == sara_total_fractions[0]['sara_type']
        assert obj.sara_total_fractions[0].percent == sara_total_fractions[0]['percent']

        assert obj.sara_total_fractions[1].sara_type == sara_total_fractions[1]['sara_type']
        assert obj.sara_total_fractions[1].percent == sara_total_fractions[1]['percent']

    @pytest.mark.parametrize('synonyms',
                             [
                              [{'name': 'Synonym1'},
                               {'name': 'Synonym2'}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_synonyms(self, synonyms):
        obj = ECImportedRecord(oil_id='EC000001', name='Oil Name',
                               synonyms=synonyms)

        assert obj.synonyms[0].name == synonyms[0]['name']
        assert obj.synonyms[1].name == synonyms[1]['name']














