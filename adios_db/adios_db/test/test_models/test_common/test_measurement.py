
import pytest
import math

import unit_conversion as uc

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
                                                Unitless)


# # Fixme: why is this in this test file ???
# class TestProductType:
#     @pytest.mark.parametrize("product_type", ('crude',
#                                               'refined',
#                                               'bitumen product',
#                                               'Refined',
#                                               'Bitumen Product',
#                                               'other'))
#     def test_validation(self, product_type):
#         pt = ProductType(product_type)

#         assert pt.validate() == []

#     @pytest.mark.parametrize("product_type", ('crud',
#                                               'rfined',
#                                               'bitumen',
#                                               'Reefined',
#                                               'Biitumen Product',
#                                               'random'))
#     def test_validation_invalid(self, product_type):
#         pt = ProductType(product_type)

#         result = pt.validate()
#         assert len(result) == 1
#         assert result[0].startswith("W003:")


def test_str():
    """
    testing the str() -- only one example, but it's something

    It should only provide the non-None fields

    NOTE: this is now in the base decorator
    """
    mass = Mass(value=2.3,
                unit='kg',
                standard_deviation=0.2,
                replicates=6
                )

    s = str(mass)

    print(repr(mass))

    assert s == "Mass(value=2.3, unit='kg', standard_deviation=0.2, replicates=6, unit_type='mass')"




class TestUnitless:
    def test_init_empty(self):
        model = Unitless()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'unitless'}

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
        model = Unitless(value=1.1,
                         standard_deviation=0.5,
                         replicates=5)
        py_json = model.py_json()

        print(py_json)

        assert len(py_json) == 4  # (no unit field)
        assert 'unit' not in py_json

        assert py_json['value'] == 1.1
        assert py_json['unit_type'] == 'unitless'

        assert py_json['standard_deviation'] == 0.5
        assert py_json['replicates'] == 5

    def test_from_py_json(self):
        model = Unitless.from_py_json({'value': 1.1,
                                       'standard_deviation': 1.2,
                                       'replicates': 3})

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


# keeping these, as the tests for initializing any empty one should maybe be adopted for Measurement
# class TestUnittedValue:
#     def test_init(self):
#         uv = UnittedValue(1.0, unit="m")

#         assert uv.value == 1.0
#         assert uv.unit == "m"

#     def test_init_no_value(self):
#         with pytest.raises(ValueError):
#             UnittedValue(1.0)
#         with pytest.raises(ValueError):
#             UnittedValue("m/s")

#     def test_from_py_json(self):
#         uv = UnittedValue.from_py_json({'value': 1.0, 'unit': 'm'})

#         assert uv.value == 1.0
#         assert uv.unit == "m"

#     def test_json(self):
#         uv = UnittedValue(1.0, unit="m")
#         py_json = uv.py_json()

#         print(py_json)

#         assert py_json == {'value': 1.0, 'unit': 'm'}

#     def test_from_py_json_missing_data(self):
#         '''
#             Not sure why we aren't raising an exception
#         '''
#         with pytest.raises(ValueError):
#             UnittedValue.from_py_json({'value': 1.0})

#         with pytest.raises(ValueError):
#             UnittedValue.from_py_json({'unit': 'm/s'})


# class TestUnittedRange:
#     def test_min_max(self):
#         ur = UnittedValue(None, 1.0, 5.0, "ft")

#         assert ur.min_value == 1.0
#         assert ur.max_value == 5.0
#         assert ur.unit == "ft"

#     def test_json_sparse(self):
#         ur = UnittedValue(max_value=5.0, unit='m')
#         py_json = ur.py_json()

#         assert py_json == {'max_value': 5.0, 'unit': 'm'}

#     def test_json_max_only(self):
#         ur = UnittedValue(max_value=5.0, unit='m')
#         py_json = ur.py_json(sparse=False)

#         assert py_json == {'value': None,
#                            'min_value': None,
#                            'max_value': 5.0,
#                            'unit': 'm'}

#     def test_from_json_min_only(self):
#         ur = UnittedValue.from_py_json({'min_value': 5.0,
#                                         'unit': 'm/s'})

#         assert ur.min_value == 5.0
#         assert ur.max_value is None
#         assert ur.unit == "m/s"

#     def test_from_json_min_max(self):
#         ur = UnittedRange.from_py_json({'min_value': 5.0,
#                                         'max_value': 10.1,
#                                         'unit': 'm/s'})

#         assert ur.min_value == 5.0
#         assert ur.max_value == 10.1
#         assert ur.unit == "m/s"


class TestMeasurementBase:
    '''
        Fixme: is there any way to raise a NotImplementedError here?  We don't
              really want to use this class, just the subclasses.
    '''
    def test_init(self):
        with pytest.raises(NotImplementedError):
            model = MeasurementBase()


class TestTemperature:
    '''
    Fixme: We really need to enforce that *some* value is passed in
           The model should fail if there is no value at all
    '''
    def test_init_empty(self):
        model = Temperature()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'temperature'}

        # non-sparse should have all attributes present with None values
        py_json = model.py_json(sparse=False)

        assert py_json['unit_type'] == 'temperature'
        for attr in ('value',
                     'unit',
                     'min_value',
                     'max_value',
                     'standard_deviation',
                     'replicates'):
            assert py_json[attr] is None

    def test_std_dev_replicates(self):
        # Note on validation: If there is a standard deviation, there should be
        #                     more than 1 replicate and if there is more than
        #                     one replicate, there should probably be a
        #                     non-zero standard deviation
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

        print(py_json)

        assert len(py_json) == 5
        assert py_json['value'] == 273.15
        assert py_json['unit'] == 'K'
        assert py_json['unit_type'] == 'temperature'

        assert py_json['standard_deviation'] == 1.2
        assert py_json['replicates'] == 3

    def test_from_py_json(self):
        model = Temperature.from_py_json({'value': 273.15, 'unit': 'K',
                                          'standard_deviation': 1.2,
                                          'replicates': 3})

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

    @pytest.mark.parametrize("model", [Temperature(value=273, unit='K'),
                                       Temperature(value=15.15, unit='C'),
                                       Temperature(value=14.85, unit='C'),
                                       Temperature(value=-0.15, unit='C'),
                                       Temperature(value=-0.85, unit='C'),
                                  ])
    def test_validate_C_K_conversion_15(self, model):
        #model = Temperature(value=273, unit='K')

        msgs = model.validate()

        print(msgs)

        assert "W010:" in msgs[0]

    @pytest.mark.parametrize("temp_obj, result", [(Temperature(value=273, unit='K'), 0.0),
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


#                  "name": "Butane and Lighter IBP - 60F",
# -                    "unit": "F",
# -                    "min_value": 151.46,
# -                    "max_value": 60.0,
# +                    "unit": "C",
# +                    "min_value": 66.36666666666667,
# +                    "max_value": 15.555555555555543,
#                      "unit_type": "temperature"
#                  }
#              },
    @pytest.mark.parametrize("temp_obj", [(Temperature(value=273, unit='F')),
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

        print(f"{Temperature.fixCK=}")

        # turn on fix
        monkeypatch.setattr(Temperature, "fixCK", True)

        print(f"{Temperature.fixCK=}")

        temp_obj = Temperature(value = t, unit=unit)

        assert temp_obj.unit == 'C'
        assert temp_obj.value == result



class TestLength:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = Length()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'length'}

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
            model = Length(value=1.0, unit='m', unit_type="mass")

    def test_from_py_json(self):
        model = Length(value=1.0,
                       unit='m',
                       standard_deviation=0.01,
                       replicates=3)
        print(model.py_json())

        pyson = model.py_json()

        model2 = Length.from_py_json(pyson)

        assert model == model2

    def test_from_py_json_bad_unit_type(self):
        pyson = {'value': 1.0,
                 'unit': 'm',
                 'standard_deviation': 0.01,
                 'replicates': 3,
                 'unit_type': 'volume'}
        with pytest.raises(ValueError):
            model = Length.from_py_json(pyson)




class TestMass:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = Mass()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'mass'}

    def test_convert_to(self):
        model = Mass(value=1.0, unit='kg')
        model.convert_to('g')

        assert model.value == 1000.0
        assert model.unit == 'g'


class TestMassFraction:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = MassFraction()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'massfraction'}

    def test_convert_to(self):
        model = MassFraction(value=1.0, unit='g/kg')
        model.convert_to('%')

        assert model.value == 0.1
        assert model.unit == '%'


class TestVolumeFraction:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = VolumeFraction()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'volumefraction'}

    def test_convert_to(self):
        model = VolumeFraction(value=1.0, unit='mL/L')
        model.convert_to('%')

        assert model.value == 0.1
        assert model.unit == '%'

    def test_convert_to_invalid(self):
        model = VolumeFraction(value=1.0, unit='mL/L')
        with pytest.raises(uc.InvalidUnitError):
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
            model = MassOrVolumeFraction()

    def test_init_bad_unit_type(self):
        """
        You shouldn't be able to initialize without specifying what
        type of fraction this is.
        """
        with pytest.raises(ValueError):
            model = MassOrVolumeFraction(unit_type="mass")

    def test_init_empty_mass(self):
        model = MassOrVolumeFraction(unit_type='MassFraction')

        py_json = model.py_json()

        assert model.unit_type == 'massfraction'

        # should only have a unit_type
        assert py_json == {'unit_type': 'massfraction'}

    def test_init_empty_volume(self):
        model = MassOrVolumeFraction(unit_type="VolumeFraction")

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'volumefraction'}

    def test_init_full(self):
        model = MassOrVolumeFraction(value=0.001,
                                     standard_deviation=0.0002,
                                     replicates=12,
                                     unit_type="VolumeFraction")

        assert model.value == 0.001
        assert model.standard_deviation == 0.0002
        assert model.replicates == 12
        assert model.min_value == None
        assert model.max_value == None


    def test_convert_value_mass(self):
        model = MassOrVolumeFraction(value=0.0005,
                                     unit='fraction',
                                     unit_type="MassFraction")

        model2 = model.converted_to('ppm')

        assert math.isclose(model2.value, 500)
        assert model2.unit_type == "massfraction"
        assert model2.unit == "ppm"

    def test_convert_value_volume(self):
        model = MassOrVolumeFraction(value=0.0005,
                                     unit='fraction',
                                     unit_type="volumeFraction")

        model2 = model.converted_to('ppm')

        assert math.isclose(model2.value, 500)
        assert model2.unit_type == "volumefraction"
        assert model2.unit == "ppm"

    def test_convert_value_invalid(self):
        model = MassOrVolumeFraction(value=0.0005,
                                     unit='fraction',
                                     unit_type="volumeFraction")

        with pytest.raises(uc.InvalidUnitError):
            model2 = model.converted_to('g/kg')


    def test_equal(self):
        model1 = MassOrVolumeFraction(value=0.0005,
                                      unit='fraction',
                                      unit_type="MassFraction")

        model2 = MassOrVolumeFraction(value=0.0005,
                                      unit='fraction',
                                      unit_type="MassFraction")

        assert model1 == model2

    def test_equal_except_unit_type(self):
        model1 = MassOrVolumeFraction(value=0.0005,
                                      unit='fraction',
                                      unit_type="MassFraction")

        model2 = MassOrVolumeFraction(value=0.0005,
                                      unit='fraction',
                                      unit_type="VolumeFraction")

        assert model1 != model2

    def test_from_py_json_no_unit_type(self):
        pyson = {'value': 0.002,
                 'unit': 'ppm'}

        with pytest.raises(TypeError):
            model = MassOrVolumeFraction.from_py_json(pyson)

    def test_from_py_json_volume(self):
        pyson = {'value': 0.002,
                 'unit': 'ppm',
                 'unit_type': 'volumefraction'}

        model = MassOrVolumeFraction.from_py_json(pyson)

        print(f"{pyson=}")
        print(f"{model.py_json()=}")
        assert model.py_json() == pyson


class TestConcentration:
    '''
    Unit used for unknown whether it's volume of mass or ??
    '''
    def test_init_empty(self):
        model = Concentration()

        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'concentration'}

    def test_convert_to(self):
        model = Concentration(value=1.0, unit='fraction')
        model.convert_to('%')

        assert model.value == 100.0
        assert model.unit == '%'

    def test_convert_to_invalid(self):
        model = Concentration(value=50, unit='%')
        with pytest.raises(uc.InvalidUnitError):
            model.convert_to('g/kg')

        assert model.value == 50
        assert model.unit == '%'


class TestDensity:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = Density()
        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'density'}

    def test_convert_to(self):
        model = Density(value=1000.0, unit='kg/m^3')
        model.convert_to('g/cm^3')

        assert model.value == 1.0
        assert model.unit == 'g/cm^3'

    def test_convert_to_API(self):
        model = Density(value=900.0, unit='kg/m^3')
        model.convert_to('API')

        assert math.isclose(model.value, 25.585438, rel_tol=1e-7)
        assert model.unit == 'API'

class TestDynamicViscosity:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = DynamicViscosity()
        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'dynamicviscosity'}

    def test_convert_to(self):
        model = DynamicViscosity(value=100.0, unit='cP')
        model.convert_to('P')

        assert model.value == 1.0
        assert model.unit == 'P'


class TestKinematicViscosity:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = KinematicViscosity()
        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'kinematicviscosity'}

    def test_convert_to(self):
        model = KinematicViscosity(value=100.0, unit='cSt')
        model.convert_to('St')

        assert model.value == 1.0
        assert model.unit == 'St'


class TestPressure:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = Pressure()
        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'pressure'}

    def test_convert_to(self):
        model = Pressure(value=10.0, unit='Pa')
        model.convert_to('dyn/cm^2')

        assert math.isclose(model.value, 100.0, rel_tol=1e-05)
        assert model.unit == 'dyn/cm^2'


class TestNeedleAdhesion:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = NeedleAdhesion()
        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': "needleadhesion"}

    def test_convert_to(self):
        model = NeedleAdhesion(value=10.0, unit='g/cm^2')

        with pytest.raises(ValueError):
            model.convert_to('kg/m^2')


class TestInterfacialTension:
    '''
        All of our common Measurement subclasses share a common codebase.
        We will only test the things that are different, which haven't been
        tested yet.
    '''
    def test_init_empty(self):
        model = InterfacialTension()
        py_json = model.py_json()

        # should only have a unit_type
        assert py_json == {'unit_type': 'interfacialtension'}

    def test_convert_to(self):
        model = InterfacialTension(value=1000.0, unit='dyne/cm')
        model.convert_to('N/m')

        #assert math.isclose(model.value, 10.0, rel_tol=1e-05)
        assert model.value == 1.0
        assert model.unit == 'N/m'
