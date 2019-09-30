'''
    Test our FloatUnit model class
    This is one of the very basic building blocks of all our models.
'''
import pytest

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


class TestFloatUnit():
    @pytest.mark.parametrize('value, unit, expected',
                             [
                              (10.0, '%', '10.0 %'),
                              (10.0, '1', '10.0'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight', 'N/A',
                                  marks=pytest.mark.raises(exception=ValueError)),
                              pytest.param(
                                  10.0, '', 'N/A',
                                  marks=pytest.mark.raises(exception=ValueError)),
                              pytest.param(
                                  10.0, None, 'N/A',
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit, expected):
        float_unit = FloatUnit(value=value, unit=unit)

        assert float_unit.value == value
        assert float_unit.unit == unit

        assert repr(float_unit) == (u'<FloatUnit({})>'
                                    .format(expected))

    @pytest.mark.parametrize('value, min_value, max_value, unit, expected',
                             [
                              (10.0, None, None, '1', '10.0'),
                              (None, 10.0, None, '1', '>10.0'),
                              (None, None, 10.0, '1', '<10.0'),
                              (None, 10.0, 20.0, '1', '[10.0\u219220.0]'),
                              (None, 10.0, 10.0, '1', '10.0'),
                              (10.0, None, None, '%', '10.0 %'),
                              (None, 10.0, None, '%', '>10.0 %'),
                              (None, None, 10.0, '%', '<10.0 %'),
                              (None, 10.0, 20.0, '%', '[10.0\u219220.0] %'),
                              (None, 10.0, 10.0, '%', '10.0 %'),
                              (None, None, None, '1', ''),
                              (None, None, None, '%', ''),
                              (10.0, 20.0, 30.0, '1', '10.0'),
                              (10.0, 20.0, 30.0, '%', '10.0 %'),
                              ])
    def test_interval_init(self, value, min_value, max_value, unit, expected):
        float_unit = FloatUnit(value=value,
                               min_value=min_value,
                               max_value=max_value,
                               unit=unit)

        assert float_unit.value == value
        assert float_unit.min_value == min_value
        assert float_unit.max_value == max_value
        assert float_unit.unit == unit

        assert repr(float_unit) == (u'<FloatUnit({})>'
                                    .format(expected))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        am_unit = AngularMeasureUnit(value=value, unit=unit)

        assert repr(am_unit) == (u'<AngularMeasureUnit({} {})>'
                                 .format(value, unit))
        assert str(am_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        area_unit = AreaUnit(value=value, unit=unit)

        assert repr(area_unit) == (u'<AreaUnit({} {})>'.format(value, unit))
        assert str(area_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        cw_unit = ConcentrationInWaterUnit(value=value, unit=unit)

        assert repr(cw_unit) == (u'<ConcentrationInWaterUnit({} {})>'
                                 .format(value, unit))
        assert str(cw_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        density_unit = DensityUnit(value=value, unit=unit)

        assert repr(density_unit) == (u'<DensityUnit({} {})>'
                                      .format(value, unit))
        assert str(density_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        discharge_unit = DischargeUnit(value=value, unit=unit)

        assert repr(discharge_unit) == (u'<DischargeUnit({} {})>'
                                        .format(value, unit))
        assert str(discharge_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        kvis_unit = KinematicViscosityUnit(value=value, unit=unit)

        assert repr(kvis_unit) == (u'<KinematicViscosityUnit({} {})>'
                                   .format(value, unit))
        assert str(kvis_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        length_unit = LengthUnit(value=value, unit=unit)

        assert repr(length_unit) == (u'<LengthUnit({} {})>'
                                     .format(value, unit))
        assert str(length_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        mass_unit = MassUnit(value=value, unit=unit)

        assert repr(mass_unit) == (u'<MassUnit({} {})>'.format(value, unit))
        assert str(mass_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        oc_unit = OilConcentrationUnit(value=value, unit=unit)

        assert repr(oc_unit) == (u'<OilConcentrationUnit({} {})>'
                                 .format(value, unit))
        assert str(oc_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        temp_unit = TemperatureUnit(value=value, unit=unit)

        assert repr(temp_unit) == (u'<TemperatureUnit({} {})>'
                                   .format(value, unit))
        assert str(temp_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        time_unit = TimeUnit(value=value, unit=unit)

        assert repr(time_unit) == (u'<TimeUnit({} {})>'.format(value, unit))
        assert str(time_unit) == (u'{} {}'.format(value, unit))


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
                                  marks=pytest.mark.raises(exception=ValueError)),
                              ])
    def test_init(self, value, unit):
        velocity_unit = VelocityUnit(value=value, unit=unit)

        assert repr(velocity_unit) == (u'<VelocityUnit({} {})>'.format(value,
                                                                       unit))
        assert str(velocity_unit) == (u'{} {}'.format(value, unit))


class TestVolumeUnit(object):
    @pytest.mark.parametrize('value, unit',
                             [
                              (10.0, b'barrel'),
                              (10.0, b'barrel (petroleum)'),
                              (10.0, b'barrels'),
                              (10.0, b'bbl'),
                              (10.0, b'bbls'),
                              (10.0, b'cc'),
                              (10.0, b'cm^3'),
                              (10.0, b'cu cm'),
                              (10.0, b'cu feet'),
                              (10.0, b'cu inch'),
                              (10.0, b'cu km'),
                              (10.0, b'cu m'),
                              (10.0, b'cu yard'),
                              (10.0, b'cubic centimeter'),
                              (10.0, b'cubic foot'),
                              (10.0, b'cubic inch'),
                              (10.0, b'cubic kilometer'),
                              (10.0, b'cubic kilometers'),
                              (10.0, b'cubic meter'),
                              (10.0, b'cubic meters'),
                              (10.0, b'cubic yard'),
                              (10.0, b'cubicfeet'),
                              (10.0, b'cubicinches'),
                              (10.0, b'cubicyards'),
                              (10.0, b'fluid ounce'),
                              (10.0, b'fluid ounce (UK)'),
                              (10.0, b'fluid oz'),
                              (10.0, b'fluid oz(uk)'),
                              (10.0, b'ft^3'),
                              (10.0, b'gal'),
                              (10.0, b'gallon'),
                              (10.0, b'gallon (UK)'),
                              (10.0, b'gallons'),
                              (10.0, b'gallons(uk)'),
                              (10.0, b'in^3'),
                              (10.0, b'km^3'),
                              (10.0, b'l'),
                              (10.0, b'liter'),
                              (10.0, b'liters'),
                              (10.0, b'm^3'),
                              (10.0, b'milgal'),
                              (10.0, b'million US gallon'),
                              (10.0, b'milliongallons'),
                              (10.0, b'ounces(fluid)'),
                              (10.0, b'oz'),
                              (10.0, b'ukgal'),
                              (10.0, b'ukoz'),
                              (10.0, b'usgal'),
                              (10.0, b'yd^3'),
                              (10.0, 'cm\xb3'),
                              (10.0, 'ft\xb3'),
                              (10.0, 'in\xb3'),
                              (10.0, 'km\xb3'),
                              (10.0, 'm\xb3'),
                              (10.0, 'yd\xb3'),
                              pytest.param(
                                  10.0, 'hogsheads per fortnight',
                                  marks=pytest.mark.raises(exception=ValueError)),

                              ])
    def test_init(self, value, unit):
        volume_unit = VolumeUnit(value=value, unit=unit)

        if hasattr(unit, 'decode'):
            unit = unit.decode('utf-8')

        assert repr(volume_unit) == ('<VolumeUnit({} {})>'.format(value, unit))
        assert str(volume_unit) == (u'{} {}'.format(value, unit))
