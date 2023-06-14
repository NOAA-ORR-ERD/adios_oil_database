import pytest

from adios_db.models.common.measurement import MassFraction
from adios_db.models.oil.properties import (Dispersibility,
                                            DispersibilityList,
                                            EmulsionList)
from adios_db.models.oil.environmental_behavior import EnvironmentalBehavior


class TestPhysicalProperties:
    def test_init(self):
        s = EnvironmentalBehavior()

        for attr in ('dispersibilities', 'emulsions'):
            assert hasattr(s, attr)

        assert type(s.dispersibilities) == DispersibilityList
        assert type(s.emulsions) == EmulsionList

    def test_json(self):
        s = EnvironmentalBehavior()
        py_json = s.py_json()

        assert tuple(py_json.keys()) == ()  # sparse by default

    def test_json_non_sparse(self):
        s = EnvironmentalBehavior()
        py_json = s.py_json(sparse=False)

        assert set(py_json.keys()) == {'adhesion',
                                       'dispersibilities',
                                       'emulsions',
                                       'ests_evaporation_test'}

    def test_add_non_existing(self):
        s = EnvironmentalBehavior()

        with pytest.raises(AttributeError):
            s.something_random = 43

    def test_complete_sample(self):
        """
        trying to do a pretty complete one

        Note: This is more an integration test.  Each complex attribute of the
              EnvironmentalBehavior dataclass should have its own pytests
        """
        p = EnvironmentalBehavior()

        p.dispersibilities = DispersibilityList([
            Dispersibility(dispersant='corexit 9500',
                           method='ASTM F2059',
                           effectiveness=MassFraction(value=10.0, unit="%",
                                                      standard_deviation=1.2,
                                                      replicates=3)),
        ])

        py_json = p.py_json(sparse=False)  # the non-sparse version

        assert set(py_json.keys()) == {'adhesion',
                                       'dispersibilities',
                                       'emulsions',
                                       'ests_evaporation_test'}

        # Now test some real stuff:
        disp = py_json['dispersibilities']
        print(type(disp))

        assert type(disp) == list
        assert disp[0]['method'] == 'ASTM F2059'
        assert disp[0]['effectiveness']['value'] == 10.0
