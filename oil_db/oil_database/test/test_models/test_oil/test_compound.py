# from math import isclose

# import pytest

from pprint import pprint

from oil_database.models.oil.compound import (Compound,
                                              CompoundList,
                                              )

from oil_database.models.oil.measurement import MassFraction

# Example:

EXAMPLE = {"name": "1-Methyl-2-Isopropylbenzene",
           "groups": ["C4-C6 Alkyl Benzenes", ...],
           "method": "ESTS 2002b",
           "measurement": {"value": 3.4,
                           "unit": "ppm",
                           "replicates": 3,
                           "standard_deviation": 0.1
                           }
           }

Comp1 = Compound(name="1-Methyl-2-Isopropylbenzene",
                 groups=["C4-C6 Alkyl Benzenes", "Aromatics"],
                 method="ESTS 2002b",
                 measurement=MassFraction(value=3.4,
                                          unit="ppm",
                                          replicates=3,
                                          standard_deviation=0.1
                                          )
                 )

Comp2 = Compound(name="4-Ethyl Death-benzene",
                 groups=["C6-C64 Alkyl Benzenes", "Saturated"],
                 method="ANSI random number",
                 measurement=MassFraction(value=2.1,
                                          unit="g/kg",
                                          replicates=5,
                                          standard_deviation=0.2
                                          )
                 )


def test_CompoundBasic():
    comp = Compound(name="1-Methyl-2-Isopropylbenzene",
                    groups=["C4-C6 Alkyl Benzenes", "Aromatics"],
                    method="ESTS 2002b",
                    measurement=MassFraction(value=3.4,
                                             unit="ppm",
                                             replicates=3,
                                             standard_deviation=0.1
                                             )
                    )

    assert comp.name == "1-Methyl-2-Isopropylbenzene"
    assert len(comp.groups) == 2
    assert comp.measurement.value == 3.4
    assert comp.measurement.unit_type == "massfraction"


def test_Compound_from_json():
    comp = Compound.from_py_json(EXAMPLE)

    assert comp.name == "1-Methyl-2-Isopropylbenzene"
    assert len(comp.groups) == 2
    assert comp.measurement.value == 3.4
    assert comp.measurement.unit_type == "massfraction"


def test_CompoundList_basic():
    c_list = CompoundList([Comp1, Comp2]
                          )

    assert len(c_list) == 2
    assert c_list[0] == Comp1
    assert c_list[1] == Comp2


def test_CompoundList_to_json():
    c_list = CompoundList([Comp1, Comp2]
                          )

    py_json = c_list.py_json()

    pprint(py_json)

    # looks OK, so jsut a couple wuick sanity checks
    assert py_json[0]['name'] == Comp1.name
    assert py_json[0]['groups'] == Comp1.groups
    assert py_json[0]['measurement']['value'] == Comp1.measurement.value

    assert py_json[1]['name'] == Comp2.name
    assert py_json[1]['groups'] == Comp2.groups
    assert py_json[1]['measurement']['value'] == Comp2.measurement.value


def test_Comopund_round_trip():
    c_list = CompoundList([Comp1, Comp2]
                          )

    py_json = c_list.py_json()

    c_list2 = CompoundList.from_py_json(py_json)

    assert c_list2 == c_list


def test_Compound_sparse():
    comp = Compound(name="n-C12 to n-C16",
                    method="ESTS 2002a",
                    measurement=MassFraction(value=38,
                                             unit='mg/g'),
                    )

    assert comp.groups == []
    py_json = comp.py_json()

    pprint(py_json)
    assert py_json['method'] == "ESTS 2002a"
    assert 'groups' not in py_json




