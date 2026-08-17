# data_gen_templates/__init__.py
#
# Copyright (C) 2025-2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from collections.abc import Mapping
from enum import IntEnum, StrEnum

class Hm(StrEnum):
    # TEMPLATE: HMS

    def badge_item(self) -> str | None:
        match self:
            # TEMPLATE: HM_BADGE_ITEMS
            case _: return None

    def tmhm_id(self) -> int:
        match self:
            # TEMPLATE: HM_TMHM_IDS
            case _: return 0 # TEMPLATE: DELETE

AP_STRUCT_ADDRESS: Mapping[str, int] = {
    # TEMPLATE: AP_STRUCT_ADDRESS
}

class VersionEnum(IntEnum):
    HEARTGOLD = 0
    SOULSILVER = 1

tm_moves: Mapping[int, str] = {
    # TEMPLATE: TM_MOVES
}
