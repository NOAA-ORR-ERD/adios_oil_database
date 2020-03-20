"""
Main class that represents an oil record.

This maps to the JSON used in the DB

Having a Python class makes it easier to write importing, validating etc, code.
"""

from ..common.utilities import dataclass_to_json, JSON_List

from .values import (UnittedValue,
                     DensityList,
                     ViscosityList,
                     DistCutsList)

from dataclasses import dataclass, field


@dataclass_to_json
@dataclass
class Sample:
    """
    represents the physical and chemical properties of particular sub sample.

    could be fresh oil, or weathered samples, or distillation cuts, or ...
    """
    # metadata:
    name: str = "Fresh Oil Sample"
    short_name: str = None
    fraction_weathered: float = None
    boiling_point_range: tuple = None

    pour_point: UnittedValue = None

    densities: DensityList = field(default_factory=DensityList)
    kvis: ViscosityList = field(default_factory=ViscosityList)
    dvis: ViscosityList = field(default_factory=ViscosityList)
    cuts: DistCutsList = field(default_factory=DistCutsList)
    # Assorted:

    sulfur_mass_fraction: UnittedValue = None

    # From Exxon Dist cut data
    cut_volume: UnittedValue = None
    carbon_mass_fraction: UnittedValue = None
    hydrogen_mass_fraction: UnittedValue = None
    total_acid_number: UnittedValue = None
    mercaptan_sulfur_mass_fraction: UnittedValue = None
    nitrogen_mass_fraction: UnittedValue = None
    ccr_percent: UnittedValue = None
    calcium_mass_fraction: UnittedValue = None
    reid_vapor_pressure: UnittedValue = None
    hydrogen_sulfide_concentration: UnittedValue = None
    salt_content: UnittedValue = None
    paraffin_volume_fraction: UnittedValue = None
    naphthene_volume_fraction: UnittedValue = None
    aromatic_volume_fraction: UnittedValue = None

    def __post_init__(self):
        if self.name is not None:
            if self.name.lower() == 'whole crude':
                self.name = 'Fresh Oil Sample'

        if self.short_name is None:
            if self.name.lower() == 'fresh oil sample':
                self.short_name = 'Fresh Oil'
            else:
                self.short_name = '{}...'.format(self.name[:12])


class SampleList(JSON_List):
    item_type = Sample
