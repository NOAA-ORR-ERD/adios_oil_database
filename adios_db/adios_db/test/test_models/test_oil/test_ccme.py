from pathlib import Path

from adios_db.models.common.measurement import MassFraction
from adios_db.models.oil.ccme import CCME


HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"


class TestCCME:
    def test_init_empty(self):
        ccme = CCME()

        for attr in ('F1', 'F2', 'F3', 'F4', 'method'):
            assert hasattr(ccme, attr)

    def test_json_empty(self):
        py_json = CCME().py_json()

        assert tuple(py_json.keys()) == ()  # sparse by default

    def test_json_empty_non_sparse(self):
        py_json = CCME().py_json(sparse=False)

        assert set(py_json.keys()) == {'F1', 'F2', 'F3', 'F4', 'method'}

    def test_with_ccme(self):
        """
        Generally we should keep our pytests small, testing one thing at a
        time.
        """
        ccme = CCME()

        ccme.F1 = MassFraction(unit="mg/g", value=15.58)
        ccme.F2 = MassFraction(unit="mg/g", value=50)
        ccme.F3 = MassFraction(unit="mg/g", value=193)
        ccme.F4 = MassFraction(unit="mg/g", value=40)

        py_json = ccme.py_json()

        # test the round trip
        ccme2 = CCME.from_py_json(py_json)

        assert ccme2 == ccme

    def test_full(self):
        """
        But hey, here we go with a full-on test of everything
        """
        ccme = CCME()

        ccme.F1 = MassFraction(unit="mg/g", value=15.58)
        ccme.F2 = MassFraction(unit="mg/g", value=50)
        ccme.F3 = MassFraction(unit="mg/g", value=193)
        ccme.F4 = MassFraction(unit="mg/g", value=40)
        ccme.method = "a method name"

        py_json = ccme.py_json()

        # dump the json:
        # json.dump(py_json, open(OUTPUT_DIR / "example_ccme.json", 'w'),
        #           indent=4)

        # test the round trip
        ccme2 = CCME.from_py_json(py_json)

        assert ccme2 == ccme
