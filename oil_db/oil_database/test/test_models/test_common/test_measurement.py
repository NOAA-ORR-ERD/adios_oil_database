
import pytest
import math

from oil_database.models.common import (ProductType,
                                        UnittedValue,
                                        UnittedRange,
                                        MeasurementBase,
                                        Temperature,
                                        Length,
                                        Mass,
                                        MassFraction,
                                        VolumeFraction,
                                        Density,
                                        DynamicViscosity,
                                        KinematicViscosity,
                                        Pressure,
                                        NeedleAdhesion,
                                        InterfacialTension)


class TestProductType:
    @pytest.mark.parametrize("product_type", ('crude',
                                              'refined',
                                              'bitumen product',
                                              'Refined',
                                              'Bitumen Product',
                                              'other'))
    def test_validation(self, product_type):
        pt = ProductType(product_type)

        assert pt.validate() == []

    @pytest.mark.parametrize("product_type", ('crud',
                                              'rfined',
                                              'bitumen',
                                              'Reefined',
                                              'Biitumen Product',
                                              'random'))
    def test_validation_invalid(self, product_type):
        pt = ProductType(product_type)

        result = pt.validate()
        assert len(result) == 1
        assert result[0].startswith("W003:")


class TestUnittedValue:
    def test_init(self):
        uv = UnittedValue(1.0, unit="m")

        assert uv.value == 1.0
        assert uv.unit == "m"

    def test_init_no_value(self):
        with pytest.raises(ValueError):
            UnittedValue(1.0)
        with pytest.raises(ValueError):
            UnittedValue("m/s")

    def test_from_py_json(self):
        uv = UnittedValue.from_py_json({'value': 1.0, 'unit': 'm'})

        assert uv.value == 1.0
        assert uv.unit == "m"

    def test_json(self):
        uv = UnittedValue(1.0, unit="m")
        py_json = uv.py_json()

        print(py_json)

        assert py_json == {'value': 1.0, 'unit': 'm'}

    def test_from_py_json_missing_data(self):
        '''
            Not sure why we aren't raising an exception
        '''
        with pytest.raises(ValueError):
            UnittedValue.from_py_json({'value': 1.0})

        with pytest.raises(ValueError):
            UnittedValue.from_py_json({'unit': 'm/s'})


class TestUnittedRange:
    def test_min_max(self):
        ur = UnittedValue(None, 1.0, 5.0, "ft")

        assert ur.min_value == 1.0
        assert ur.max_value == 5.0
        assert ur.unit == "ft"

    def test_json_sparse(self):
        ur = UnittedValue(max_value=5.0, unit='m')
        py_json = ur.py_json()

        assert py_json == {'max_value': 5.0, 'unit': 'm'}

    def test_json_max_only(self):
        ur = UnittedValue(max_value=5.0, unit='m')
        py_json = ur.py_json(sparse=False)

        assert py_json == {'value': None,
                           'min_value': None,
                           'max_value': 5.0,
                           'unit': 'm'}

    def test_from_json_min_only(self):
        ur = UnittedValue.from_py_json({'min_value': 5.0,
                                        'unit': 'm/s'})

        assert ur.min_value == 5.0
        assert ur.max_value is None
        assert ur.unit == "m/s"

    def test_from_json_min_max(self):
        ur = UnittedRange.from_py_json({'min_value': 5.0,
                                        'max_value': 10.1,
                                        'unit': 'm/s'})

        assert ur.min_value == 5.0
        assert ur.max_value == 10.1
        assert ur.unit == "m/s"


class TestMeasurementBase:
    '''
        Todo: is there any way to raise a NotImplementedError here?  We don't
              really want to use this class, just the subclasses.
    '''
    def test_init(self):
        model = MeasurementBase()

        assert model.value is None
        assert model.min_value is None
        assert model.max_value is None

        assert model.unit is None
        assert model.unit_type is None

        assert model.standard_deviation is None
        assert model.replicates is None


class TestTemperature:
    '''
        Todo: We really need to enforce that *some* value is passed in
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
        assert py_json == {'unit_type': None}

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
