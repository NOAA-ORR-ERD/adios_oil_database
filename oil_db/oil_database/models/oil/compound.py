"""
dataclass to store the compounds
"""
from dataclasses import dataclass, field

from ..common.utilities import dataclass_to_json, JSON_List

from ..common.measurement import MassFraction


@dataclass_to_json
@dataclass
class Compound:
    '''
        Some compounds that will be handled by this dataclass:
        - sulfur_mass_fraction: UnittedValue = None
        - carbon_mass_fraction: UnittedValue = None
        - hydrogen_mass_fraction: UnittedValue = None
        - mercaptan_sulfur_mass_fraction: UnittedValue = None
        - nitrogen_mass_fraction: UnittedValue = None
        - ccr_percent: UnittedValue = None  # conradson carbon residue
        - calcium_mass_fraction: UnittedValue = None
        - hydrogen_sulfide_concentration: UnittedValue = None
        - salt_content: UnittedValue = None
        - paraffin_volume_fraction: UnittedValue = None
        - naphthene_volume_fraction: UnittedValue = None
        - aromatic_volume_fraction: UnittedValue = None

        Note: are these going in the compound list?
        - total_acid_number: UnittedValue = None
        - reid_vapor_pressure: UnittedValue = None
    '''
    name: str = ""
    groups: list = field(default_factory=list)
    method: str = ""
    measurement: MassFraction = None


class CompoundList(JSON_List):
    item_type = Compound
