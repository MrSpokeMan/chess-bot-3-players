"""Renders the static connected tri-hex board.

Draws six 4x4 sections that share one 60° lattice (single board, not six islands).
The board is pre-baked to a Surface at startup to avoid per-frame polygon computation.
"""

from __future__ import annotations

import pygame

from chess_3.coords import Coord
from chess_3.coord_system import (
    CoordSystem,
    ROWS_PER_SECTION,
    COLS_PER_SECTION,
)

# Colors
LIGHT_SQUARE = (240, 217, 181)   # warm cream
DARK_SQUARE = (181, 136, 99)     # warm brown
# Six section tints — pairs of sections per player (sections 0&1, 2&3, 4&5)
SECTION_TINTS = [
    (200, 200, 255, 40),   # S0: blue (Player 0)
    (200, 200, 255, 60),   # S1: blue deeper (Player 0)
    (255, 200, 200, 40),   # S2: red (Player 1)
    (255, 200, 200, 60),   # S3: red deeper (Player 1)
    (200, 255, 200, 40),   # S4: green (Player 2)
    (200, 255, 200, 60),   # S5: green deeper (Player 2)
]
GRID_LINE_COLOR = (80, 80, 80)
BACKGROUND_COLOR = (30, 30, 30)


class BoardRenderer:
    """Draws the static board. Pre-bakes the board surface at construction time.

    Usage:
        renderer = BoardRenderer(coord_system)
        renderer.draw(screen)  # blits the pre-baked surface
    """

    def __init__(self, coord_system: CoordSystem) -> None:
        self._cs = coord_system
        self._board_surface: pygame.Surface | None = None

    def _build_board_surface(self, width: int, height: int) -> pygame.Surface:
        """Pre-bake the entire board to a surface. Called once at first draw."""
        surface = pygame.Surface((width, height))
        surface.fill(BACKGROUND_COLOR)

        for s in range(6):
            tint_surface = pygame.Surface((width, height), pygame.SRCALPHA)

            for row in range(ROWS_PER_SECTION):
                for col in range(COLS_PER_SECTION):
                    coord = Coord(s, row, col)
                    corners = self._cs.cell_corners(coord)

                    # Alternating square colors
                    is_light = (row + col) % 2 == 0
                    color = LIGHT_SQUARE if is_light else DARK_SQUARE

                    # Draw filled square
                    pygame.draw.polygon(surface, color, corners)
                    # Draw grid outline
                    pygame.draw.polygon(surface, GRID_LINE_COLOR, corners, 1)

            # Apply section tint overlay
            for row in range(ROWS_PER_SECTION):
                for col in range(COLS_PER_SECTION):
                    coord = Coord(s, row, col)
                    corners = self._cs.cell_corners(coord)
                    pygame.draw.polygon(tint_surface, SECTION_TINTS[s], corners)

            surface.blit(tint_surface, (0, 0))

        return surface

    def draw(self, screen: pygame.Surface) -> None:
        """Blit the pre-baked board surface onto the screen."""
        if self._board_surface is None:
            self._board_surface = self._build_board_surface(
                screen.get_width(), screen.get_height()
            )
        screen.blit(self._board_surface, (0, 0))
