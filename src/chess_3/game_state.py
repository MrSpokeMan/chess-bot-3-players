"""Pure data model for the game state.

GameState is the single source of truth. Renderers read it but never mutate it.
"""

from __future__ import annotations

import queue
from dataclasses import dataclass, field
from enum import Enum, auto

from chess_3.coords import Coord
from chess_3.piece import Piece


class SelectionPhase(Enum):
    """UI state machine for piece selection flow."""
    IDLE = auto()
    PIECE_SELECTED = auto()
    MOVE_PENDING = auto()


@dataclass
class GameState:
    """Pure data container for the game.

    Attributes:
        board: Maps Coord -> Piece. Empty squares have no entry.
        current_player: 0, 1, or 2 — whose turn it is.
        selection_phase: Current UI state.
        selected_coord: The coord of the currently selected piece, or None.
        legal_move_highlights: Coords where the selected piece can move.
        game_over: Whether the game has ended.
        winner: Player number of the winner, or None.
    """
    board: dict[Coord, Piece] = field(default_factory=dict)
    current_player: int = 0
    selection_phase: SelectionPhase = SelectionPhase.IDLE
    selected_coord: Coord | None = None
    legal_move_highlights: list[Coord] = field(default_factory=list)
    game_over: bool = False
    winner: int | None = None
    _result_queue: queue.Queue = field(  # type: ignore[type-arg]
        default_factory=queue.Queue,
        repr=False,
        compare=False,
    )
