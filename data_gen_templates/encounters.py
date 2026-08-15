# data_gen_templates/encounters.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class EncounterSlot:
    species: str
    accessibility: Sequence[str] = field(default_factory=list)
    version: Optional[str] = None

@dataclass(frozen=True)
class EncounterData:
    id: int
    land: Sequence[EncounterSlot] = field(default_factory=list)
    water: Sequence[EncounterSlot] = field(default_factory=list)
    rock_smash: Sequence[EncounterSlot] = field(default_factory=list)

encounters: Mapping[str, EncounterData] = {
    # TEMPLATE: ENCOUNTERS
}

