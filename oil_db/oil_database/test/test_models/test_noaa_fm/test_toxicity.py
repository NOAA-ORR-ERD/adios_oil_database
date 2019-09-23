'''
    Test our NOAA Filemaker toxicity model class
'''
import pytest

from pydantic import ValidationError

from oil_database.models.noaa_fm import NoaaFmToxicity


class TestNoaaFmToxicity():
    @pytest.mark.parametrize('tox_type, species',
                             [
                              pytest.param(
                                  None, None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  None, 'Species',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'EC', None,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'bogus', 'Species',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  'EC', 'Some Really Long Species Name',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ('EC', 'Species'),
                              ])
    def test_init_required(self, tox_type, species):
        if tox_type is None and species is None:
            obj = NoaaFmToxicity()
        elif tox_type is None:
            obj = NoaaFmToxicity(species=species)
        elif species is None:
            obj = NoaaFmToxicity(tox_type=tox_type)
        else:
            obj = NoaaFmToxicity(tox_type=tox_type, species=species)

        assert obj.tox_type == str(tox_type)
        assert obj.species == str(species)

    def test_init_defaults(self):
        obj = NoaaFmToxicity(tox_type='EC', species='Species')

        assert obj.after_24h is None
        assert obj.after_48h is None
        assert obj.after_96h is None

    @pytest.mark.parametrize('after_24h, after_48h, after_96h',
                             [
                              (0.3, 0.2, 0.1),
                              ('0.3', '0.2', '0.1'),
                              pytest.param(
                                  'nope', 0.2, 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.3, 'nope', 0.1,
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              pytest.param(
                                  0.3, 0.2, 'nope',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init_optional(self, after_24h, after_48h, after_96h):
        obj = NoaaFmToxicity(tox_type='EC', species='Species',
                             after_24h=after_24h,
                             after_48h=after_48h,
                             after_96h=after_96h)

        assert obj.after_24h == float(after_24h)
        assert obj.after_48h == float(after_48h)
        assert obj.after_96h == float(after_96h)
