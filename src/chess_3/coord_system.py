"""Coordinate system for the tri-hex board.

Owns all pixel <-> board coordinate conversion.
All hit-testing MUST go through pixel_to_coord — never use pygame.Rect.collidepoint
on rotated sections (it only works for axis-aligned rectangles).

Board geometry (locked 2026-04-05):
- 6 sections × 4×4 = 96 squares total
- Sections numbered 0–5, each rotated 60° clockwise from the previous
- Section 0 at top, sections proceed clockwise
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from chess_3.coords import Coord

# Board layout constants — confirmed geometry, do not change without updating STATE.md
CELL_SIZE = 56        # pixels per cell side
BOARD_CENTER = (640, 400)  # pixel center of the full board

# Distance from board center to each section's origin (center of its 4×4 grid)
_RADIUS = 190  # pixels

# Section origins and rotation angles — 6 sections at 60° intervals, starting from top
S_ROTATIONS: list[float] = [0.0, 60.0, 120.0, 180.0, 240.0, 300.0]

S_ORIGINS: list[tuple[float, float]] = [
    (
        BOARD_CENTER[0] + _RADIUS * math.sin(math.radians(angle)),
        BOARD_CENTER[1] - _RADIUS * math.cos(math.radians(angle)),
    )
    for angle in S_ROTATIONS
]

# Grid dimensions per section (locked geometry)
ROWS_PER_SECTION = 4
COLS_PER_SECTION = 4


class CoordSystem:
    """Converts between board coordinates and pixel positions.

    All rendering and hit-testing should use this class.
    """

    def coord_to_pixel(self, coord: Coord) -> tuple[int, int]:
        """Return the center pixel (x, y) of a board cell."""
        ox, oy = S_ORIGINS[coord.section]
        angle = math.radians(S_ROTATIONS[coord.section])

        # Local offset from section center (before rotation)
        lx = (coord.col - (COLS_PER_SECTION - 1) / 2) * CELL_SIZE
        ly = (coord.row - (ROWS_PER_SECTION - 1) / 2) * CELL_SIZE

        # Rotate around section origin
        rx = lx * math.cos(angle) - ly * math.sin(angle)
        ry = lx * math.sin(angle) + ly * math.cos(angle)

        return int(ox + rx), int(oy + ry)

    def pixel_to_coord(self, px: int, py: int) -> Coord | None:
        """Find the board cell nearest to a pixel, or None if outside all sections.

        Uses inverse rotation per section and grid snapping.
        Never use pygame.Rect.collidepoint for this — it fails on rotated sections.
        """
        best_dist = float("inf")
        best_coord: Coord | None = None

        for sec in range(6):
            ox, oy = S_ORIGINS[sec]
            angle = math.radians(-S_ROTATIONS[sec])  # inverse rotation

            dx, dy = px - ox, py - oy
            lx = dx * math.cos(angle) - dy * math.sin(angle)
            ly = dx * math.sin(angle) + dy * math.cos(angle)

            # Convert to grid coordinates
            col_f = lx / CELL_SIZE + (COLS_PER_SECTION - 1) / 2
            row_f = ly / CELL_SIZE + (ROWS_PER_SECTION - 1) / 2

            # Check bounds
            if not (-0.5 <= col_f < COLS_PER_SECTION + 0.5 and -0.5 <= row_f < ROWS_PER_SECTION + 0.5):
                continue

            # Snap to nearest cell
            col_i = int(round(col_f))
            row_i = int(round(row_f))

            # Clamp to valid range
            col_i = max(0, min(COLS_PER_SECTION - 1, col_i))
            row_i = max(0, min(ROWS_PER_SECTION - 1, row_i))

            # Distance from snapped cell center (in grid units)
            dist = (col_f - col_i) ** 2 + (row_f - row_i) ** 2

            if dist < best_dist:
                best_dist = dist
                best_coord = Coord(sec, row_i, col_i)

        # Reject if too far from any cell center (more than half a cell away)
        if best_dist > 0.5:
            return None

        return best_coord
