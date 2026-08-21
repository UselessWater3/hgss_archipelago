# locations.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from BaseClasses import ItemClassification, Location, Region
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING

from .data import items as itemdata, locations as locationdata, regions as regiondata, trainers as trainerdata, species as speciesdata
from .options import PokemonHgssOptions, RemoteItems, Version

if TYPE_CHECKING:
    from . import PokemonHgssWorld

raw_id_to_const_name = { loc.get_raw_id():name for name, loc in locationdata.locations.items() }

@dataclass(frozen=True)
class LocationType:
    is_enabled: Callable[[PokemonHgssOptions], bool]
    should_be_added: Callable[[PokemonHgssOptions], bool] = lambda _ : True
    should_have_item: Callable[[PokemonHgssOptions], bool] = lambda _ : True

location_types: Mapping[str, LocationType] = {
    "overworld": LocationType(is_enabled = lambda opts : opts.overworlds.value == 1),
    "hidden": LocationType(is_enabled = lambda opts : opts.hiddens.value == 1),
    "hm": LocationType(is_enabled = lambda opts : opts.hms.value == 1),
    "badge": LocationType(is_enabled = lambda opts : opts.badges.value == 1),
    "key_item": LocationType(is_enabled = lambda opts : opts.key_items.value == 1),
    "key_item_hg": LocationType(
        is_enabled = lambda opts : opts.key_items.value == 1 and opts.version == Version.option_heartgold,
        should_be_added = lambda opts : opts.version == Version.option_heartgold,
    ),
    "key_item_ss": LocationType(
        is_enabled = lambda opts : opts.key_items.value == 1 and opts.version == Version.option_soulsilver,
        should_be_added = lambda opts : opts.version == Version.option_soulsilver,
    ),
    "npc_gift": LocationType(is_enabled = lambda opts : opts.npc_gifts.value == 1),
    "rod": LocationType(is_enabled = lambda opts : opts.rods.value == 1),
    "running_shoes": LocationType(is_enabled = lambda opts : opts.running_shoes.value == 1),
    "bicycle": LocationType(is_enabled = lambda opts : opts.bicycle.value == 1),
    "pokedex": LocationType(is_enabled = lambda opts : opts.pokedex.value == 1),
    "pokegear_card": LocationType(is_enabled = lambda opts : opts.pokegear_card.value == 1),
    "fly_location_kanto": LocationType(
        is_enabled = lambda opts : "kanto" in opts.randomize_fly_items,
        should_be_added = lambda opts : "kanto" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
        should_have_item = lambda opts : "kanto" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
    ),
    "fly_location_johto": LocationType(
        is_enabled = lambda opts : "johto" in opts.randomize_fly_items,
        should_be_added = lambda opts : "johto" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
        should_have_item = lambda opts : "johto" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
    ),
    "fly_location_silver_cave": LocationType(
        is_enabled = lambda opts : "mount_silver" in opts.randomize_fly_items,
        should_be_added = lambda opts : "mount_silver" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
        should_have_item = lambda opts : "mount_silver" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
    ),
    "fly_location_pokemon_league": LocationType(
        is_enabled = lambda opts : "pokemon_league" in opts.randomize_fly_items,
        should_be_added = lambda opts : "pokemon_league" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
        should_have_item = lambda opts : "pokemon_league" in opts.randomize_fly_items or opts.require_fly_items_for_flight.value == 1,
    ),
}

def get_parent_region(label: str, world: "PokemonHgssWorld") -> str | None:
    const_name = raw_id_to_const_name[world.location_name_to_id[label]]
    return locationdata.locations[const_name].parent_region

def remote_items_should_add(const_name: str, world: "PokemonHgssWorld") -> bool:
    if world.options.remote_items == RemoteItems.option_all:
        return True
    elif world.options.remote_items == RemoteItems.option_only_randomized_or_progression:
        orig_item = locationdata.locations[const_name].original_item
        if not isinstance(orig_item, str):
            return False
        if itemdata.items[orig_item].classification == ItemClassification.progression:
            return True
    return False

def is_location_in_world(label: str, world: "PokemonHgssWorld") -> bool:
    const_name = raw_id_to_const_name[world.location_name_to_id[label]]
    lt = location_types[locationdata.locations[const_name].type]
    if not lt.should_be_added(world.options):
        return False
    if lt.is_enabled(world.options) or const_name in world.required_locations:
        return True
    return remote_items_should_add(const_name, world)

def create_location_label_to_code_map() -> Dict[str, int]:
    id_map = {}
    id_map.update({v.label:v.get_raw_id() for v in locationdata.locations.values()})
    id_map.update({
        v.label:v.get_raw_id()
        for k, v in trainerdata.trainers.items()
        if not ((k.startswith("rival_") or k.startswith("partner_rival")) \
                and (k.endswith("cyndaquil") or k.endswith("totodile")))
    })
    id_map.update({"Pokedex - " + v.label:v.id | (locationdata.LocationTable.DEX << 16) for v in speciesdata.species.values()})
    return id_map

class PokemonHgssLocation(Location):
    game: str = "Pokemon HeartGold and SoulSilver"
    type: str
    default_item_id: int | None
    is_enabled: bool

    def __init__(
        self,
        player: int,
        name: str,
        type: str,
        address: int | None = None,
        parent: Region | None = None,
        default_item_id: int | None = None,
        is_enabled: bool = True,
    ) -> None:
        super().__init__(player, name, address, parent)
        self.default_item_id = default_item_id
        self.is_enabled = is_enabled
        self.type = type

def create_locations(world: "PokemonHgssWorld", regions: Mapping[str, Region]) -> None:
    for region_name, region_data in regiondata.regions.items():
        if region_name not in regions:
            continue
        region = regions[region_name]
        for name in region_data.locs:
            loc = locationdata.locations[name]
            lt = location_types[loc.type]
            is_enabled = lt.is_enabled(world.options)
            if not is_location_in_world(loc.label, world):
                continue
            if isinstance(loc.original_item, str):
                original_item = loc.original_item
            else:
                original_item = world.random.choice(loc.original_item)
            item = itemdata.items[original_item]
            isnt_event = remote_items_should_add(name, world)
            if is_enabled or isnt_event:
                address = loc.get_raw_id()
            else:
                address = None
            plat_loc = PokemonHgssLocation(
                world.player,
                loc.label,
                loc.type,
                address=address,
                parent=region,
                default_item_id=item.get_raw_id(),
                is_enabled=is_enabled)
            if not is_enabled:
                if isnt_event:
                    ap_item = world.create_item(item.label)
                else:
                    ap_item = world.create_event(item.label)
                plat_loc.place_locked_item(ap_item)
                plat_loc.show_in_spoiler = False
            region.locations.append(plat_loc)

    for name in world.trainersanity_trainers:
        tr_reg = regions[f"trainer_{name}"]
        if name.startswith("rival_") or name.startswith("partner_rival_"):
            name += "_chikorita"
        tr = trainerdata.trainers[name]
        original_item = world.random.choice(["star_piece", "nugget"])
        item = itemdata.items[original_item]
        address = tr.get_raw_id()
        plat_loc = PokemonHgssLocation(
            world.player,
            tr.label,
            "trainersanity",
            address=address,
            parent=tr_reg,
            default_item_id=item.get_raw_id(),
            is_enabled=True)
        tr_reg.locations.append(plat_loc)

    rgms = set(speciesdata.regional_mons)
    balls = sorted(world.item_name_groups["Balls"])
    dex_reg = regions["virt_dex"]
    national_dex_reg = regions["virt_national_dex"]
    for spec in world.dexsanity_specs:
        if spec in rgms:
            region = dex_reg
        else:
            region = national_dex_reg
        plat_loc = PokemonHgssLocation(
            world.player,
            "Pokedex - " + speciesdata.species[spec].label,
            "dexsanity",
            address=speciesdata.species[spec].id | (locationdata.LocationTable.DEX << 16),
            parent=region,
            default_item_id=world.item_name_to_id[world.random.choice(balls)],
            is_enabled=True)
        region.locations.append(plat_loc)

