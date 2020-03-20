
import pytest

from oil_database.models.oil.values import (UnittedValue,
                                            UnittedRange,
                                            Density,
                                            DensityList,
                                            Viscosity,
                                            ViscosityList,
                                            ProductType,
                                            )


def test_UnittedValue():
    uv = UnittedValue(1.0, unit="m")

    assert uv.value == 1.0
    assert uv.unit == "m"


# def test_UnittedValue_no_value():
#     with pytest.raises(TypeError):
#         UnittedValue(1.0)
#     with pytest.raises(TypeError):
#         UnittedValue("m/s")


def test_UnittedValue_json():
    uv = UnittedValue(1.0, unit="m")

    py_json = uv.py_json()

    print(py_json)

    assert py_json == {'value': 1.0, 'unit': 'm'}


def test_UnittedValue_from_py_json():
    uv = UnittedValue.from_py_json({'value': 1.0, 'unit': 'm'})

    assert uv.value == 1.0
    assert uv.unit == "m"


# def test_UnittedValue_from_py_json_missing_data():

#     with pytest.raises(TypeError):
#         UnittedValue.from_py_json({'value': 1.0})

#     with pytest.raises(TypeError):
#         UnittedValue.from_py_json({'unit': 'm/s'})


def test_UnittedRange_both():
    ur = UnittedValue(None, 1.0, 5.0, "ft")

    assert ur.min_value == 1.0
    assert ur.max_value == 5.0
    assert ur.unit == "ft"


def test_UnittedRange_json_sparse():
    ur = UnittedValue(max_value=5.0, unit='m')

    py_json = ur.py_json()

    assert py_json == {'max_value': 5.0, 'unit': 'm'}


def test_UnittedRange_json_full():
    ur = UnittedValue(max_value=5.0, unit='m')

    py_json = ur.py_json(sparse=False)

    assert py_json == {'value': None,
                       'max_value': 5.0,
                       'unit': 'm',
                       'min_value': None}


def test_UnittedRange_from_json():
    ur = UnittedValue.from_py_json({'min_value': 5.0,
                                    'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value is None
    assert ur.unit == "m/s"


def test_UnittedRange_from_json():
    ur = UnittedRange.from_py_json({'min_value': 5.0,
                                    'max_value': 10.1,
                                    'unit': 'm/s'})

    assert ur.min_value == 5.0
    assert ur.max_value == 10.1
    assert ur.unit == "m/s"


def test_Density_std():
    # note on validation: if there is a standard deviation, there should be
    #                     more than 1 replicate
    #                     and if there is more than one replicate, there should
    #                     probably be a non-zero standard deviation
    dm = Density(standard_deviation=1.2,
                 replicates=3)

    assert dm.density is None
    assert dm.standard_deviation == 1.2
    assert dm.replicates == 3


def test_Density_val():
    # note on validation: if there is a standard deviation, there should be
    #                     more than 1 replicate
    #                     and if there is more than one replicate, there should
    #                     probably be a non-zero standard deviation
    dm = Density(UnittedValue(0.8751, unit="kg/m^3"),
                 UnittedValue(15.0, unit="C"))

    assert dm.standard_deviation is None
    assert dm.density.value == 0.8751
    assert dm.ref_temp.value == 15.0
    assert dm.ref_temp.unit == 'C'


def test_DM_json():
    dm = Density(standard_deviation=1.2,
                 replicates=3,
                 density=UnittedValue(0.8751, unit="kg/m^3"),
                 ref_temp=UnittedValue(15.0, unit="C"),
                 )

    py_json = dm.py_json()

    print(py_json)

    assert len(py_json) == 4
    assert py_json['standard_deviation'] == 1.2
    assert py_json['replicates'] == 3
    assert py_json['density'] == {'unit': 'kg/m^3', 'value': 0.8751}
    assert py_json['ref_temp'] == {'unit': 'C', 'value': 15.0}


def test_DM_from_py_json():
    dm = Density.from_py_json({'standard_deviation': 1.2,
                               'replicates': 3,
                               'density': {'value': 0.8751, 'unit': 'kg/m^3'},
                               'ref_temp': {'value': 15.0, 'unit': 'C'}
                               })

    assert dm.standard_deviation == 1.2
    assert dm.replicates == 3
    assert dm.density == UnittedValue(value=0.8751, unit='kg/m^3')
    assert dm.density.value == 0.8751
    assert dm.ref_temp == UnittedValue(value=15.0, unit='C')
    assert dm.ref_temp.unit == "C"


def test_density_list_falsey():
    dl = DensityList()

    assert not dl


def test_DensityList_fromjson():
    pyjson = [{'standard_deviation': 1.2,
               'replicates': 3,
               'density': {'value': 0.8751, 'unit': 'kg/m^3'},
               'ref_temp': {'value': 15.0, 'unit': 'C'}
               },
              {'standard_deviation': 1.1,
               'replicates': 3,
               'density': {'value': 0.8751, 'unit': 'kg/m^3'},
               'ref_temp': {'value': 15.0, 'unit': 'C'}
               },
              ]
    dl = DensityList.from_py_json(pyjson)

    assert len(dl) == 2
    assert dl[0].density.value == 0.8751
    assert dl[1].standard_deviation == 1.1


def test_Viscosity_empty():
    vm = Viscosity()

    pyj = vm.py_json()

    # no values, should be an empty dict
    assert pyj == {}

    # should all be None if not sparse:
    pyj = vm.py_json(sparse=False)

    assert pyj['method']is None
    assert pyj['ref_temp'] is None
    assert pyj['replicates'] is None
    assert pyj['standard_deviation'] is None
    assert pyj['viscosity'] is None


@pytest.mark.parametrize("product_type", ('crude',
                                          'refined',
                                          'bitumen product',
                                          'Refined',
                                          'Bitumen Product',
                                          'other'))
def test_ProductType_validation(product_type):
    pt = ProductType(product_type)

    assert pt.validate() == []


@pytest.mark.parametrize("product_type", ('crud',
                                          'rfined',
                                          'bitumen',
                                          'Reefined',
                                          'Biitumen Product',
                                          'random'))
def test_ProductType_validation_invalid(product_type):
    pt = ProductType(product_type)

    result = pt.validate()
    assert len(result) == 1
    assert result[0].startswith("W003:")
