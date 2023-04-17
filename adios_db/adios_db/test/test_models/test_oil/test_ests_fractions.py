from pathlib import Path
import json

from adios_db.models.common.measurement import MassFraction
from adios_db.models.oil.compound import Compound, CompoundList

from adios_db.models.oil.ests_fractions import ESTSFractions


HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"


class TestESTSFractions:
    def test_init_empty(self):
        ccme = ESTSFractions()

        for attr in ('saturates', 'aromatics', 'GC_TPH'):
            assert hasattr(ccme, attr)

    def test_json_empty(self):
        py_json = ESTSFractions().py_json()

        assert tuple(py_json.keys()) == ()  # sparse by default

    def test_json_empty_non_sparse(self):
        py_json = ESTSFractions().py_json(sparse=False)

        assert set(py_json.keys()) == {'saturates',
                                       'aromatics',
                                       'GC_TPH',
                                       'method'}

    def test_small(self):
        """
        Generally we should keep our pytests small, testing one thing at a
        time.
        """
        ccme = ESTSFractions()

        ccme.saturates = CompoundList([
            Compound(name="n-C8 to n-C10", method="ESTS 2002a",
                     measurement=MassFraction(value=18, unit='mg/g')),
            Compound(name="n-C10 to n-C12", method="ESTS 2002a",
                     measurement=MassFraction(value=11, unit='mg/g')),
        ])

        assert len(ccme.saturates) == 2

        ccme.aromatics.extend([
            Compound(name="n-C8 to n-C10", method="ESTS 2002a",
                     measurement=MassFraction(value=4, unit='mg/g')),
            Compound(name="n-C10 to n-C12", method="ESTS 2002a",
                     measurement=MassFraction(value=2, unit='mg/g')),
        ])

        assert len(ccme.saturates) == 2

        ccme.GC_TPH.extend([
            Compound(name="n-C8 to n-C10", method="ESTS 2002a",
                     measurement=MassFraction(value=15, unit='mg/g')),
            Compound(name="n-C10 to n-C12", method="ESTS 2002a",
                     measurement=MassFraction(value=14, unit='mg/g')),
        ])

        assert len(ccme.GC_TPH) == 2
        assert ccme.GC_TPH[1].measurement.value == 14.0

        py_json = ccme.py_json()

        # dump the json:
        json.dump(py_json,
                  open(OUTPUT_DIR / "example_ests_fraction.json", 'w',
                       encoding="utf-8"),
                  indent=4)

        # test the round trip
        ccme2 = ESTSFractions.from_py_json(py_json)

        assert ccme2 == ccme

    def test_full(self):
        """
        But hey, here we go with a full-on test of everything
        """
        ccme = ESTSFractions()

        ccme.saturates.extend([
            Compound(name="n-C8 to n-C10", method="ESTS 2002a",
                     measurement=MassFraction(value=18, unit='mg/g')),
            Compound(name="n-C10 to n-C12", method="ESTS 2002a",
                     measurement=MassFraction(value=11, unit='mg/g')),
            Compound(name="n-C12 to n-C16", method="ESTS 2002a",
                     measurement=MassFraction(value=30, unit='mg/g')),
            Compound(name="n-C16 to n-C20", method="ESTS 2002a",
                     measurement=MassFraction(value=31, unit='mg/g')),
            Compound(name="n-C20 to n-C24", method="ESTS 2002a",
                     measurement=MassFraction(value=22, unit='mg/g')),
            Compound(name="n-C24 to n-C28", method="ESTS 2002a",
                     measurement=MassFraction(value=16, unit='mg/g')),
            Compound(name="n-C28 to n-C34", method="ESTS 2002a",
                     measurement=MassFraction(value=22, unit='mg/g')),
            Compound(name="n-C34+", method="ESTS 2002a",
                     measurement=MassFraction(value=15, unit='mg/g')),
        ])

        assert len(ccme.saturates) == 8

        ccme.aromatics.extend([
            Compound(name="n-C8 to n-C10", method="ESTS 2002a",
                     measurement=MassFraction(value=4, unit='mg/g')),
            Compound(name="n-C10 to n-C12", method="ESTS 2002a",
                     measurement=MassFraction(value=2, unit='mg/g')),
            Compound(name="n-C12 to n-C16", method="ESTS 2002a",
                     measurement=MassFraction(value=6, unit='mg/g')),
            Compound(name="n-C16 to n-C20", method="ESTS 2002a",
                     measurement=MassFraction(value=17, unit='mg/g')),
            Compound(name="n-C20 to n-C24", method="ESTS 2002a",
                     measurement=MassFraction(value=23, unit='mg/g')),
            Compound(name="n-C24 to n-C28", method="ESTS 2002a",
                     measurement=MassFraction(value=23, unit='mg/g')),
            Compound(name="n-C28 to n-C34", method="ESTS 2002a",
                     measurement=MassFraction(value=33, unit='mg/g')),
            Compound(name="n-C34+", method="ESTS 2002a",
                     measurement=MassFraction(value=27, unit='mg/g')),
        ])

        assert len(ccme.saturates) == 8

        ccme.GC_TPH.extend([
            Compound(name="n-C8 to n-C10", method="ESTS 2002a",
                     measurement=MassFraction(value=15, unit='mg/g')),
            Compound(name="n-C10 to n-C12", method="ESTS 2002a",
                     measurement=MassFraction(value=14, unit='mg/g')),
            Compound(name="n-C12 to n-C16", method="ESTS 2002a",
                     measurement=MassFraction(value=38, unit='mg/g')),
            Compound(name="n-C16 to n-C20", method="ESTS 2002a",
                     measurement=MassFraction(value=48, unit='mg/g')),
            Compound(name="n-C20 to n-C24", method="ESTS 2002a",
                     measurement=MassFraction(value=45, unit='mg/g')),
            Compound(name="n-C24 to n-C28", method="ESTS 2002a",
                     measurement=MassFraction(value=40, unit='mg/g')),
            Compound(name="n-C28 to n-C34", method="ESTS 2002a",
                     measurement=MassFraction(value=58, unit='mg/g')),
            Compound(name="n-C34+", method="ESTS 2002a",
                     measurement=MassFraction(value=40, unit='mg/g')),
        ])

        assert len(ccme.GC_TPH) == 8
        assert ccme.GC_TPH[2].measurement.value == 38.0

        py_json = ccme.py_json()

        # test the round trip
        ccme2 = ESTSFractions.from_py_json(py_json)

        assert ccme2 == ccme
