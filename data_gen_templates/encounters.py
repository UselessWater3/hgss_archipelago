# data_gen_templates/encounters.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from collections.abc import Mapping, Sequence, Set
from dataclasses import dataclass, field
from os import access
from typing import Optional, Tuple

from . import VersionEnum

@dataclass(frozen=True)
class EncounterSlot:
    species: str
    accessibility: Sequence[str] = field(default_factory=list)
    version: Optional[str] = None

    def in_logic(self, version: int, in_logic_access: Set[str]) -> bool:
        return (self.version is None or self.version == ("hg" if version == VersionEnum.HEARTGOLD else "ss")) and (not self.accessibility or bool(set(self.accessibility) & in_logic_access))

@dataclass(frozen=True)
class EncounterData:
    id: int
    land: Sequence[EncounterSlot] = field(default_factory=list)
    water: Sequence[EncounterSlot] = field(default_factory=list)
    rock_smash: Sequence[EncounterSlot] = field(default_factory=list)

encounters: Mapping[str, EncounterData] = {
    # TEMPLATE: ENCOUNTERS
}

encounter_types: Sequence[str] = ["land", "water", "rock_smash"]

def encounter_string_to_key(s: str) -> Tuple[str, str, int]:
    i = s.rfind("_")
    j = s.rfind("_", 0, i)
    return s[:j], s[j + 1:i], int(s[i + 1:])
