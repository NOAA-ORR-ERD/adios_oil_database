"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""
from dataclasses import dataclass, field
from operator import itemgetter

from .validation.errors import ERRORS

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
    def validate(self):
        """
        validator for anything that has a list of reference temps

        e.g. density and viscosity

        For viscosity it checks for shear rate as well.
        """
        points_list = self
        data_str = self.__class__.__name__
        msgs = super().validate()

        # check for odd temperatures
        for pt in points_list:
            if pt.ref_temp is None:
                msgs.append(ERRORS["E042"]
                            .format(data_str + " reference temp"))
                return msgs

            temp = pt.ref_temp.converted_to('C').value

            if temp is None:
                msgs.append(ERRORS["E042"]
                            .format(data_str + " reference temp"))
                return msgs

            if temp < -100.0:  # arbitrary, but should catch K/C confusion
                t = f"{pt.ref_temp.value:.2f} {pt.ref_temp.unit}"
                msgs.append(ERRORS["E040"].format(data_str, t))

        # check for duplicate temp/shear_rate combos
        temps = []

        for p in points_list:
            temp = p.ref_temp.converted_to('K').value

            try:
                temp = temp + p.shear_rate.value
            except (TypeError, AttributeError):
                pass

            temps.append(temp)

        temps.sort()
        diff = (abs(t2 - t1) for t1, t2 in zip(temps[1:], temps[:1]))

        for d in diff:
            if d < 1e-3:
                msgs.append(ERRORS["E050"].format("Temperatures", data_str))

        # make sure values are reasonable too
        # find the attr with the data
        for name in {"density", "viscosity", "tension"}:
            if hasattr(self.item_type, name):
                data_name = name
                break
            else:
                data_name = None

        for pt in points_list:
            value = getattr(getattr(pt, data_name, None), 'value', None)

            if value is not None:
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    msgs.append(ERRORS["E044"].format(value, data_name))
                else:
                    if value <= 0.0:
                        msgs.append(ERRORS["E044"].format(value, data_name))

        return msgs


@dataclass_to_json
@dataclass
class DensityPoint:
    density: Density = None
    ref_temp: Temperature = None
    method: str = None
    comment: str = None


class DensityList(RefTempList, JSON_List):
    item_type = DensityPoint

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
            kvl.append(DynamicViscosityPoint(viscosity=DynamicViscosity(row[0], unit=row[1]),
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
        points_list = self
        dvis_list = []
        for pt in points_list:
            try:
                ref_temp = pt.ref_temp.converted_to('C').value
                viscosity = pt.viscosity.converted_to('Pas').value
                dvis_list.append((viscosity,ref_temp))
            except (TypeError, AttributeError):
                pass

        if len(dvis_list) > 1:
            dvis_list = sorted(dvis_list, key=itemgetter(1))
            dvis_list.sort(key=itemgetter(0), reverse=True)
            dvis, temps = zip(*dvis_list)
            if(any(i <= j for i, j in zip(dvis, dvis[1:]))):
                msgs.append(ERRORS["E062"])

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
            kvl.append(KinematicViscosityPoint(viscosity=KinematicViscosity(row[0], unit=row[1]),
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
        points_list = self
        kvis_list = []
        for pt in points_list:
            try:
                ref_temp = pt.ref_temp.converted_to('C').value
                viscosity = pt.viscosity.converted_to('m^2/s').value
                kvis_list.append((viscosity,ref_temp))
            except (TypeError, AttributeError):
                pass

        if len(kvis_list) > 1:
            kvis_list = sorted(kvis_list, key=itemgetter(1))
            kvis, temps = zip(*kvis_list)
            if(any(i <= j for i, j in zip(kvis, kvis[1:]))):
                msgs.append(ERRORS["E062"])

#         if len(temp) > 1:
#             if(any(i > j for i, j in zip(temp, temp[1:]))):
#                 msgs.append(ERRORS["E061"])
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
