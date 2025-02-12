"""
Special class to hold the Pseudo Components for the
SINTEF OSCAR OIl Weathering Model

These are included as a special  case, because they
cannot be computed from the other data measured and stored in this data model.

NOTE: Some of the components to fit elsewhere -- e.g.
Benzene

But it makes sense to keep these all together.

https://docs.google.com/spreadsheets/d/1F-kuIpoCkuZIntDiXxFFwgCQrmVKu5tJjk7bgm0ZQ6E/edit?usp=sharing

Here's the list

CHEM_NAME   FORMULA

C1-C4 gasses (dissolved in oil) C1-C4
C5-saturates (n-/iso-/cyclo)    C5-sat
C6-saturates (n-/iso-/cyclo)    C6-sat
C7-saturates (n-/iso-/cyclo)    C7-sat
C8-saturates (n-/iso-/cyclo)    C8-sat
C9-saturates (n-/iso-/cyclo)    C9-sat
Benzene Bezene
C1-Benzene (Toluene) et. B  C1-Ben
C2-Benzene (xylenes; using O-xylene)    C2-Ben
C3-Benzene  C3-Ben
C4 and C5 Benzenes  C4-Ben
C10-saturates (n-/iso-/cyclo)   C10-sat
C11-C12 (total sat + aro)   C11-C12
C13-C14 (total sat + aro)   C13-C14
C15-C16 (total sat + aro)   C15-C16
C17-C18 (total sat + aro)   C17-C18
C19-C20 (total sat + aro)   C19-C20
C21-C25 (total sat + aro)   C21-C22
C25+ (total)    C25+
Naphthalenes 1 (C0-C1-alkylated)    Napth.1
Naphthalenes 2 (C2-C3-alkylated)    Napth.2
PAH 1 (Medium soluble polyaromatic hydrocrbns (3 rings-non-alkyltd;<4 rings)    PAH-1
PAH 2 (Low soluble polyaromatic hydrocarbons (3 rings-alkylated; 4-5+ rings)    PAH-2
Phenols (C0-C4 alkylated)   Phenols
Unresolved Chromatographic Materials (UCM: C10 to C36)  UCM
"""

# Compound from elsewhere -- needs to be adapted for OSCAR PCs
@dataclass_to_json
@dataclass
class Compound:
    """
    Some compounds that will be handled by this dataclass:
    - sulfur_mass_fraction: MassFraction = None
    - carbon_mass_fraction: MassFraction = None
    - hydrogen_mass_fraction: MassFraction = None
    - mercaptan_sulfur_mass_fraction: MassFraction = None
    - nitrogen_mass_fraction: MassFraction = None
    - ccr_percent: MassFraction = None  # conradson carbon residue
    - calcium_mass_fraction: MassFraction = None
    - hydrogen_sulfide_concentration: MassFraction = None
    - salt_content: MassFraction = None
    - paraffin_volume_fraction: MassFraction = None
    - naphthene_volume_fraction: MassFraction = None
    - aromatic_volume_fraction: MassFraction = None
    """
    name: str = ""
    groups: list = field(default_factory=list)
    method: str = ""
    measurement: MassFraction = None
    comment: str = ""


class CompoundList(JSON_List):
    item_type = Compound

@dataclass_to_json
@dataclass
class OSCAR_PCs:
    """
    Holds the Pseudo Components for the

    SINTEF OSCAR OIl Weathering Model

    Reed, Mark and Daling, Per and Brakstad, Odd and Singsaas,
    Ivar and Faksness, Liv-Guri and Hetland, B. and Ekrol, N..
    Oscar2000: a multi-component 3-dimensional oil spill
    contingency and response model.
    Arctic and Marine Oilspill Program Technical Seminar. 2. 663-680.

    https://www.researchgate.net/publication/285051234_Oscar2000_a_multi-component_3-dimensional_oil_spill_contingency_and_response_model

    """
    method: str = None

    saturates: CompoundList = field(default_factory=CompoundList)
    aromatics: CompoundList = field(default_factory=CompoundList)
    GC_TPH: CompoundList = field(default_factory=CompoundList)
