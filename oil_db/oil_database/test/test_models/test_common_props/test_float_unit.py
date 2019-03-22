'''
    Test our FloatUnit model class
    This is one of the very basic building blocks of all our models.
'''
import pytest

from pymodm.errors import ValidationError

from oil_database.models.common.float_unit import (FloatUnit,
                                                   AngularMeasureUnit,
                                                   AreaUnit,
                                                   ConcentrationInWaterUnit,
                                                   DensityUnit,
                                                   DischargeUnit,
                                                   KinematicViscosityUnit,
                                                   LengthUnit,
                                                   MassUnit,
                                                   OilConcentrationUnit,
                                                   TemperatureUnit,
                                                   TimeUnit,
                                                   VelocityUnit,
                                                   VolumeUnit)


class TestFloatUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'kg/m^3'),
                              (10.0, 'g/cm^3'),
                              (10.0, 'hogsheads per fortnight'),
                              ])
    def test_init(self, value, unit):
        float_unit = FloatUnit(value=value, unit=unit)

        assert float_unit.value == value
        assert float_unit.unit == unit

        float_unit.clean_fields()

        assert repr(float_unit) == (u'<FloatUnit({} {})>'
                                    .format(float_unit.value, float_unit.unit))

    @pytest.mark.parametrize('value, expected',
                             [
                              ('Area', ['Area']),
                              ('OilConcentration', ['Oil', 'Concentration']),
                              ('ConcentrationInWater', ['Concentration',
                                                        'In',
                                                        'Water']),
                              ('concentrationInWater', ['In', 'Water']),
                              ])
    def test_camelcase(self, value, expected):
        words = FloatUnit.__metaclass__.separate_camelcase(value)

        assert words == expected

    @pytest.mark.parametrize('value, lower, expected',
                             [
                              ('Area', False, 'Area'),
                              ('OilConcentration', False, 'Oil Concentration'),
                              ('ConcentrationInWater', False,
                               'Concentration In Water'),
                              ('concentrationInWater', False, 'In Water'),
                              ('Area', True, 'area'),
                              ('OilConcentration', True, 'oil concentration'),
                              ('ConcentrationInWater', True,
                               'concentration in water'),
                              ('concentrationInWater', True, 'in water'),
                              ])
    def test_camelcase_to_space(self, value, lower, expected):
        words = FloatUnit.__metaclass__.camelcase_to_space(value, lower=lower)

        assert words == expected

    @pytest.mark.parametrize('value, lower, expected',
                             [
                              ('Area', False, 'Area'),
                              ('OilConcentration', False, 'Oil_Concentration'),
                              ('ConcentrationInWater', False,
                               'Concentration_In_Water'),
                              ('concentrationInWater', False, 'In_Water'),
                              ('Area', True, 'area'),
                              ('OilConcentration', True, 'oil_concentration'),
                              ('ConcentrationInWater', True,
                               'concentration_in_water'),
                              ('concentrationInWater', True, 'in_water'),
                              ])
    def test_camelcase_to_underscore(self, value, lower, expected):
        words = FloatUnit.__metaclass__.camelcase_to_underscore(value,
                                                                lower=lower)

        assert words == expected


class TestAngularMeasureUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, u'rad'),
                              (10.0, u'radian'),
                              (10.0, u'radians'),
                              (10.0, u'deg'),
                              (10.0, u'degree'),
                              (10.0, u'degrees'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        am_unit = AngularMeasureUnit(value=value, unit=unit)

        am_unit.clean_fields()

        assert repr(am_unit) == (u'<AngularMeasureUnit({} {})>'
                                 .format(value, unit)
                                 .encode('utf-8'))
        assert str(am_unit) == (u'<AngularMeasureUnit({} {})>'
                                .format(value, unit)
                                .encode('utf-8'))


class TestAreaUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'acre'),
                              (10.0, 'acres'),
                              (10.0, 'cm^2'),
                              (10.0, 'ft^2'),
                              (10.0, 'ha'),
                              (10.0, 'hectare'),
                              (10.0, 'hectares'),
                              (10.0, 'in^2'),
                              (10.0, 'km^2'),
                              (10.0, 'm^2'),
                              (10.0, 'nm^2'),
                              (10.0, 'sq cm'),
                              (10.0, 'sq foot'),
                              (10.0, 'sq inch'),
                              (10.0, 'sq km'),
                              (10.0, 'sq m'),
                              (10.0, 'sq miles'),
                              (10.0, 'sq nm'),
                              (10.0, 'sq yards'),
                              (10.0, 'square centimeter'),
                              (10.0, 'square feet'),
                              (10.0, 'square foot'),
                              (10.0, 'square inch'),
                              (10.0, 'square inches'),
                              (10.0, 'square kilometer'),
                              (10.0, 'square meter'),
                              (10.0, 'square mile'),
                              (10.0, 'square nautical mile'),
                              (10.0, 'square yard'),
                              (10.0, 'squareyards'),
                              (10.0, u'cm\xb2'),
                              (10.0, u'ft\xb2'),
                              (10.0, u'in\xb2'),
                              (10.0, u'km\xb2'),
                              (10.0, u'm\xb2'),
                              (10.0, u'nm\xb2'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        area_unit = AreaUnit(value=value, unit=unit)

        area_unit .clean_fields()

        assert repr(area_unit) == (u'<AreaUnit({} {})>'
                                   .format(value, unit)
                                   .encode('utf-8'))
        assert str(area_unit) == (u'<AreaUnit({} {})>'
                                  .format(value, unit)
                                  .encode('utf-8'))


class TestConcentrationInWaterUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, '%'),
                              (10.0, 'fraction'),
                              (10.0, 'fraction (decimal)'),
                              (10.0, 'g/m^3'),
                              (10.0, 'gram per cubic meter'),
                              (10.0, 'kg/m^3'),
                              (10.0, 'kilogram per cubic meter'),
                              (10.0, 'lb/ft^3'),
                              (10.0, 'mass per mass'),
                              (10.0, 'mg/kg'),
                              (10.0, 'mg/l'),
                              (10.0, 'mg/ml'),
                              (10.0, 'microgram per liter'),
                              (10.0, 'milligram per kilogram'),
                              (10.0, 'milligram per liter'),
                              (10.0, 'milligram per milliliter'),
                              (10.0, 'nanogram per liter'),
                              (10.0, 'ng/l'),
                              (10.0, 'part per billion'),
                              (10.0, 'part per million'),
                              (10.0, 'part per thousand'),
                              (10.0, 'part per trillion'),
                              (10.0, 'parts per billion'),
                              (10.0, 'parts per hundred'),
                              (10.0, 'parts per million'),
                              (10.0, 'parts per thousand'),
                              (10.0, 'parts per trillion'),
                              (10.0, 'per cent'),
                              (10.0, 'percent'),
                              (10.0, 'pound per cubic foot'),
                              (10.0, 'ppb'),
                              (10.0, 'ppm'),
                              (10.0, 'ppt'),
                              (10.0, 'pptr'),
                              (10.0, 'ug/l'),
                              (10.0, u'g/m\xb3'),
                              (10.0, u'kg/m\xb3'),
                              (10.0, u'lb/ft\xb3'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        cw_unit = ConcentrationInWaterUnit(value=value, unit=unit)

        cw_unit.clean_fields()

        assert repr(cw_unit) == (u'<ConcentrationInWaterUnit({} {})>'
                                 .format(value, unit)
                                 .encode('utf-8'))
        assert str(cw_unit) == (u'<ConcentrationInWaterUnit({} {})>'
                                .format(value, unit)
                                .encode('utf-8'))


class TestDensityUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'grams per cubic centimeter'),
                              (10.0, 'gram per cubic centimeter'),
                              (10.0, 'pound per cubic foot'),
                              (10.0, 'g/cm^3'),
                              (10.0, 'lbs/ft^3'),
                              (10.0, 'kg/m^3'),
                              (10.0, 'SG'),
                              (10.0, 'S'),
                              (10.0, 'api'),
                              (10.0, 'API degree'),
                              (10.0, 'Spec grav'),
                              (10.0, 'specificgravity'),
                              (10.0, 'kilogram per cubic meter'),
                              (10.0, 'specificgravity(15C)'),
                              (10.0, u'specific gravity (15\xb0C)'),
                              (10.0, u'lb/ft\xb3'),
                              (10.0, u'g/cm\xb3'),
                              (10.0, u'kg/m\xb3'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        density_unit = DensityUnit(value=value, unit=unit)

        density_unit.clean_fields()

        assert repr(density_unit) == (u'<DensityUnit({} {})>'
                                      .format(value, unit)
                                      .encode('utf-8'))
        assert str(density_unit) == (u'<DensityUnit({} {})>'
                                     .format(value, unit)
                                     .encode('utf-8'))


class TestDischargeUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'barrel per day'),
                              (10.0, 'barrel per hour'),
                              (10.0, 'bbl/day'),
                              (10.0, 'bbl/hr'),
                              (10.0, 'cfs'),
                              (10.0, 'cms'),
                              (10.0, 'cu feet/s'),
                              (10.0, 'cu m/s'),
                              (10.0, 'cubic foot per minute'),
                              (10.0, 'cubic foot per second'),
                              (10.0, 'cubic meter per hour'),
                              (10.0, 'cubic meter per min'),
                              (10.0, 'cubic meter per second'),
                              (10.0, 'feet^3/s'),
                              (10.0, 'ft^3/min'),
                              (10.0, 'gal/day'),
                              (10.0, 'gal/hr'),
                              (10.0, 'gal/min'),
                              (10.0, 'gal/s'),
                              (10.0, 'gal/sec'),
                              (10.0, 'gallon per day'),
                              (10.0, 'gallon per hour'),
                              (10.0, 'gallon per minute'),
                              (10.0, 'gallon per second'),
                              (10.0, 'gpm'),
                              (10.0, 'l/min'),
                              (10.0, 'l/s'),
                              (10.0, 'liter per minute'),
                              (10.0, 'liter per second'),
                              (10.0, 'lps'),
                              (10.0, 'm^3/hr'),
                              (10.0, 'm^3/min'),
                              (10.0, 'm^3/s'),
                              (10.0, u'ft\xb3/min'),
                              (10.0, u'ft\xb3/s'),
                              (10.0, u'm\xb3/hr'),
                              (10.0, u'm\xb3/min'),
                              (10.0, u'm\xb3/s'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        discharge_unit = DischargeUnit(value=value, unit=unit)

        discharge_unit.clean_fields()

        assert repr(discharge_unit) == (u'<DischargeUnit({} {})>'
                                        .format(value, unit)
                                        .encode('utf-8'))
        assert str(discharge_unit) == (u'<DischargeUnit({} {})>'
                                       .format(value, unit)
                                       .encode('utf-8'))


class TestKinematicViscosityUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'SFS'),
                              (10.0, 'SSF'),
                              (10.0, 'SSU'),
                              (10.0, 'SUS'),
                              (10.0, 'Saybolt Furol Second'),
                              (10.0, 'Saybolt Universal Second'),
                              (10.0, 'St'),
                              (10.0, 'Stoke'),
                              (10.0, 'cSt'),
                              (10.0, 'centiStoke'),
                              (10.0, 'centistokes'),
                              (10.0, 'cm^2/s'),
                              (10.0, 'in^2/s'),
                              (10.0, 'm^2/s'),
                              (10.0, 'mm^2/s'),
                              (10.0, 'square centimeter per second'),
                              (10.0, 'square inch per second'),
                              (10.0, 'square meter per second'),
                              (10.0, 'square millimeter per second'),
                              (10.0, 'squareinchespersecond'),
                              (10.0, 'stokes'),
                              (10.0, u'cm\xb2/s'),
                              (10.0, u'in\xb2/s'),
                              (10.0, u'mm\xb2/s'),
                              (10.0, u'm\xb2/s'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        kvis_unit = KinematicViscosityUnit(value=value, unit=unit)

        kvis_unit.clean_fields()

        assert repr(kvis_unit) == (u'<KinematicViscosityUnit({} {})>'
                                   .format(value, unit)
                                   .encode('utf-8'))
        assert str(kvis_unit) == (u'<KinematicViscosityUnit({} {})>'
                                  .format(value, unit)
                                  .encode('utf-8'))


class TestLengthUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'centimeter'),
                              (10.0, 'centimeters'),
                              (10.0, 'cm'),
                              (10.0, 'fathom'),
                              (10.0, 'fathoms'),
                              (10.0, 'feet'),
                              (10.0, 'foot'),
                              (10.0, 'ft'),
                              (10.0, 'fthm'),
                              (10.0, 'in'),
                              (10.0, 'inch'),
                              (10.0, 'inches'),
                              (10.0, 'kilometer'),
                              (10.0, 'kilometers'),
                              (10.0, 'km'),
                              (10.0, 'latitude degree'),
                              (10.0, 'latitude minute'),
                              (10.0, 'latitudedegrees'),
                              (10.0, 'latitudeminutes'),
                              (10.0, 'm'),
                              (10.0, 'meter'),
                              (10.0, 'meters'),
                              (10.0, 'metre'),
                              (10.0, 'mi'),
                              (10.0, 'micron'),
                              (10.0, 'microns'),
                              (10.0, 'mile'),
                              (10.0, 'miles'),
                              (10.0, 'millimeter'),
                              (10.0, 'millimeters'),
                              (10.0, 'mm'),
                              (10.0, 'nautical mile'),
                              (10.0, 'nauticalmiles'),
                              (10.0, 'nm'),
                              (10.0, 'yard'),
                              (10.0, 'yards'),
                              (10.0, 'yrd'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        length_unit = LengthUnit(value=value, unit=unit)

        length_unit.clean_fields()

        assert repr(length_unit) == (u'<LengthUnit({} {})>'
                                     .format(value, unit)
                                     .encode('utf-8'))
        assert str(length_unit) == (u'<LengthUnit({} {})>'
                                    .format(value, unit)
                                    .encode('utf-8'))


class TestMassUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'g'),
                              (10.0, 'gram'),
                              (10.0, 'grams'),
                              (10.0, 'kg'),
                              (10.0, 'kilogram'),
                              (10.0, 'kilograms'),
                              (10.0, 'lb'),
                              (10.0, 'lbs'),
                              (10.0, 'long ton'),
                              (10.0, 'metric ton'),
                              (10.0, 'metric ton (tonne)'),
                              (10.0, 'metric tons'),
                              (10.0, 'mt'),
                              (10.0, 'ounce'),
                              (10.0, 'ounces'),
                              (10.0, 'oz'),
                              (10.0, 'pound'),
                              (10.0, 'pounds'),
                              (10.0, 'slug'),
                              (10.0, 'slugs'),
                              (10.0, 'ton'),
                              (10.0, 'ton (UK)'),
                              (10.0, 'tonnes'),
                              (10.0, 'tons'),
                              (10.0, 'ukton'),
                              (10.0, 'uston'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        mass_unit = MassUnit(value=value, unit=unit)

        mass_unit.clean_fields()

        assert repr(mass_unit) == (u'<MassUnit({} {})>'
                                   .format(value, unit)
                                   .encode('utf-8'))
        assert str(mass_unit) == (u'<MassUnit({} {})>'
                                  .format(value, unit)
                                  .encode('utf-8'))


class TestOilConcentrationUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'barrel per acre'),
                              (10.0, 'barrel per square mile'),
                              (10.0, 'bbl/acre'),
                              (10.0, 'bbl/sq.mile'),
                              (10.0, 'cubic meter per square kilometer'),
                              (10.0, 'gal/acre'),
                              (10.0, 'gallon per acre'),
                              (10.0, 'in'),
                              (10.0, 'inch'),
                              (10.0, 'inches'),
                              (10.0, 'liter per hectare'),
                              (10.0, 'liter/hectare'),
                              (10.0, 'm^3/km^2'),
                              (10.0, 'micron'),
                              (10.0, 'microns'),
                              (10.0, 'millimeter'),
                              (10.0, 'millimeters'),
                              (10.0, 'mm'),
                              (10.0, u'bbl/mile\xb2'),
                              (10.0, u'm\xb3/km\xb2'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        oc_unit = OilConcentrationUnit(value=value, unit=unit)

        oc_unit.clean_fields()

        assert repr(oc_unit) == (u'<OilConcentrationUnit({} {})>'
                                 .format(value, unit)
                                 .encode('utf-8'))
        assert str(oc_unit) == (u'<OilConcentrationUnit({} {})>'
                                .format(value, unit)
                                .encode('utf-8'))


class TestTemperatureUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'degrees c'),
                              (10.0, 'degree kelvin'),
                              (10.0, 'degree k'),
                              (10.0, 'degrees f'),
                              (10.0, 'degrees fahrenheit'),
                              (10.0, 'F'),
                              (10.0, 'Kelvin'),
                              (10.0, 'K'),
                              (10.0, 'C'),
                              (10.0, 'degree f'),
                              (10.0, 'Fahrenheit'),
                              (10.0, 'deg k'),
                              (10.0, 'Celsius'),
                              (10.0, 'degrees celsius'),
                              (10.0, 'centigrade'),
                              (10.0, 'degrees k'),
                              (10.0, 'deg c'),
                              (10.0, 'degrees kelvin'),
                              (10.0, 'deg f'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        temp_unit = TemperatureUnit(value=value, unit=unit)

        temp_unit.clean_fields()

        assert repr(temp_unit) == (u'<TemperatureUnit({} {})>'
                                   .format(value, unit)
                                   .encode('utf-8'))
        assert str(temp_unit) == (u'<TemperatureUnit({} {})>'
                                  .format(value, unit)
                                  .encode('utf-8'))


class TestTimeUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'day'),
                              (10.0, 'days'),
                              (10.0, 'hour'),
                              (10.0, 'hours'),
                              (10.0, 'hr'),
                              (10.0, 'hrs'),
                              (10.0, 'min'),
                              (10.0, 'minute'),
                              (10.0, 'minutes'),
                              (10.0, 's'),
                              (10.0, 'sec'),
                              (10.0, 'second'),
                              (10.0, 'seconds'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        time_unit = TimeUnit(value=value, unit=unit)

        time_unit.clean_fields()

        assert repr(time_unit) == (u'<TimeUnit({} {})>'
                                   .format(value, unit)
                                   .encode('utf-8'))
        assert str(time_unit) == (u'<TimeUnit({} {})>'
                                  .format(value, unit)
                                  .encode('utf-8'))


class TestVelocityUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'centimeter per second'),
                              (10.0, 'cm/s'),
                              (10.0, 'feet per hour'),
                              (10.0, 'feet per minute'),
                              (10.0, 'feet per second'),
                              (10.0, 'feet/hour'),
                              (10.0, 'feet/min'),
                              (10.0, 'feet/s'),
                              (10.0, 'foot per hour'),
                              (10.0, 'foot per minute'),
                              (10.0, 'foot per second'),
                              (10.0, 'ft/hr'),
                              (10.0, 'ft/min'),
                              (10.0, 'ft/s'),
                              (10.0, 'ft/sec'),
                              (10.0, 'kilometer per hour'),
                              (10.0, 'km/h'),
                              (10.0, 'km/hr'),
                              (10.0, 'knot'),
                              (10.0, 'knots'),
                              (10.0, 'kts'),
                              (10.0, 'm s-1'),
                              (10.0, 'm/min'),
                              (10.0, 'm/s'),
                              (10.0, 'meter per minute'),
                              (10.0, 'meter per second'),
                              (10.0, 'meter second-1'),
                              (10.0, 'meters per minute'),
                              (10.0, 'meters per second'),
                              (10.0, 'meters s-1'),
                              (10.0, 'mile per hour'),
                              (10.0, 'miles per hour'),
                              (10.0, 'mph'),
                              (10.0, 'mps'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),
                              ])
    def test_init(self, value, unit):
        velocity_unit = VelocityUnit(value=value, unit=unit)

        velocity_unit.clean_fields()

        assert repr(velocity_unit) == (u'<VelocityUnit({} {})>'
                                       .format(value, unit)
                                       .encode('utf-8'))
        assert str(velocity_unit) == (u'<VelocityUnit({} {})>'
                                      .format(value, unit)
                                      .encode('utf-8'))


class TestVolumeUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, 'barrel'),
                              (10.0, 'barrel (petroleum)'),
                              (10.0, 'barrels'),
                              (10.0, 'bbl'),
                              (10.0, 'bbls'),
                              (10.0, 'cc'),
                              (10.0, 'cm^3'),
                              (10.0, 'cu cm'),
                              (10.0, 'cu feet'),
                              (10.0, 'cu inch'),
                              (10.0, 'cu km'),
                              (10.0, 'cu m'),
                              (10.0, 'cu yard'),
                              (10.0, 'cubic centimeter'),
                              (10.0, 'cubic foot'),
                              (10.0, 'cubic inch'),
                              (10.0, 'cubic kilometer'),
                              (10.0, 'cubic kilometers'),
                              (10.0, 'cubic meter'),
                              (10.0, 'cubic meters'),
                              (10.0, 'cubic yard'),
                              (10.0, 'cubicfeet'),
                              (10.0, 'cubicinches'),
                              (10.0, 'cubicyards'),
                              (10.0, 'fluid ounce'),
                              (10.0, 'fluid ounce (UK)'),
                              (10.0, 'fluid oz'),
                              (10.0, 'fluid oz(uk)'),
                              (10.0, 'ft^3'),
                              (10.0, 'gal'),
                              (10.0, 'gallon'),
                              (10.0, 'gallon (UK)'),
                              (10.0, 'gallons'),
                              (10.0, 'gallons(uk)'),
                              (10.0, 'in^3'),
                              (10.0, 'km^3'),
                              (10.0, 'l'),
                              (10.0, 'liter'),
                              (10.0, 'liters'),
                              (10.0, 'm^3'),
                              (10.0, 'milgal'),
                              (10.0, 'million US gallon'),
                              (10.0, 'milliongallons'),
                              (10.0, 'ounces(fluid)'),
                              (10.0, 'oz'),
                              (10.0, 'ukgal'),
                              (10.0, 'ukoz'),
                              (10.0, 'usgal'),
                              (10.0, 'yd^3'),
                              (10.0, u'cm\xb3'),
                              (10.0, u'ft\xb3'),
                              (10.0, u'in\xb3'),
                              (10.0, u'km\xb3'),
                              (10.0, u'm\xb3'),
                              (10.0, u'yd\xb3'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValidationError)),

                              ])
    def test_init(self, value, unit):
        volume_unit = VolumeUnit(value=value, unit=unit)

        volume_unit.clean_fields()

        assert repr(volume_unit) == (u'<VolumeUnit({} {})>'
                                     .format(value, unit)
                                     .encode('utf-8'))
        assert str(volume_unit) == (u'<VolumeUnit({} {})>'
                                    .format(value, unit)
                                    .encode('utf-8'))
