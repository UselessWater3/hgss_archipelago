# rom/encounterdata.py
#
# Copyright (C) 2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from collections.abc import Mapping, MutableSequence, Sequence
from dataclasses import dataclass, astuple
from struct import pack, unpack_from

from ..apnds.narc import Narc

@dataclass
class EncounterSlot:
    min_level: int
    max_level: int
    species: int

    @staticmethod
    def from_bytes(data: bytes, offset: int) -> "EncounterSlot":
        return EncounterSlot(*unpack_from("<2BH", data, offset))

    def to_bytes(self) -> bytes:
        return pack("<2BH", *astuple(self))

@dataclass
class LandEncounters:
    levels: MutableSequence[int]
    species_morning: MutableSequence[int]
    species_day: MutableSequence[int]
    species_night: MutableSequence[int]

    @staticmethod
    def from_bytes(data: bytes, offset: int) -> "LandEncounters":
        out = unpack_from("<12B36H", data, offset)
        return LandEncounters(*(list(out[i:i + 12]) for i in range(0, 48, 12)))

    def to_bytes(self) -> bytes:
        return pack("<12B36H", *(v for l in astuple(self) for v in l))

@dataclass
class Encounters:
    encrates: MutableSequence[int]
    land_encs: LandEncounters
    hoenn_encs: MutableSequence[int]
    sinnoh_encs: MutableSequence[int]
    surf_slots: MutableSequence[EncounterSlot]
    rock_smash_slots: MutableSequence[EncounterSlot]
    old_rod_slots: MutableSequence[EncounterSlot]
    good_rod_slots: MutableSequence[EncounterSlot]
    super_rod_slots: MutableSequence[EncounterSlot]
    land_swarm: int
    surf_swarm: int
    night_fish: int
    fish_swarm: int

    @staticmethod
    def from_bytes(data: bytes) -> "Encounters":
        return Encounters(
            list(unpack_from("<6B", data)),
            LandEncounters.from_bytes(data, 8),
            list(unpack_from("<2H", data, 92)),
            list(unpack_from("<2H", data, 96)),
            list(EncounterSlot.from_bytes(data, 100 + i) for i in range(0, 20, 4)),
            list(EncounterSlot.from_bytes(data, 120 + i) for i in range(0, 8, 4)),
            list(EncounterSlot.from_bytes(data, 128 + i) for i in range(0, 20, 4)),
            list(EncounterSlot.from_bytes(data, 148 + i) for i in range(0, 20, 4)),
            list(EncounterSlot.from_bytes(data, 168 + i) for i in range(0, 20, 4)),
            *unpack_from("<4H", data, 188),
        )

    def to_bytes(self) -> bytes:
        return b''.join((
            pack("<6B2x", *self.encrates),
            self.land_encs.to_bytes(),
            pack("<2H", *self.hoenn_encs),
            pack("<2H", *self.sinnoh_encs),
            *(v.to_bytes() for v in self.surf_slots),
            *(v.to_bytes() for v in self.rock_smash_slots),
            *(v.to_bytes() for v in self.old_rod_slots),
            *(v.to_bytes() for v in self.good_rod_slots),
            *(v.to_bytes() for v in self.super_rod_slots),
            pack("<4H", self.land_swarm, self.surf_swarm, self.night_fish, self.fish_swarm),
        ))

def patch_encounters(encounter_data: bytes, patch_info: Mapping[str, Mapping[str, Sequence[Sequence[int]]]]) -> bytes:
    narc = Narc.from_bytes(encounter_data)
    for id_str, table_maps in patch_info.items():
        id = int(id_str)
        data = Encounters.from_bytes(narc.files[id])
        for table, maps in table_maps.items():
            mp = {v[0]:v[1] for v in maps}
            match table:
                case "land":
                    for time in ["morning", "day", "night"]:
                        e = getattr(data.land_encs, "species_" + time)
                        for i, v in enumerate(e):
                            if v in mp:
                                e[i] = mp[v]
                    for sound in ["hoenn", "sinnoh"]:
                        e = getattr(data, sound + "_encs")
                        for i, v in enumerate(e):
                            if v in mp:
                                e[i] = mp[v]
                    if data.land_swarm in mp:
                        data.land_swarm = mp[data.land_swarm]
                case "water":
                    for tbl in ["surf", "old_rod", "good_rod", "super_rod"]:
                        e = getattr(data, tbl + "_slots")
                        for i, v in enumerate(e):
                            if v.species in mp:
                                v.species = mp[v.species]
                    for k in ["surf_swarm", "night_fish", "fish_swarm"]:
                        e = getattr(data, k)
                        if e in mp:
                            setattr(data, k, mp[e])
                case "rock_smash":
                    e = data.rock_smash_slots
                    for i, v in enumerate(e):
                        if v.species in mp:
                            v.species = mp[v.species]
        narc.files[id] = data.to_bytes()
    return narc.to_bytes()
