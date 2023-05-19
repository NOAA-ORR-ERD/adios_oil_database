from adios_db.models.common.measurement import MassFraction
from adios_db.models.oil.compound import Compound, CompoundList


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
                                          standard_deviation=0.1))

Comp2 = Compound(name="4-Ethyl Death-benzene",
                 groups=["C6-C64 Alkyl Benzenes", "Saturated"],
                 method="ANSI random number",
                 measurement=MassFraction(value=2.1,
                                          unit="g/kg",
                                          replicates=5,
                                          standard_deviation=0.2))


class TestCompound:
    def test_init(self):
        comp = Compound()

        assert comp.name == ''
        assert comp.method == ''
        assert comp.groups == []
        assert comp.measurement is None

    def test_init_full(self):
        comp = Compound(name="1-Methyl-2-Isopropylbenzene",
                        groups=["C4-C6 Alkyl Benzenes", "Aromatics"],
                        method="ESTS 2002b",
                        measurement=MassFraction(value=3.4,
                                                 unit="ppm",
                                                 replicates=3,
                                                 standard_deviation=0.1))

        assert comp.name == "1-Methyl-2-Isopropylbenzene"
        assert len(comp.groups) == 2
        assert comp.measurement.value == 3.4
        assert comp.measurement.unit_type == "massfraction"

    def test_py_json_empty(self):
        py_json = Compound().py_json()

        assert py_json == {}

    def test_py_json_empty_non_sparse(self):
        py_json = Compound().py_json(sparse=False)

        assert py_json == {'name': '',
                           'method': '',
                           'groups': [],
                           'measurement': None,
                           'comment': ''}

    def test_py_json(self):
        comp = Compound(name="n-C12 to n-C16",
                        method="ESTS 2002a",
                        measurement=MassFraction(value=38, unit='mg/g'))
        py_json = comp.py_json()

        assert py_json['method'] == "ESTS 2002a"
        assert 'groups' not in py_json

    def test_from_py_json(self):
        comp = Compound.from_py_json(EXAMPLE)

        assert comp.name == "1-Methyl-2-Isopropylbenzene"
        assert len(comp.groups) == 2
        assert comp.measurement.value == 3.4
        assert comp.measurement.unit_type == "massfraction"


class TestCompoundList:
    def test_basic(self):
        c_list = CompoundList([Comp1, Comp2])

        assert len(c_list) == 2
        assert c_list[0] == Comp1
        assert c_list[1] == Comp2

    def test_to_json(self):
        c_list = CompoundList([Comp1, Comp2])
        py_json = c_list.py_json()

        # looks OK, so just a couple quick sanity checks
        for c, j in zip((Comp1, Comp2), py_json):
            assert j['name'] == c.name
            assert j['groups'] == c.groups
            assert j['measurement']['value'] == c.measurement.value

    def test_round_trip(self):
        c_list = CompoundList([Comp1, Comp2])
        py_json = c_list.py_json()

        c_list2 = CompoundList.from_py_json(py_json)

        assert c_list == c_list2
