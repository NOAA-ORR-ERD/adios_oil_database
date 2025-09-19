"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field

from .validation.errors import ERRORS
from .validation.warnings import WARNINGS

from ..common.utilities import dataclass_to_json, JSON_List

from ..common.measurement import (Temperature,
                                  Density,
                                  DynamicViscosity,
                                  KinematicViscosity,
                                  SayboltViscosity,
                                  AngularVelocity,
                                  InterfacialTension)


class RefTempList:
    """
    mixin for all classes that are a list of points with
    reference temperatures
    """
    _data_name = None  # set in subclass -- one of: {"density", "viscosity", "tension"}

    def validate(self):
        """
        validator for anything that has a list of reference temps

        e.g. density and viscosity

        For viscosity it checks for shear rate as well.
        """
        points_list = self
        data_str = self.__class__.__name__
        msgs = super().validate()

        bad_item = False
        # make sure values are reasonable
        for pt in points_list:

            meas = getattr(pt, self._data_name, None)
            ref_temp = pt.ref_temp
            temp = getattr(ref_temp, 'value', None)

            # check the measurement
            if meas is None or meas.is_empty():
                    msgs.append(ERRORS["E049"].format(type(meas).__name__, temp))
                    bad_item = True
                    continue
            elif not meas.just_value():
                # "W014": "Non-simple value:{} for {}",
                msgs.append(WARNINGS["W014"].format(meas.as_text(), data_str))
                bad_item = True
                continue
            else:
                value = getattr(meas, 'value', None)

                # check if the value make any sense:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    msgs.append(ERRORS["E044"].format(value, self._data_name))
                    bad_item = True
                    continue
                else:
                    if value <= 0.0:
                        msgs.append(ERRORS["E044"].format(value, self._data_name))
                        bad_item = True
                        continue

            # check the ref temp

            # check if either are empty:
            # "E048": "Missing reference temperature for {} with value: {}",
            if ref_temp is None or ref_temp.value is None:  # ref_temp can't be a range, etc. is_empty():
                msgs.append(ERRORS["E048"].format(data_str, value))
                bad_item = True
                continue

            # check reasonable temp range.
            temp_c = pt.ref_temp.converted_to('C').value
            if temp_c is not None and temp_c < -100.0:  # arbitrary, but should catch K/C confusion
                t = f"{pt.ref_temp.value:.2f} {pt.ref_temp.unit}"
                msgs.append(ERRORS["E040"].format(data_str, t))
                continue

        # check for duplicate temp/shear_rate combos
        if not bad_item:

# <<<<<<< Updated upstream
#         # make sure there is data there
#         for pt in points_list:
#             meas = getattr(pt, data_name, None)
#             if meas is None or meas.no_value():
#                 msgs.append(ERRORS["E044"].format(None, data_name))
#                 continue
#             # how to check all three
#             value = meas.minimum
#             if value is None:
#                 value = meas.maximum

#             # if value is None:
#             #     # this should get picked up by the measurement test?
#             #     # breakpoint()
#             #     pass
#             #     # msgs.append(ERRORS["E044"].format(value, data_name))
#             # else:
#             try:
#                 value = float(value)
#             except (ValueError, TypeError):
#                 msgs.append(ERRORS["E044"].format(value, data_name))
#             else:
#                 if value <= 0.0:
#                     msgs.append(ERRORS["E044"].format(value, data_name))
            temps = []

            for p in points_list:
                temp = p.ref_temp.converted_to('K').value

                try:
                    temp = temp + p.shear_rate.value
                except (TypeError, AttributeError):
                    pass

                temps.append(temp)

            # look for duplicates
            temps.sort()
            diff = (abs(t2 - t1) for t1, t2 in zip(temps[1:], temps[:1]))

            for d in diff:
                if d < 1e-3:
                    msgs.append(ERRORS["E050"].format("Temperatures", data_str))

        return msgs

    def delete_empty_values(self):
        """
        Deletes entries that have empty values in either the ref_temp or value
        entry
        """
        points_list = self
        data_str = self.__class__.__name__

        for i in reversed(range(len(self))):
            pt = self[i]
            meas = getattr(pt, self._data_name, None)
            ref_temp = pt.ref_temp

            if (ref_temp is None
                or ref_temp.no_value()
                or meas is None
                or meas.no_value()):
                del self[i]


@dataclass_to_json
@dataclass
class DensityPoint:
    density: Density = None
    ref_temp: Temperature = None
    method: str = None
    comment: str = None


class DensityList(RefTempList, JSON_List):
    item_type = DensityPoint
    _data_name = "density"

    @classmethod
    def from_data(cls, data_table):
        """
        Create a DensityList from data of the format:

        ```
        [(density, density_unit, temp, temp_unit),
         (density, density_unit, temp, temp_unit),
         ...
         ]
        ```
        example:

        ```
        [(0.8663, "g/cm³", 15, "C"),
         (0.9012, "g/cm³", 0.0, "C"),
         ]
        """
        dl = cls()
        for row in data_table:
            dl.append(DensityPoint(density=Density(row[0], unit=row[1]),
                                   ref_temp=Temperature(row[2], unit=row[3]),
                                   ))
        # sort by temp -- assume the same units
        dl.sort(key=lambda dp: dp.ref_temp.converted_to('C').value)
        return dl

def check_for_out_of_order_visc(vis_list):
    """
    check out of order and missing shear rates for viscosity
    """
    msgs = []
    num_shear_rate = 0
    if len(vis_list) > 1:
        vis_list.sort(key=lambda sl: (sl[1], sl[2]))

        viscosities = {}
        for visc, temp, shear_rate in vis_list:
            viscosities.setdefault(shear_rate, []).append((temp, visc))
            if shear_rate is not None:
                num_shear_rate += 1

        for _k, v in viscosities.items():
            _temps, vis = zip(*v)
            if(any(i <= j for i, j in zip(vis, vis[1:]))):
                msgs.append(ERRORS["E062"])
        if num_shear_rate not in (0, len(vis_list)):
            msgs.append(WARNINGS["W015"])
    return msgs


def check_for_shear_rate(vis_list):
    num_shear_rate = 0
    for visc, temp, shear_rate in vis_list:
        if shear_rate is not None:
            num_shear_rate += 1
    if num_shear_rate:
        return [ERRORS["E062"]]

@dataclass_to_json
@dataclass
class DynamicViscosityPoint:
    viscosity: DynamicViscosity = None
    ref_temp: Temperature = None
    shear_rate: AngularVelocity = None
    method: str = None
    comment: str = None


class DynamicViscosityList(RefTempList, JSON_List):
    item_type = DynamicViscosityPoint
    _data_name = "viscosity"
    @classmethod
    def from_data(cls, data_table):
        """
        Create a DensityList from data of the format:

        ```
        [(viscosity, viscosity_unit, temp, temp_unit),
         (viscosity, viscosity, temp, temp_unit),
         ...
         ]
        ```
        example:

        ```
        [(100, "cSt", 273.15, "K"),
         (1234.3, "cSt", 15.0, "C"),
         ]
        """
        kvl = cls()
        for row in data_table:
            kvl.append(DynamicViscosityPoint(
                viscosity=DynamicViscosity(row[0], unit=row[1]),
                ref_temp=Temperature(row[2], unit=row[3]),
            ))

        # sort by temp -- assume the same units
        kvl.sort(key=lambda dp: dp.ref_temp.converted_to('C').value)

        return kvl

    def validate(self):
        """
        validator for viscosity

        Checks dvis are increasing with temperature.
        """
        msgs = super().validate()
        data_str = self.__class__.__name__
        points_list = self
        dvis_list = []

        for p in points_list:
            if p.ref_temp is None or p.ref_temp.is_empty():
                # continue  # Error should be caught by the base class
                # msgs.append(ERRORS["E042"]
                #             .format(data_str + " reference temp"))
                return msgs  # Error should be reported by base class

            ref_temp = p.ref_temp.converted_to('C').value

            try:
                shear_rate = p.shear_rate.value
            except (TypeError, AttributeError):
                shear_rate = None

            try:
                viscosity = p.viscosity.converted_to('Pas').value
            except (TypeError, AttributeError):
                viscosity = None

            if viscosity is not None:
                dvis_list.append((viscosity, ref_temp, shear_rate))

        # check for decreasing with temp.
        msgs += check_for_out_of_order_visc(dvis_list)
        # if len(dvis_list) > 1:
        #     dvis_list.sort(key=lambda sl: (sl[1], sl[2]))

        #     viscosities = {}
        #     for visc, temp, shear_rate in dvis_list:
        #         viscosities.setdefault(shear_rate, []).append((temp, visc))

        #     for _k, v in viscosities.items():
        #         _temps, dvis = zip(*v)
        #         if(any(i <= j for i, j in zip(dvis, dvis[1:]))):
        #             msgs.append(ERRORS["E062"])

        return msgs


@dataclass_to_json
@dataclass
class KinematicViscosityPoint:
    viscosity: KinematicViscosity = None
    ref_temp: Temperature = None
    shear_rate: AngularVelocity = None
    method: str = None
    comment: str = None


class KinematicViscosityList(RefTempList, JSON_List):
    item_type = KinematicViscosityPoint
    _data_name = "viscosity"
    @classmethod
    def from_data(cls, data_table):
        """
        Create a KinematicViscosityList from data of the format:

        ```
        [(viscosity, viscosity_unit, temp, temp_unit),
         (viscosity, viscosity_unit, temp, temp_unit),
         ...
         ]
        ```
        example:

        ```
        [(100, "cSt", 273.15, "K"),
         (1234.3, "cSt", 15.0, "C"),
         ]
        """
        kvl = cls()
        for row in data_table:
            kvl.append(KinematicViscosityPoint(
                viscosity=KinematicViscosity(row[0], unit=row[1]),
                ref_temp=Temperature(row[2], unit=row[3]),
            ))

        # sort by temp -- assume the same units
        kvl.sort(key=lambda dp: dp.ref_temp.converted_to('C').value)

        return kvl

    def validate(self):
        """
        validator for viscosity

        Checks kvis are increasing with temperature.
        """
        msgs = super().validate()
        data_str = self.__class__.__name__
        points_list = self
        kvis_list = []

        for p in points_list:
            if p.ref_temp is None or p.ref_temp.is_empty():
                # msgs.append(ERRORS["E042"]
                #             .format(data_str + " reference temp"))
                return msgs  # error should have been caught by base class

            ref_temp = p.ref_temp.converted_to('C').value

            try:
                shear_rate = p.shear_rate.value
            except (TypeError, AttributeError):
                shear_rate = 0

            try:
                viscosity = p.viscosity.converted_to('m^2/s').value
            except (TypeError, AttributeError):
                viscosity = None

            if viscosity is not None:
                kvis_list.append((viscosity, ref_temp, shear_rate))

        # check for decreasing with temp.
        msgs += check_for_out_of_order_visc(kvis_list)

        return msgs


@dataclass_to_json
@dataclass
class SayboltViscosityPoint:
    viscosity: SayboltViscosity = None
    ref_temp: Temperature = None
    shear_rate: AngularVelocity = None
    method: str = None
    comment: str = None


class SayboltViscosityList(RefTempList, JSON_List):
    item_type = SayboltViscosityPoint


@dataclass_to_json
@dataclass
class PourPoint:
    measurement: Temperature = None
    method: str = None
    comment: str = None


@dataclass_to_json
@dataclass
class FlashPoint:
    measurement: Temperature = None
    method: str = None
    comment: str = None


@dataclass_to_json
@dataclass
class InterfacialTensionPoint:
    tension: InterfacialTension = None
    ref_temp: Temperature = None
    method: str = None
    comment: str = None


class InterfacialTensionList(RefTempList, JSON_List):
    item_type = InterfacialTensionPoint
    _data_name = "tension"

@dataclass_to_json
@dataclass
class PhysicalProperties:
    pour_point: PourPoint = None
    flash_point: FlashPoint = None
    appearance: str = ''

    densities: DensityList = field(default_factory=DensityList)
    kinematic_viscosities: KinematicViscosityList = field(default_factory=KinematicViscosityList)
    dynamic_viscosities: DynamicViscosityList = field(default_factory=DynamicViscosityList)

    interfacial_tension_air: InterfacialTensionList = field(default_factory=InterfacialTensionList)
    interfacial_tension_water: InterfacialTensionList = field(default_factory=InterfacialTensionList)
    interfacial_tension_seawater: InterfacialTensionList = field(default_factory=InterfacialTensionList)
