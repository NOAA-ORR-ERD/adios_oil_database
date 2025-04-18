import math
import json
from dataclasses import dataclass

import pytest

import nucos

from adios_db.models.common.utilities import dataclass_to_json
from adios_db.models.common.measurement import (MeasurementBase,
                                                Temperature,
                                                Length,
                                                Mass,
                                                Concentration,
                                                MassFraction,
                                                VolumeFraction,
                                                MassOrVolumeFraction,
                                                Density,
                                                DynamicViscosity,
                                                KinematicViscosity,
                                                Pressure,
                                                NeedleAdhesion,
                                                InterfacialTension,
                                                Unitless,
                                                AnyUnit)


def test_str():
    """
    testing the str() -- only one example, but it's something

    It should only provide the non-None fields

    NOTE: this is now in the base decorator
    """
    mass = Mass(value=2.3, unit='kg', standard_deviation=0.2, replicates=6)
    s = str(mass)

    print(repr(mass))

    assert s == ("Mass(value=2.3, unit='kg', standard_deviation=0.2, "
                 "replicates=6, unit_type='mass')")


def test_empty_py_json():
    """
    test that a measurement with no values has an empty dict as py_json
    """
    # arbitrary example
    length = Length()

    assert length.value is None
    assert length.min_value is None

    pj = length.py_json(sparse=True)

    assert pj == {}


def test_empty_measurement_not_saved_in_json():
    @dataclass_to_json
    @dataclass
    class JustMeasurement:
        length: Length = None

    jm = JustMeasurement(length=Length())
    print(jm)

    pj = jm.py_json(sparse=False)
    print(pj)

    assert pj['length']

    pj = jm.py_json(sparse=True)
    print(pj)

    assert pj == {}


def test_ensure_float():
    """
    values should all be always float type
    """
    mass = Mass(min_value=10, max_value=20, unit='kg',
                standard_deviation=3, replicates=6)

    assert isinstance(mass.min_value, float)
    assert isinstance(mass.max_value, float)
    assert isinstance(mass.standard_deviation, float)


def test_ensure_float_from_json():
    """
    values should all be always float type

    this is testing from JSON, and also string values -- why not?
    """
    JSON = """{"value": 10,
               "unit": "kg",
               "standard_deviation": 3.1,
               "replicates": "6",
               "unit_type": "mass"
               }
            """
    mass = Mass.from_py_json(json.loads(JSON))

    assert isinstance(mass.value, float)
    assert isinstance(mass.standard_deviation, float)

def test_meas_is_empty():
    # create and empty one
    m = Length()
    assert m.is_empty()


@pytest.mark.parametrize('kwargs', [{"value": 3.2},
                                    {"min_value": 3.2},
                                    {"max_value": 3.2},
                                    ])
def test_meas_not_is_empty(kwargs):
    m = Length(**kwargs)

    print(m)
    assert not m.is_empty()


def test_meas_no_value():
    # no value even if other stuff is set.
    m = Length(standard_deviation=3.1, replicates=3)

    print(m)
    assert m.no_value()


@pytest.mark.parametrize('kwargs', [{"value": 3.2},
                                    {"min_value": 3.2},
                                    {"max_value": 3.2},
                                    ])
def test_meas_not_no_value(kwargs):
    m = Length(**kwargs)

    print(m)
    assert not m.no_value()

@pytest.mark.parametrize("meas, is_empty",[(Mass(value=5), False),
                                           (Mass(min_value=5), False),
                                           (Mass(max_value=5), False),
                                           (Mass(), True),
                                           (Mass(unit='kg'), True),
                                        ])
def test_is_empty(meas, is_empty):
    """
    An empty measurement is one with no values.
    It will have a unit type
    It might have a unit
    """
    print(meas)
    assert meas.is_empty() is is_empty

@pytest.mark.parametrize("meas, just_value",[(Mass(value=5), True),
                                             (Mass(min_value=5), False),
                                             (Mass(max_value=5), False),
                                             (Mass(), False),
                                             (Mass(value=5, min_value=3, unit='kg'), False),
                                             (Mass(value=5, max_value=7, unit='kg'), False),
                                             (Mass(min_value=3, max_value=5, unit='kg'), False),
                                             ])
def test_just_value(meas, just_value):
    """
    An empty measurement is one with no values.
    It will have a unit type
    It might have a unit
    """
    print(meas)
    assert meas.just_value() is just_value


class TestUnitless:
    def test_init_empty(self):
        model = Unitless()
        py_json = model.py_json()

        # should be empty
        assert py_json == {}

        # non-sparse should have all attributes present with None values
        py_json = model.py_json(sparse=False)

        assert py_json['unit_type'] == 'unitless'

        for attr in ('value',
                     'unit',
                     'min_value',
                     'max_value',
                     'standard_deviation',
                     'replicates'):
            assert py_json[attr] is None

    def test_value(self):
        model = Unitless(value=0.123)

        assert model.value == 0.123
        assert model.min_value is None
        assert model.max_value is None
        assert model.unit is None

        assert model.standard_deviation is None
        assert model.replicates is None

    def test_min_max(self):
        model = Unitless(min_value=0.1, max_value=0.2)

        assert model.value is None
        assert model.min_value == 0.1
        assert model.max_value == 0.2
        assert model.unit is None

        assert model.standard_deviation is None
        assert model.replicates is None

    def test_py_json(self):
        model = Unitless(value=1.1, standard_deviation=0.5, replicates=5)
        py_json = model.py_json()

        print(py_json)

        assert len(py_json) == 4  # (no unit field)
        assert 'unit' not in py_json

        assert py_json['value'] == 1.1
        assert py_json['unit_type'] == 'unitless'

        assert py_json['standard_deviation'] == 0.5
        assert py_json['replicates'] == 5

    def test_from_py_json(self):
        model = Unitless.from_py_json({
            'value': 1.1,
            'standard_deviation': 1.2,
            'replicates': 3
        })

        assert model.value == 1.1
        assert model.min_value is None
        assert model.max_value is None
        assert model.unit is None
        assert model.unit_type == 'unitless'

        assert model.standard_deviation == 1.2
        assert model.replicates == 3

    def test_convert_to(self):
        model = Unitless(value=12.34)

        with pytest.raises(TypeError):
            model.convert_to('C')

    def test_converted_to(self):
        model = Unitless(value=12.34)

        with pytest.raises(TypeError):
            model.converted_to('C')


class TestAnyUnit:
    def test_init_empty(self):
        with pytest.raises(TypeError):
            _model = AnyUnit()

    def test_init_just_unit_type(self):
        model = AnyUnit(unit_type='MassFraction')

        py_json = model.py_json()
        assert py_json == {}

        # non-sparse should have all attributes present with None values
        py_json = model.py_json(sparse=False)

        assert py_json['unit_type'] == 'massfraction'

        for attr in ('value', 'min_value', 'max_value', 'unit',
                     'standard_deviation', 'replicates'):
            assert py_json[attr] is None

    def test_convert_to(self):
        model = AnyUnit(value=273.15, unit='K', unit_type='temperature')
        model.convert_to('C')

        assert model.value == 0.0
        assert model.unit == 'C'

    def test_converted_to(self):
        model = AnyUnit(value=273.15, unit='K', unit_type='temperature')
        new = model.converted_to('C')

        assert model is not new

        assert model.value == 273.15
        assert model.unit == 'K'

        assert new.value == 0.0
        assert new.unit == 'C'


class TestMeasurementBase:
    """
    Fixme: is there any way to raise a NotImplementedError here?  We don't
          really want to use this class, just the subclasses.
    """
    def test_init(self):
        with pytest.raises(NotImplementedError):
            _model = MeasurementBase()


class TestTemperature:
    """
    Fixme: We really need to enforce that *some* value is passed in
           The model should fail if there is no value at all
    """
    def test_init_empty(self):
        model = Temperature()
        py_json = model.py_json()

        assert py_json == {}

        # non-sparse should have all attributes present with None values
        py_json = model.py_json(sparse=False)

        assert py_json['unit_type'] == 'temperature'

        for attr in ('value', 'min_value', 'max_value', 'unit',
                     'standard_deviation', 'replicates'):
            assert py_json[attr] is None

    def test_std_dev_replicates(self):
        """
        Note on validation: If there is a standard deviation, there should be
                            more than 1 replicate and if there is more than
                            one replicate, there should probably be a
                            non-zero standard deviation
        """
        model = Temperature(standard_deviation=1.2, replicates=3)

        assert model.value is None
        assert model.min_value is None
        assert model.max_value is None
        assert model.unit is None

        assert model.standard_deviation == 1.2
        assert model.replicates == 3

    def test_value(self):
        model = Temperature(value=273.15, unit="K")

        assert model.value == 273.15
        assert model.min_value is None
        assert model.max_value is None
        assert model.unit == 'K'

        assert model.standard_deviation is None
        assert model.replicates is None

    def test_min_max(self):
        model = Temperature(min_value=273.15, max_value=288.15, unit="K")

        assert model.value is None
        assert model.min_value == 273.15
        assert model.max_value == 288.15
        assert model.unit == 'K'

        assert model.standard_deviation is None
        assert model.replicates is None

    def test_py_json(self):
        model = Temperature(value=273.15, unit="K",
                            standard_deviation=1.2, replicates=3)
        py_json = model.py_json()

        assert len(py_json) == 5
        assert py_json['value'] == 273.15
        assert py_json['unit'] == 'K'
        assert py_json['unit_type'] == 'temperature'

        assert py_json['standard_deviation'] == 1.2
        assert py_json['replicates'] == 3

    def test_from_py_json(self):
        model = Temperature.from_py_json({
            'value': 273.15, 'unit': 'K',
            'standard_deviation': 1.2,
            'replicates': 3
        })

        assert model.value == 273.15
        assert model.min_value is None
        assert model.max_value is None
        assert model.unit == 'K'
        assert model.unit_type == 'temperature'

        assert model.standard_deviation == 1.2
        assert model.replicates == 3

    def test_convert_to(self):
        model = Temperature(value=273.15, unit='K')
        model.convert_to('C')

        assert model.value == 0.0
        assert model.unit == 'C'

    def test_converted_to(self):
        model = Temperature(value=273.15, unit='K')
        new = model.converted_to('C')

        assert model is not new

        assert model.value == 273.15
        assert model.unit == 'K'

        assert new.value == 0.0
        assert new.unit == 'C'

    @pytest.mark.parametrize("model", [
        Temperature(value=273, unit='K'),
        Temperature(value=15.15, unit='C'),
        Temperature(value=14.85, unit='C'),
        Temperature(value=-0.15, unit='C'),
        Temperature(value=-0.85, unit='C'),
    ])
    def test_validate_C_K_conversion_15(self, model):
        msgs = model.validate()
        print(msgs)

        assert "W010:" in msgs[0]

    @pytest.mark.parametrize("temp_obj, result", [
        (Temperature(value=273, unit='K'), 0.0),
        (Temperature(value=15.15, unit='C'), 15.0),
        (Temperature(value=14.85, unit='C'), 15.0),
        (Temperature(value=-0.15, unit='C'), 0.0),
        (Temperature(value=-0.85, unit='C'), -1.0),
    ])
    def test_fix_C_K(self, temp_obj, result):
        """
        check if we can auto-fix the C-K conversion
        """
        temp_obj.fix_C_K()

        assert temp_obj.unit == 'C'
        assert temp_obj.value == result

    @pytest.mark.parametrize("temp_obj", [
        (Temperature(value=273, unit='F')),
        (Temperature(min_value=15.15, max_value=60.0, unit='F')),
        (Temperature(value=60.15, unit='F')),
        (Temperature(value=0.16, unit='C')),
        (Temperature(value=-0.86, unit='C')),
    ])
    def test_fix_C_K_no_change(self, temp_obj):
        """
        if temps are not in C or K, there should be no change.
        """
        t1 = temp_obj.copy()
        temp_obj.fix_C_K()

        assert temp_obj == t1

    @pytest.mark.parametrize("t, unit, result", [(273, 'K', 0.0),
                                                 (15.15, 'C', 15.0),
                                                 (14.85, 'C', 15.0),
                                                 (-0.15, 'C', 0.0),
                                                 (-0.85, 'C', -1.0),
                                                 ])
    def test_patch_fix_C_K(self, monkeypatch, t, unit, result):
        temp_obj = Temperature(value=t, unit=unit)

        assert temp_obj.value == t

        # turn on fix
        print(f"{Temperature.fixCK=}")
        monkeypatch.setattr(Temperature, "fixCK", True)
        print(f"{Temperature.fixCK=}")

        temp_obj = Temperature(value=t, unit=unit)

        assert temp_obj.unit == 'C'
        assert temp_obj.value == result


class TestLength:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = Length()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = Length(value=1.0, unit='m')
        model.convert_to('cm')

        assert model.value == 100.0
        assert model.unit == 'cm'

    def test_with_unit_type(self):
        model = Length(value=1.0, unit='m', unit_type="length")
        model.convert_to('cm')

        assert model.value == 100.0
        assert model.unit == 'cm'

    def test_with_bad_unit_type(self):
        with pytest.raises(ValueError):
            _model = Length(value=1.0, unit='m', unit_type="mass")

    def test_from_py_json(self):
        model = Length(value=1.0, unit='m',
                       standard_deviation=0.01, replicates=3)
        py_json = model.py_json()

        model2 = Length.from_py_json(py_json)

        assert model == model2

    def test_from_py_json_bad_unit_type(self):
        py_json = {'value': 1.0, 'unit': 'm', 'unit_type': 'volume',
                   'standard_deviation': 0.01, 'replicates': 3}
        with pytest.raises(ValueError):
            _model = Length.from_py_json(py_json)


class TestMass:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = Mass()
        py_json = model.py_json()

        # should be empty dict
        assert py_json == {}

    def test_convert_to(self):
        model = Mass(value=1.0, unit='kg')
        model.convert_to('g')

        assert model.value == 1000.0
        assert model.unit == 'g'


class TestMassFraction:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = MassFraction()
        py_json = model.py_json()

        # should be empty dict
        assert py_json == {}

    def test_convert_to(self):
        model = MassFraction(value=1.0, unit='g/kg')
        model.convert_to('%')

        assert model.value == 0.1
        assert model.unit == '%'


class TestVolumeFraction:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = VolumeFraction()
        py_json = model.py_json()

        # should be empty dict
        assert py_json == {}

    def test_convert_to(self):
        model = VolumeFraction(value=1.0, unit='mL/L')
        model.convert_to('%')

        assert model.value == 0.1
        assert model.unit == '%'

    def test_convert_to_invalid(self):
        model = VolumeFraction(value=1.0, unit='mL/L')

        with pytest.raises(nucos.InvalidUnitError):
            model.convert_to('g/kg')

        assert model.value == 1.0
        assert model.unit == 'mL/L'


class TestMassOrVolumeFraction:
    """
    Could be Mass or Volume, depending on how it's initialized

    unit_type must be passed in when created.
    """
    def test_init_no_unit_type(self):
        """
        You shouldn't be able to initialize without specifying what
        type of fraction this is.
        """
        with pytest.raises(TypeError):
            _model = MassOrVolumeFraction()

    def test_init_bad_unit_type(self):
        """
        You shouldn't be able to initialize without specifying what
        type of fraction this is.
        """
        with pytest.raises(ValueError):
            _model = MassOrVolumeFraction(unit_type="mass")

    def test_init_empty_mass(self):
        model = MassOrVolumeFraction(unit_type='MassFraction')
        py_json = model.py_json()

        assert model.unit_type == 'massfraction'
        assert py_json == {}

    def test_init_empty_volume(self):
        model = MassOrVolumeFraction(unit_type="VolumeFraction")

        py_json = model.py_json()

        assert py_json == {}

    def test_init_empty_concentration(self):
        model = MassOrVolumeFraction(unit_type="Concentration")

        py_json = model.py_json()

        assert py_json == {}

    def test_init_full(self):
        model = MassOrVolumeFraction(value=0.001, unit_type="VolumeFraction",
                                     standard_deviation=0.0002, replicates=12)

        assert model.value == 0.001
        assert model.standard_deviation == 0.0002
        assert model.replicates == 12
        assert model.min_value is None
        assert model.max_value is None

    def test_convert_value_mass(self):
        model = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                     unit_type="MassFraction")
        model2 = model.converted_to('ppm')

        assert math.isclose(model2.value, 500)
        assert model2.unit_type == "massfraction"
        assert model2.unit == "ppm"

    def test_convert_value_volume(self):
        model = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                     unit_type="volumeFraction")
        model2 = model.converted_to('ppm')

        assert math.isclose(model2.value, 500)
        assert model2.unit_type == "volumefraction"
        assert model2.unit == "ppm"

    def test_convert_value_invalid(self):
        model = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                     unit_type="volumeFraction")

        with pytest.raises(nucos.InvalidUnitError):
            _model2 = model.converted_to('g/kg')

    def test_convert_conc_value_invalid(self):
        model = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                     unit_type="Concentration")

        with pytest.raises(nucos.InvalidUnitError):
            _model2 = model.converted_to('g/kg')

    def test_integer_value(self):
        """
        integer values should get auto-converted to floats
        """
        model = MassOrVolumeFraction(value=4, min_value=1, unit='fraction',
                                     unit_type="volumeFraction",
                                     standard_deviation=2)

        assert type(model.value) is float
        assert type(model.min_value) is float
        assert type(model.standard_deviation) is float

    def test_equal(self):
        model1 = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                      unit_type="MassFraction")
        model2 = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                      unit_type="MassFraction")

        assert model1 == model2

    def test_equal_except_unit_type(self):
        model1 = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                      unit_type="MassFraction")
        model2 = MassOrVolumeFraction(value=0.0005, unit='fraction',
                                      unit_type="VolumeFraction")

        assert model1 != model2

    def test_from_py_json_no_unit_type(self):
        py_json = {'value': 0.002, 'unit': 'ppm'}

        with pytest.raises(TypeError):
            _model = MassOrVolumeFraction.from_py_json(py_json)

    def test_from_py_json_volume(self):
        py_json = {'value': 0.002, 'unit': 'ppm',
                   'unit_type': 'volumefraction'}

        model = MassOrVolumeFraction.from_py_json(py_json)

        print(f"{py_json=}")
        print(f"{model.py_json()=}")
        assert model.py_json() == py_json


class TestConcentration:
    """
    Unit used for unknown whether it's volume of mass or ??
    """
    def test_init_empty(self):
        model = Concentration()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = Concentration(value=1.0, unit='fraction')
        model.convert_to('%')

        assert model.value == 100.0
        assert model.unit == '%'

    def test_convert_to_invalid(self):
        model = Concentration(value=50, unit='%')

        with pytest.raises(nucos.InvalidUnitError):
            model.convert_to('g/kg')

        assert model.value == 50
        assert model.unit == '%'


class TestDensity:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = Density()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = Density(value=1000.0, unit='kg/m^3')
        model.convert_to('g/cm^3')

        assert model.value == 1.0
        assert model.unit == 'g/cm^3'

    def test_convert_to_API(self):
        model = Density(value=900.0, unit='kg/m^3')
        model.convert_to('API')

        assert math.isclose(model.value, 25.57, rel_tol=1e-3)
        assert model.unit == 'API'


class TestDynamicViscosity:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = DynamicViscosity()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = DynamicViscosity(value=100.0, unit='cP')
        model.convert_to('P')

        assert model.value == 1.0
        assert model.unit == 'P'


class TestKinematicViscosity:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = KinematicViscosity()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = KinematicViscosity(value=100.0, unit='cSt')
        model.convert_to('St')

        assert model.value == 1.0
        assert model.unit == 'St'


class TestPressure:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = Pressure()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = Pressure(value=10.0, unit='Pa')
        model.convert_to('dyn/cm^2')

        assert math.isclose(model.value, 100.0, rel_tol=1e-05)
        assert model.unit == 'dyn/cm^2'


class TestNeedleAdhesion:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = NeedleAdhesion()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = NeedleAdhesion(value=10.0, unit='g/cm^2')

        with pytest.raises(ValueError):
            model.convert_to('kg/m^2')


class TestInterfacialTension:
    """
    All of our common Measurement subclasses share a common codebase.
    We will only test the things that are different, which haven't been
    tested yet.
    """
    def test_init_empty(self):
        model = InterfacialTension()
        py_json = model.py_json()

        assert py_json == {}

    def test_convert_to(self):
        model = InterfacialTension(value=1000.0, unit='dyne/cm')
        model.convert_to('N/m')

        assert model.value == 1.0
        assert model.unit == 'N/m'


@pytest.mark.skipif(not hasattr(nucos, 'is_supported_unit'),
                    reason='nucos too old for unit checking')
class TestUnitValidation:
    """
    Tests for the validation of units matching the unit_type
    """
    def test_good_unit(self):
        """
        a good unit shouldn't create any warnings or errors
        """
        length = Length(4, 'm')
        msgs = length.validate()

        assert not msgs

    def test_bad_unit(self):
        """
        an arbitrary bad unit
        """
        length = Length(4, 'sploit')
        msgs = length.validate()

        print(msgs)
        assert msgs
        assert "E045: Unit: 'sploit' is not a valid unit for unit type: 'length'" in msgs[0]

    def test_bad_unit_temp(self):
        """
        Temperature has another validator -- make sure it hasn't
        overridden this one
        """
        temp = Temperature(value=98.6, unit='Fred')
        msgs = temp.validate()

        assert msgs

    def test_unitless_good(self):
        meas = Unitless(value=1.2)
        msgs = meas.validate()

        assert not msgs

    def test_unitless_bad(self):
        meas = Unitless(value=1.2, unit='nothing')
        msgs = meas.validate()

        assert msgs[0] == 'E045: Unitless measurements should have no unit. "nothing" is not valid'

    def test_none_unit(self):
        """
        it's obviously an error if a unit is None, but it shouldn't crash
        """
        m = Length(value=3.0)

        # just to make sure
        assert m.unit is None

        msgs = m.validate()

        assert "E046: A unit must be specified for unit type: 'length'" in msgs

    def test_garbage_unit(self):
        """
        an unit can't be any non-string type
        """
        m = Length(value=3.0)

        # just to make sure
        m.unit = 1.0

        msgs = m.validate()

        assert "E045: Unit: '1.0' is not a valid unit for unit type: 'length'" in msgs[0]


def test_get_minimum_maximum_value():
    """
    with single value, you should get it as both minimum and maximum
    """
    m = Length(value=2.3, unit='meter')

    assert m.value == 2.3
    assert m.minimum == 2.3
    assert m.maximum == 2.3

def test_get_minimum_maximum_min_only():
    """
    with just a minimum, you should get only min
    """
    m = Length(min_value=2.3, unit='meter')

    assert m.value is None
    assert m.minimum == 2.3
    assert m.maximum is None


def test_get_minimum_maximum_max_only():
    """
    With max value, you should only max
    """
    m = Length(max_value=2.3, unit='meter')

    assert m.value is None
    assert m.minimum is None
    assert m.maximum == 2.3


def test_get_minimum_maximum_range():
    """
    With a range, you should get the min and max, but no value
    """
    m = Length(max_value=2.3, min_value=1.0, unit='meter')

    assert m.value is None
    assert m.minimum == 1.0
    assert m.maximum == 2.3


def test_validate_all_fields():
    """
    A measurement should never have all three values filled in.
    """
    m = Length(value=1, min_value=2, max_value=3, unit='m')

    print(m)

    val = m.validate()

    print(val)

    assert len(val) == 1
    assert val[0].startswith("E047:")


def test_as_text_value():
    m = MassFraction(value=0.3)
    text = m.as_text()

    assert text == "0.3"


def test_as_text_min():
    m = MassFraction(min_value=0.3)
    text = m.as_text()

    assert text == ">0.3"


def test_as_text_max():
    m = MassFraction(max_value=0.3)
    text = m.as_text()

    assert text == "<0.3"


def test_as_text_range():
    m = MassFraction(min_value=0.1, max_value=0.3)
    text = m.as_text()

    assert text == "0.1\N{Em Dash}0.3"

def test_validate_non_number_for_values_std():
    # NOTE: actual example from some bad data!
    dv = DynamicViscosity(value=2170.0,
                          unit="mPa.s",
                          standard_deviation="ESTS 12.05/1.0/M",
                          )

    msgs = dv.validate()
    assert "E044" in msgs[0]
    assert "standard_deviation" in msgs[0]

def test_validate_non_in_for_values_replicates():
    dv = KinematicViscosity(value=2170.0,
                            unit="cSt",
                            standard_deviation=132.2,
                            replicates=1.2,
                          )

    msgs = dv.validate()
    print(msgs)
    assert "E048" in msgs[0]
    assert "replicates" in msgs[0]
