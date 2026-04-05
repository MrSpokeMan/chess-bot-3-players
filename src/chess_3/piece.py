"""Piece data model — runtime state for a single piece on the board."""

from __future__ import annotations

from dataclasses import dataclass

from chess_3.piece_config import PieceStats


@dataclass
class Piece:
    """A piece on the board with runtime state.

    Attributes:
        piece_type: One of "pawn", "knight", "bishop", "rook", "queen", "king"
        player: 0, 1, or 2
        stats: Immutable reference to config-loaded stats
        current_life: Starts at stats.life, decremented on hits
    """
    piece_type: str
    player: int
    stats: PieceStats
    current_life: int

    @staticmethod
    def from_config(piece_type: str, player: int, stats: PieceStats) -> Piece:
        """Create a piece at full health from config stats."""
        return Piece(
            piece_type=piece_type,
            player=player,
            stats=stats,
            current_life=stats.life,
        )
