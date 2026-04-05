"""Canonical coordinate type for the tri-hex board.

Each cell is identified by (section, row, col) where:
- section: 0–5 (six sections of the hexagonal board, 60° apart)
- row: 0–3 (0 = section's back rank)
- col: 0–3 (left to right from section's perspective)

Total: 6 × 4 × 4 = 96 squares.

This is a frozen dataclass so it can be used as a dict key.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Coord:
    section: int  # 0–5
    row: int      # 0–3
    col: int      # 0–3

    def __post_init__(self) -> None:
        if self.section not in range(6):
            raise ValueError(f"section must be 0–5, got {self.section}")
        if not (0 <= self.row <= 3):
            raise ValueError(f"row must be 0–3, got {self.row}")
        if not (0 <= self.col <= 3):
            raise ValueError(f"col must be 0–3, got {self.col}")

    def __str__(self) -> str:
        return f"s{self.section}r{self.row}c{self.col}"

    @staticmethod
    def from_str(s: str) -> Coord:
        """Parse 's0r3c2' -> Coord(0, 3, 2)."""
        parts = s[1:].split("r")
        sec = int(parts[0])
        r_and_c = parts[1].split("c")
        return Coord(sec, int(r_and_c[0]), int(r_and_c[1]))
