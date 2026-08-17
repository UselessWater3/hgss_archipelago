# regions.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from BaseClasses import Region
from collections.abc import Callable, Mapping, MutableSet, Sequence, Set
from dataclasses import dataclass
from typing import Tuple, TYPE_CHECKING

from .options import PokemonHgssOptions

from .data import regions as regiondata
from .data.encounters import EncounterSlot, encounters
from .data.trainers import trainer_party_supporting_starters
from .locations import PokemonHgssLocation

if TYPE_CHECKING:
    from . import PokemonHgssWorld

def is_region_enabled(region: str | None, opts: PokemonHgssOptions) -> bool:
    return True

def is_event_region_enabled(event: str, opts: PokemonHgssOptions) -> bool:
    return is_region_enabled(regiondata.event_region_map[event], opts)

def create_regions(world: "PokemonHgssWorld") -> Tuple[Mapping[str, Region], Set[str]]:
    regions: Mapping[str, Region] = {}
    trainers: Set[str] = set()
    connections: Sequence[Tuple[str, str, str]] = []
    version = world.options.version.value
    enc_mthds = world.options.in_logic_encounters.methods()

    def setup_wild_regions(parent_region: Region, wild_region_data: regiondata.RegionData) -> None:
        enc_key = wild_region_data.encounters
        if enc_key is None:
            return
        encs = encounters[enc_key]
        for type in wild_region_data.accessible_encounters:
            name = f"{enc_key}_{type}"
            e: Sequence[EncounterSlot] = getattr(encs, type)
            if not e:
                continue
            if name not in regions:
                wild_region = Region(name, world.player, world.multiworld)
                regions[name] = wild_region
                if type == "rock_smash" and type not in world.options.in_logic_encounters.methods():
                    continue

                for i, slot in enumerate(e):
                    if not slot.in_logic(version, enc_mthds):
                        continue
                    loc_name = f"{enc_key}_{type}_{i + 1}"
                    location = PokemonHgssLocation(
                        world.player,
                        loc_name,
                        "mon_event",
                        parent=wild_region,
                    )
                    location.show_in_spoiler = False
                    wild_region.locations.append(location)
            else:
                wild_region = regions[name]
            parent_region.connect(wild_region, f"{parent_region.name} -> {name}")

    def setup_trainer_region(parent_region: Region, trainer: str) -> None:
        trainers.add(trainer)
        trainer_region = Region(f"trainer_{trainer}", world.player, world.multiworld)
        regions[f"trainer_{trainer}"] = trainer_region
        parent_region.connect(trainer_region, f"{parent_region.name} -> trainer_{trainer}")
        for i in range(len(trainer_party_supporting_starters(trainer))):
            location = PokemonHgssLocation(
                world.player,
                f"{trainer}_party_{i + 1}",
                "see_mon_event",
                parent=trainer_region
            )
            location.show_in_spoiler = False
            trainer_region.locations.append(location)


    ignored_regions: MutableSet[str] = set()
    for region_name, region_data in regiondata.regions.items():
        if not is_region_enabled(region_name, world.options):
            ignored_regions.add(region_name)
            continue
        new_region = Region(region_name, world.player, world.multiworld)

        regions[region_name] = new_region

        for event in region_data.events:
            event_loc = PokemonHgssLocation(
                world.player,
                event,
                "event",
                parent=new_region)
            event_loc.show_in_spoiler = False
            event_loc.place_locked_item(world.create_event(event))
            new_region.locations.append(event_loc)

        setup_wild_regions(new_region, region_data)

        for trainer in region_data.trainers:
            setup_trainer_region(new_region, trainer)

        for region_exit in region_data.exits:
            connections.append((f"{region_name} -> {region_exit}", region_name, region_exit))

    for name, source, dest in connections:
        if dest in ignored_regions:
            continue
        regions[source].connect(regions[dest], name)

    return (regions, trainers)

