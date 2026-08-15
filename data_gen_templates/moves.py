# data_gen_templates/moves.py
#
# Copyright (C) 2026 James Petersen <m@jamespetersen.ca>
# Licensed under MIT. See LICENSE

from collections.abc import Mapping
from dataclasses import dataclass

from .species import PokemonType

@dataclass(frozen=True)
class Move:
    id: int
    type: PokemonType
    pp: int
    priority: int = 0
    accuracy: int = 100

moves: Mapping[str, Move] = {
    # TEMPLATE: MOVES
}
