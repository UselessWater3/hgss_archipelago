# rom/eventdata.py
#
# Copyright (C) 2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from collections.abc import Mapping, MutableSequence, Sequence
from dataclasses import dataclass, astuple, fields
from struct import pack, unpack_from
from typing import Any, Literal, Tuple

from ..apnds.narc import Narc

MOSSY_ROCK_GFX = 1050
ICY_ROCK_GFX = 1051

EVO_ROCK_KANTO = 1
EVO_ROCK_JOHTO = 2

# kanto/johto, events, type, x, z, y
EVO_ROCK_INFO: Sequence[Tuple[int, int, Literal["mossy"] | Literal["icy"], int, int, int]] = [
    (EVO_ROCK_KANTO, 143, "mossy", 22, 54, 0),
    (EVO_ROCK_JOHTO, 114, "mossy", 31, 13, 0),
    (EVO_ROCK_KANTO, 410, "icy", 44, 16, 0),
    (EVO_ROCK_JOHTO, 117, "icy", 45, 17, 0),
]

def generate_add_rock_patch(which: Literal["mossy"] | Literal["icy"], x: int, z: int, y: int) -> Tuple[str, Any]:
    return (
        "add_obj_event_at_end",
        {
            "graphics_id": MOSSY_ROCK_GFX if which == "mossy" else ICY_ROCK_GFX,
            "movement_type": 0,
            "trainer_type": 0,
            "flag": 0,
            "script": 2085 if which == "mossy" else 2086,
            "initial_dir": 0,
            "data_0": 0,
            "data_1": 0,
            "data_2": 0,
            "movement_range_x": 0,
            "movement_range_z": 0,
            "x": x,
            "z": z,
            "y": y,
        },
    )

@dataclass
class BgEvent:
    script: int
    type: int
    x: int
    z: int
    y: int
    player_facing_dir: int

    @staticmethod
    def from_bytes(data: bytes, offset: int) -> "BgEvent":
        return BgEvent(*unpack_from("<2H3iH", data, offset))

    def to_bytes(self) -> bytes:
        return pack("<2H3iH2x", *astuple(self))

@dataclass
class ObjectEvent:
    local_id: int
    graphics_id: int
    movement_type: int
    trainer_type: int
    flag: int
    script: int
    initial_dir: int
    data_0: int
    data_1: int
    data_2: int
    movement_range_x: int
    movement_range_z: int
    x: int
    z: int
    y: int

    @staticmethod
    def from_bytes(data: bytes, offset: int) -> "ObjectEvent":
        return ObjectEvent(*unpack_from("<6Hh3H2h2Hi", data, offset))

    def to_bytes(self) -> bytes:
        return pack("<6Hh3H2h2Hi", *astuple(self))

@dataclass
class WarpEvent:
    x: int
    z: int
    dest_header_id: int
    dest_warp_id: int
    y: int

    @staticmethod
    def from_bytes(data: bytes, offset: int) -> "WarpEvent":
        return WarpEvent(*unpack_from("<4HI", data, offset))

    def to_bytes(self) -> bytes:
        return pack("<4HI", *astuple(self))

@dataclass
class CoordEvent:
    script: int
    x: int
    z: int
    width: int
    length: int
    y: int
    value: int
    var: int
    
    @staticmethod
    def from_bytes(data: bytes, offset: int) -> "CoordEvent":
        return CoordEvent(*unpack_from("<H2h5H", data, offset))

    def to_bytes(self) -> bytes:
        return pack("<H2h5H", *astuple(self))

@dataclass
class Events:
    bg_events: MutableSequence[BgEvent]
    object_events: MutableSequence[ObjectEvent]
    warp_events: MutableSequence[WarpEvent]
    coord_events: MutableSequence[CoordEvent]

    @staticmethod
    def from_bytes(data: bytes) -> "Events":
        offset = 0
        def get_events(clas, b_len: int):
            nonlocal offset
            num = int.from_bytes(data[offset:offset + 4], 'little')
            offset += 4
            ret = [clas.from_bytes(data, offset + b_len * i) for i in range(num)]
            offset += b_len * num
            return ret

        return Events(*(
            get_events(clas, b_len)
            for clas, b_len in [(BgEvent, 20), (ObjectEvent, 32), (WarpEvent, 12), (CoordEvent, 16)]
        ))

    def to_bytes(self) -> bytes:
        return b''.join(
            bts
            for field in fields(self)
            for bts in [len(getattr(self, field.name)).to_bytes(4, 'little'), *(v.to_bytes() for v in getattr(self, field.name))]
        )

def patch_events(events_data: bytes, patch_info: Mapping[str, Sequence[Tuple[str, Any]]]) -> bytes:
    narc = Narc.from_bytes(events_data)

    def replace_obj_field(obj: ObjectEvent, new_fields: Mapping[str, int]) -> None:
        for field, val in new_fields.items():
            setattr(obj, field, val)

    for idx_str, patches in patch_info.items():
        events = Events.from_bytes(narc.files[int(idx_str)])
        for patch, patch_data in patches:
            match patch:
                case "remove_objs_by_graphics_id":
                    events.object_events = [e for e in events.object_events if e.graphics_id != patch_data or e.script == 0xFFFF]
                case "replace_obj_fields_by_graphics_id":
                    for e in events.object_events:
                        if e.graphics_id == patch_data[0] and e.script != 0xFFFF:
                            replace_obj_field(e, patch_data[1])
                case "remove_objs_by_data_0":
                    events.object_events = [e for e in events.object_events if e.data_0 != patch_data or e.script == 0xFFFF]
                case "replace_obj_fields_by_data_0":
                    for e in events.object_events:
                        if e.data_0 == patch_data[0] and e.script != 0xFFFF:
                            replace_obj_field(e, patch_data[1])
                case "replace_obj_fields_by_local_id":
                    for e in events.object_events:
                        if e.local_id == patch_data[0] and e.script != 0xFFFF:
                            replace_obj_field(e, patch_data[1])
                case "add_obj_event_at_end":
                    if "local_id" not in patch_data:
                        maxv = max(v.local_id for v in events.object_events if v.local_id < 200 and v.script != 0xFFFF)
                        if maxv == 199:
                            raise ValueError("could not generate appropriate local id for added event")
                        patch_data["local_id"] = maxv + 1
                    events.object_events.append(ObjectEvent(**patch_data))
                case "translate_objs_by_graphics_id":
                    for e in events.object_events:
                        if e.graphics_id == patch_data[0] and e.script != 0xFFFF:
                            e.x += patch_data[1][0];
                            e.z += patch_data[1][1];
                case "translate_objs_by_local_id":
                    for e in events.object_events:
                        if e.local_id == patch_data[0] and e.script != 0xFFFF:
                            e.x += patch_data[1][0];
                            e.z += patch_data[1][1];
                case "translate_aliases_by_local_id":
                    for e in events.object_events:
                        if e.local_id == patch_data[0] and e.script == 0xFFFF:
                            e.x += patch_data[1][0];
                            e.z += patch_data[1][1];
                case _:
                    raise ValueError(f"unsupported events patch {patch}")
        narc.files[int(idx_str)] = events.to_bytes()

    return narc.to_bytes()

