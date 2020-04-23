# from math import isclose
import json

# import pytest

from oil_database.models.oil.measurement import MassFraction
from oil_database.models.oil.compound import Compound, CompoundList

from oil_database.models.oil.ccme import CCME

from pprint import pprint


class TestCCME:
    def test_init_empty(self):
        ccme = CCME()

        for attr in ('CCME_F1',
                     'CCME_F2',
                     'CCME_F3',
                     'CCME_F4',
                     'total_GC_TPH',
                     'saturates',
                     'aromatics',
                     'GC_TPH'):
            assert hasattr(ccme, attr)

    def test_json_empty(self):
        py_json = CCME().py_json()

        assert tuple(py_json.keys()) == ()  # sparse by default

    def test_json_empty_non_sparse(self):
        py_json = CCME().py_json(sparse=False)

        assert set(py_json.keys()) == {'CCME_F1',
                                       'CCME_F2',
                                       'CCME_F3',
                                       'CCME_F4',
                                       'total_GC_TPH',
                                       'saturates',
                                       'aromatics',
                                       'GC_TPH'}

    def test_small(self):
        '''
            Generally we should keep our pytests small, testing one thing at a
            time.
        '''
        ccme = CCME()

        ccme.CCME_F1 = MassFraction(unit="mg/g", value=15.58)
        ccme.CCME_F2 = MassFraction(unit="mg/g", value=50)
        ccme.CCME_F3 = MassFraction(unit="mg/g", value=193)
        ccme.CCME_F4 = MassFraction(unit="mg/g", value=40)
        ccme.total_GC_TPH = MassFraction(unit="mg/g", value=690)

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
        print("the pyjson form:")
        pprint(py_json)

        # # dump the json:
        # json.dump(py_json, open("example_ccme.json", 'w'), indent=4)

        # test the round trip
        ccme2 = CCME.from_py_json(py_json)

        assert ccme2 == ccme

    def test_full(self):
        '''
            But hey, here we go with a full-on test of everything
        '''
        ccme = CCME()

        ccme.CCME_F1 = MassFraction(unit="mg/g", value=15.58)
        ccme.CCME_F2 = MassFraction(unit="mg/g", value=50)
        ccme.CCME_F3 = MassFraction(unit="mg/g", value=193)
        ccme.CCME_F4 = MassFraction(unit="mg/g", value=40)
        ccme.total_GC_TPH = MassFraction(unit="mg/g", value=690)

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
        pprint(py_json)

        # dump the json:
        json.dump(py_json, open("example_ccme.json", 'w'), indent=4)

        # test the round trip
        ccme2 = CCME.from_py_json(py_json)

        assert ccme2 == ccme