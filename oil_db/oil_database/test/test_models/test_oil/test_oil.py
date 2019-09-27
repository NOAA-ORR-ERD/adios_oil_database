'''
    Test our main Oil Record model class
'''
from datetime import datetime, timezone

import pytest

from pydantic import ValidationError

from oil_database.models.oil import Oil


class TestOil():
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
            obj = Oil()
        elif name is None:
            obj = Oil(oil_id=oil_id)
        elif oil_id is None:
            obj = Oil(name=name)
        else:
            obj = Oil(oil_id=oil_id, name=name)

        assert obj.oil_id == str(oil_id)
        assert obj.name == str(name)

    def test_init_defaults(self):
        # everything has a default
        obj = Oil(oil_id='EC000001', name='Oil Name')

        assert obj.location is None
        assert obj.reference is None
        assert obj.reference_date is None
        assert obj.sample_date is None
        assert obj.comments is None
        assert obj.product_type is None

        assert obj.categories is None
        assert obj.status is None
        assert obj.synonyms is None
        assert obj.densities is None

        assert obj.apis is None
        assert obj.dvis is None
        assert obj.kvis is None
        assert obj.ifts is None

        assert obj.flash_points is None
        assert obj.pour_points is None

        assert obj.cuts is None

        assert obj.adhesions is None
        assert obj.evaporation_eqs is None
        assert obj.emulsions is None
        assert obj.chemical_dispersibility is None

        assert obj.sulfur is None
        assert obj.water is None
        assert obj.benzene is None
        assert obj.headspace is None
        assert obj.chromatography is None

        assert obj.ccme is None
        assert obj.ccme_f1 is None
        assert obj.ccme_f2 is None
        assert obj.ccme_tph is None

        assert obj.alkylated_pahs is None
        assert obj.biomarkers is None
        assert obj.wax_content is None
        assert obj.alkanes is None

        assert obj.sara_total_fractions is None
        assert obj.toxicities is None
        assert obj.conradson is None

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
        obj = Oil(oil_id='EC000001', name='Oil Name',
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
        obj = Oil(oil_id='EC000001', name='Oil Name',
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
                              [{'density': {'value': 1.0, 'unit': 'g/mL'},
                                'ref_temp': {'value': 0.0, 'unit': 'C'}}],
                              pytest.param(
                                  '1.0',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_densities(self, densities):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  densities=densities)

        assert obj.densities[0].density.value == densities[0]['density']['value']
        assert obj.densities[0].density.unit == densities[0]['density']['unit']

        assert obj.densities[0].ref_temp.value == densities[0]['ref_temp']['value']
        assert obj.densities[0].ref_temp.unit == densities[0]['ref_temp']['unit']

    @pytest.mark.parametrize('apis',
                             [
                              [{'gravity': 10.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_apis(self, apis):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  apis=apis)

        assert obj.apis[0].gravity == apis[0]['gravity']

    @pytest.mark.parametrize('dvis',
                             [
                              [{'viscosity': {'value': 10.0, 'unit': 'mPa s'},
                                'ref_temp': {'value': 0.0, 'unit': 'C'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_dvis(self, dvis):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  dvis=dvis)

        assert obj.dvis[0].viscosity.value == dvis[0]['viscosity']['value']
        assert obj.dvis[0].viscosity.unit == dvis[0]['viscosity']['unit']

        assert obj.dvis[0].ref_temp.value == dvis[0]['ref_temp']['value']
        assert obj.dvis[0].ref_temp.unit == dvis[0]['ref_temp']['unit']

    @pytest.mark.parametrize('ifts',
                             [
                              [{'tension': {'value': 10.0, 'unit': 'dyne/cm'},
                                'ref_temp': {'value': 0.0, 'unit': 'C'},
                                'interface': 'water'}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ifts(self, ifts):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  ifts=ifts)

        assert obj.ifts[0].tension.value == ifts[0]['tension']['value']
        assert obj.ifts[0].tension.unit == ifts[0]['tension']['unit']

        assert obj.ifts[0].ref_temp.value == ifts[0]['ref_temp']['value']
        assert obj.ifts[0].ref_temp.unit == ifts[0]['ref_temp']['unit']

        assert obj.ifts[0].interface == ifts[0]['interface']

    @pytest.mark.parametrize('flash_points',
                             [
                              [{'ref_temp': {'value': 0.0, 'unit': 'C'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_flash_points(self, flash_points):
        obj = Oil(oil_id='EC000001', name='Oil Name',
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
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  pour_points=pour_points)

        assert obj.pour_points[0].ref_temp.value == pour_points[0]['ref_temp']['value']
        assert obj.pour_points[0].ref_temp.unit == pour_points[0]['ref_temp']['unit']

    @pytest.mark.parametrize('cuts',
                             [
                              [{'fraction': {'value': 0.1, 'unit': '1'},
                                'vapor_temp': {'value': 0.0, 'unit': 'C'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_cuts(self, cuts):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  cuts=cuts)

        assert obj.cuts[0].fraction.value == cuts[0]['fraction']['value']
        assert obj.cuts[0].fraction.unit == cuts[0]['fraction']['unit']

        assert obj.cuts[0].vapor_temp.value == cuts[0]['vapor_temp']['value']
        assert obj.cuts[0].vapor_temp.unit == cuts[0]['vapor_temp']['unit']

    @pytest.mark.parametrize('adhesions',
                             [
                              [{'adhesion': {'value': 1.0, 'unit': 'g/cm^2'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_adhesions(self, adhesions):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  adhesions=adhesions)

        assert obj.adhesions[0].adhesion.value == adhesions[0]['adhesion']['value']
        assert obj.adhesions[0].adhesion.unit == adhesions[0]['adhesion']['unit']

    @pytest.mark.parametrize('evaporation_eqs',
                             [
                              [{'a': 1.0, 'b': 2.0, 'c': 3.0,
                                'equation': '(A + BT) ln t'}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_evaporation_eqs(self, evaporation_eqs):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  evaporation_eqs=evaporation_eqs)

        assert obj.evaporation_eqs[0].a == evaporation_eqs[0]['a']
        assert obj.evaporation_eqs[0].b == evaporation_eqs[0]['b']
        assert obj.evaporation_eqs[0].c == evaporation_eqs[0]['c']
        assert obj.evaporation_eqs[0].equation == evaporation_eqs[0]['equation']

    @pytest.mark.parametrize('emulsions',
                             [
                              [{'water_content': {'value': 10.0, 'unit': '%'},
                                'ref_temp': {'value': 0.0, 'unit': 'C'},
                                'age': {'value': 7.0, 'unit': 'days'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_emulsions(self, emulsions):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  emulsions=emulsions)

        assert obj.emulsions[0].water_content.value == emulsions[0]['water_content']['value']
        assert obj.emulsions[0].water_content.unit == emulsions[0]['water_content']['unit']

        assert obj.emulsions[0].ref_temp.value == emulsions[0]['ref_temp']['value']
        assert obj.emulsions[0].ref_temp.unit == emulsions[0]['ref_temp']['unit']

        assert obj.emulsions[0].age.value == emulsions[0]['age']['value']
        assert obj.emulsions[0].age.unit == emulsions[0]['age']['unit']

    @pytest.mark.parametrize('chemical_dispersibility',
                             [
                              [{'dispersant': 'Corexit 9500',
                                'effectiveness': {'value': 0.1, 'unit': '1'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_chemical_dispersibility(self, chemical_dispersibility):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  chemical_dispersibility=chemical_dispersibility)

        assert obj.chemical_dispersibility[0].dispersant == chemical_dispersibility[0]['dispersant']

        assert obj.chemical_dispersibility[0].effectiveness.value == chemical_dispersibility[0]['effectiveness']['value']
        assert obj.chemical_dispersibility[0].effectiveness.unit == chemical_dispersibility[0]['effectiveness']['unit']

    @pytest.mark.parametrize('sulfur',
                             [
                              [{'fraction': {'value': 0.1, 'unit': '1'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_sulfur(self, sulfur):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  sulfur=sulfur)

        assert obj.sulfur[0].fraction.value == sulfur[0]['fraction']['value']
        assert obj.sulfur[0].fraction.unit == sulfur[0]['fraction']['unit']

    @pytest.mark.parametrize('water',
                             [
                              [{'fraction': {'value': 10.0, 'unit': '%'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_water(self, water):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  water=water)

        assert obj.water[0].fraction.value == water[0]['fraction']['value']
        assert obj.water[0].fraction.unit == water[0]['fraction']['unit']

    @pytest.mark.parametrize('benzene',
                             [
                              [{'benzene': {'value': 10.0, 'unit': 'ug/g'},
                                'toluene': {'value': 15.0, 'unit': 'ug/g'},
                                'x2_ethyltoluene': {'value': 20.0,
                                                    'unit': 'ug/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_benzene(self, benzene):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  benzene=benzene)

        assert obj.benzene[0].benzene.value == benzene[0]['benzene']['value']
        assert obj.benzene[0].benzene.unit == benzene[0]['benzene']['unit']

        assert obj.benzene[0].toluene.value == benzene[0]['toluene']['value']
        assert obj.benzene[0].toluene.unit == benzene[0]['toluene']['unit']

        assert obj.benzene[0].x2_ethyltoluene.value == benzene[0]['x2_ethyltoluene']['value']
        assert obj.benzene[0].x2_ethyltoluene.unit == benzene[0]['x2_ethyltoluene']['unit']

    @pytest.mark.parametrize('headspace',
                             [
                              [{'n_c5': {'value': 5.0, 'unit': 'mg/g'},
                                'n_c6': {'value': 6.0, 'unit': 'mg/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_headspace(self, headspace):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  headspace=headspace)

        assert obj.headspace[0].n_c5.value == headspace[0]['n_c5']['value']
        assert obj.headspace[0].n_c5.unit == headspace[0]['n_c5']['unit']

        assert obj.headspace[0].n_c6.value == headspace[0]['n_c6']['value']
        assert obj.headspace[0].n_c6.unit == headspace[0]['n_c6']['unit']

    @pytest.mark.parametrize('chromatography',
                             [
                              [{'tph': {'value': 10.0, 'unit': 'mg/g'},
                                'tsh': {'value': 5.0, 'unit': 'mg/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_chromatography(self, chromatography):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  chromatography=chromatography)

        assert obj.chromatography[0].tph.value == chromatography[0]['tph']['value']
        assert obj.chromatography[0].tph.unit == chromatography[0]['tph']['unit']

        assert obj.chromatography[0].tsh.value == chromatography[0]['tsh']['value']
        assert obj.chromatography[0].tsh.unit == chromatography[0]['tsh']['unit']

    @pytest.mark.parametrize('ccme',
                             [
                              [{'f1': {'value': 10.0, 'unit': 'mg/g'},
                                'f2': {'value': 5.0, 'unit': 'mg/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ccme(self, ccme):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  ccme=ccme)

        assert obj.ccme[0].f1.value == ccme[0]['f1']['value']
        assert obj.ccme[0].f1.unit == ccme[0]['f1']['unit']

        assert obj.ccme[0].f2.value == ccme[0]['f2']['value']
        assert obj.ccme[0].f2.unit == ccme[0]['f2']['unit']

    @pytest.mark.parametrize('ccme_f1',
                             [
                              [{'n_c8_to_n_c10': 10.0,
                                'n_c10_to_n_c12': 5.0}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_ccme_f1(self, ccme_f1):
        obj = Oil(oil_id='EC000001', name='Oil Name',
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
        obj = Oil(oil_id='EC000001', name='Oil Name',
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
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  ccme_tph=ccme_tph)

        assert obj.ccme_tph[0].n_c8_to_n_c10 == ccme_tph[0]['n_c8_to_n_c10']
        assert obj.ccme_tph[0].n_c10_to_n_c12 == ccme_tph[0]['n_c10_to_n_c12']

    @pytest.mark.parametrize('alkylated_pahs',
                             [
                              [{'c0_n': {'value': 10.0, 'unit': 'ug/g'},
                                'c1_n': {'value': 5.0, 'unit': 'ug/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_alkylated_pahs(self, alkylated_pahs):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  alkylated_pahs=alkylated_pahs)

        assert obj.alkylated_pahs[0].c0_n.value == alkylated_pahs[0]['c0_n']['value']
        assert obj.alkylated_pahs[0].c0_n.unit == alkylated_pahs[0]['c0_n']['unit']

        assert obj.alkylated_pahs[0].c1_n.value == alkylated_pahs[0]['c1_n']['value']
        assert obj.alkylated_pahs[0].c1_n.unit == alkylated_pahs[0]['c1_n']['unit']

    @pytest.mark.parametrize('biomarkers',
                             [
                              [{'x30_norhopane': {'value': 10.0,
                                                  'unit': 'ug/g'},
                                'hopane': {'value': 5.0, 'unit': 'ug/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_biomarkers(self, biomarkers):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  biomarkers=biomarkers)

        assert obj.biomarkers[0].x30_norhopane.value == biomarkers[0]['x30_norhopane']['value']
        assert obj.biomarkers[0].x30_norhopane.unit == biomarkers[0]['x30_norhopane']['unit']

        assert obj.biomarkers[0].hopane.value == biomarkers[0]['hopane']['value']
        assert obj.biomarkers[0].hopane.unit == biomarkers[0]['hopane']['unit']

    @pytest.mark.parametrize('wax_content',
                             [
                              [{'fraction': {'value': 10.0, 'unit': '%'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_wax_content(self, wax_content):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  wax_content=wax_content)

        assert obj.wax_content[0].fraction.value == wax_content[0]['fraction']['value']
        assert obj.wax_content[0].fraction.unit == wax_content[0]['fraction']['unit']

    @pytest.mark.parametrize('alkanes',
                             [
                              [{'pristane': {'value': 10.0, 'unit': 'ug/g'},
                                'phytane': {'value': 15.0, 'unit': 'ug/g'},
                                'c8': {'value': 20.0, 'unit': 'ug/g'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_alkanes(self, alkanes):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  alkanes=alkanes)

        assert obj.alkanes[0].pristane.value == alkanes[0]['pristane']['value']
        assert obj.alkanes[0].pristane.value == alkanes[0]['pristane']['value']

        assert obj.alkanes[0].phytane.value == alkanes[0]['phytane']['value']
        assert obj.alkanes[0].phytane.value == alkanes[0]['phytane']['value']

        assert obj.alkanes[0].c8.value == alkanes[0]['c8']['value']
        assert obj.alkanes[0].c8.value == alkanes[0]['c8']['value']

    @pytest.mark.parametrize('sara_total_fractions',
                             [
                              [{'sara_type': 'Saturates',
                                'fraction': {'value': 10.0, 'unit': '%'}},
                               {'sara_type': 'Aromatics',
                                'fraction': {'value': 15.0, 'unit': '%'}}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_sara_total_fractions(self, sara_total_fractions):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  sara_total_fractions=sara_total_fractions)

        assert obj.sara_total_fractions[0].sara_type == sara_total_fractions[0]['sara_type']

        assert obj.sara_total_fractions[0].fraction.value == sara_total_fractions[0]['fraction']['value']
        assert obj.sara_total_fractions[0].fraction.unit == sara_total_fractions[0]['fraction']['unit']

        assert obj.sara_total_fractions[1].sara_type == sara_total_fractions[1]['sara_type']

        assert obj.sara_total_fractions[1].fraction.value == sara_total_fractions[1]['fraction']['value']
        assert obj.sara_total_fractions[1].fraction.unit == sara_total_fractions[1]['fraction']['unit']

    @pytest.mark.parametrize('synonyms',
                             [
                              [{'name': 'Synonym1'},
                               {'name': 'Synonym2'}],
                              pytest.param(
                                  ['10.0'],
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_synonyms(self, synonyms):
        obj = Oil(oil_id='EC000001', name='Oil Name',
                  synonyms=synonyms)

        assert obj.synonyms[0].name == synonyms[0]['name']
        assert obj.synonyms[1].name == synonyms[1]['name']
