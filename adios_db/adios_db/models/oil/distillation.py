"""
Classes for storing measured values within an Oil record
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List
from ..common.measurement import (Temperature,
                                  MassOrVolumeFraction)

from ..common.validators import EnumValidator
from .validation.warnings import WARNINGS
from .validation.errors import ERRORS


@dataclass_to_json
@dataclass
class DistCut:
    fraction: MassOrVolumeFraction = None
    vapor_temp: Temperature = None


class DistCutList(JSON_List):
    item_type = DistCut

    @classmethod
    def from_data_arrays(cls,
                         fractions,
                         temps,
                         frac_unit,
                         temp_unit,
                         unit_type="MassFraction"):
        """
        Create a DistCutList from arrays of dist cut data

        :param fractions: sequence of cut fractions
        :param temps: sequence of cut vapor temperatures
        :param frac_unit: unit of fractions: e.g."%", "fraction"
        :param temp_unit: temperature unit: e.g. "C", "F", "K"
        :param unit_type="MassFraction": "MassFraction" or "VolumeFraction"
        """
        if len(fractions) != len(temps):
            raise ValueError("fractions and temps must be the same length")

        dcl = cls(DistCut(fraction=MassOrVolumeFraction(value=f,
                                                        unit=frac_unit,
                                                        unit_type=unit_type),
                          vapor_temp=Temperature(value=t, unit=temp_unit))
                  for f, t in zip(fractions, temps))

        return dcl


@dataclass_to_json
@dataclass
class Distillation:
    type: str = None  # "mass fraction" or "volume fraction"
    method: str = None
    end_point: Temperature = None
    fraction_recovered: MassOrVolumeFraction = None
    cuts: DistCutList = field(default_factory=DistCutList)
    comment: str = None


    def validate(self):
        msgs = []
        if self.cuts:  # only need to validate if there are cuts
            msgs.extend(EnumValidator({"mass fraction", "volume fraction"},
                                      ERRORS["E032"],
                                      case_insensitive=True)(self.type))

            if (self.fraction_recovered is None
                or (self.fraction_recovered.value is None
                    and self.fraction_recovered.max_value is None)):
                msgs.append(WARNINGS["W009"])
            else:
                frac_recov = (self.fraction_recovered.converted_to("fraction"))

                if frac_recov.value is not None:
                    val = frac_recov.value
                elif frac_recov.max_value is not None:
                    val = frac_recov.max_value
                else:
                    val = None
                    msgs.append(WARNINGS["W009"])

                if val is not None:
                    if not (0.0 <= val <= 1.0):
                        msgs.append(ERRORS["E041"]
                                    .format("distillation fraction recovered",
                                            val))

            for cut in self.cuts:
                if (cut.fraction is None or cut.fraction.value is None):
                    msgs.append(ERRORS['E042'].format('Distillation fraction'))
                else:
                    frac = cut.fraction.converted_to('fraction').value

                    if not (0.0 <= frac <= 1.0):
                        msgs.append(ERRORS['E041']
                                    .format('distillation fraction', frac))

                if (cut.vapor_temp is None or cut.vapor_temp.value is None):
                    msgs.append(ERRORS['E042']
                                .format('Distillation vapor temp'))
                else:
                    vt = cut.vapor_temp.convert_to('C').value

                    if vt < -100.0:
                        t = f"{cut.vapor_temp.value:.2f} {cut.vapor_temp.unit}"
                        msgs.append(ERRORS["E040"]
                                    .format("distillation vapor temp", t))

            # check if oil fraction is accumulative
            frac = []
            temp = []

            for cut in self.cuts:
                if hasattr(cut.fraction, 'converted_to'):
                    frac.append(cut.fraction.converted_to('fraction').value)
                else:
                    # Missing fractions in our cuts count as a discontinuity
                    frac.append(0.0)

                if hasattr(cut.vapor_temp, 'converted_to'):
                    temp.append(cut.vapor_temp.converted_to('C').value)
                else:
                    # Missing vapor_temps in our cuts count as a discontinuity
                    temp.append(0.0)

            if len(frac) > 1:
                if(any(i > j for i, j in zip(frac, frac[1:]))):
                    msgs.append(ERRORS["E060"])

            if len(temp) > 1:
                if(any(i > j for i, j in zip(temp, temp[1:]))):
                    msgs.append(ERRORS["E061"])

            # check if there are any duplicate fractions
            fractions = [c.fraction.value for c in self.cuts]
            if len(fractions) != len(set(fractions)):
                msgs.append(WARNINGS["W013"])

        return msgs
