import pytest

from adios_db.models.common.measurement import MassFraction
from adios_db.models.oil.sara import Sara


class TestSARA:
    def test_init(self):
        s = Sara()

        for attr in ('method',
                     'saturates',
                     'aromatics',
                     'resins',
                     'asphaltenes'):
            assert hasattr(s, attr)
            assert getattr(s, attr) is None

    def test_json(self):
        s = Sara()
        py_json = s.py_json()

        assert tuple(py_json.keys()) == ()  # sparse by default

    def test_json_non_sparse(self):
        s = Sara()
        py_json = s.py_json(sparse=False)

        assert set(py_json.keys()) == {'method',
                                       'saturates',
                                       'aromatics',
                                       'resins',
                                       'asphaltenes'}

    def test_add_non_existing(self):
        s = Sara()

        with pytest.raises(AttributeError):
            s.something_random = 43

    def test_complete(self):
        """
        trying to do a pretty complete one

        Note: This is more an integration test.  Each complex attribute of the
              Sara dataclass should have its own pytests
        """
        s = Sara()

        s.saturates = MassFraction(value=10.0,
                                   unit="%",
                                   standard_deviation=1.2,
                                   replicates=3)

        py_json = s.py_json(sparse=False)  # the non-sparse version

        assert set(py_json.keys()) == {'method',
                                       'saturates',
                                       'aromatics',
                                       'resins',
                                       'asphaltenes'}

        # Now test some real stuff:
        sat = py_json['saturates']
        print(type(sat))

        assert type(sat) == dict
        assert sat['value'] == 10.0
