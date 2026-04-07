"""Renders the static connected tri-hex board.

Draws six 4x4 sections that share one 60° lattice (single board, not six islands).
The board is pre-baked to a Surface at startup to avoid per-frame polygon computation.
"""

from __future__ import annotations

import pygame

from chess_3.coords import Coord
from chess_3.game_state import GameState
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
PLAYER_PIECE_COLORS = [
    (90, 130, 220),
    (210, 90, 90),
    (90, 170, 100),
]
PIECE_TEXT_COLOR = (245, 245, 245)
LABEL_TEXT_COLOR = (220, 220, 220)
HOVER_FILL_COLOR = (255, 255, 255, 55)
HOVER_OUTLINE_COLOR = (255, 255, 255, 150)
PIECE_GLYPHS = {
    "pawn": "P",
    "knight": "N",
    "bishop": "B",
    "rook": "R",
    "queen": "Q",
    "king": "K",
}


class BoardRenderer:
    """Draws the static board. Pre-bakes the board surface at construction time.

    Usage:
        renderer = BoardRenderer(coord_system)
        renderer.draw(screen)  # blits the pre-baked surface
    """

    def __init__(self, coord_system: CoordSystem) -> None:
        self._cs = coord_system
        self._board_surface: pygame.Surface | None = None
        self._surface_size: tuple[int, int] | None = None
        self._fx_surface: pygame.Surface | None = None

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

        self._draw_labels(surface)
        return surface

    def _draw_labels(self, surface: pygame.Surface) -> None:
        font_size = max(18, int(min(surface.get_width(), surface.get_height()) * 0.025))
        font = pygame.font.SysFont("dejavusansmono", font_size, bold=True)
        cx, cy = self._cs.board_center()

        for player in range(3):
            bx, by = self._cs.player_base_midpoint(player)
            vx = bx - cx
            vy = by - cy
            mag = (vx * vx + vy * vy) ** 0.5 or 1.0
            ux = vx / mag
            uy = vy / mag
            label_anchor = (
                bx + ux * self._cs.label_offset(),
                by + uy * self._cs.label_offset(),
            )

    def _draw_pieces(self, screen: pygame.Surface, game_state: GameState) -> None:
        min_side = min(screen.get_width(), screen.get_height())
        radius = max(10, int(min_side * 0.018))
        piece_font = pygame.font.SysFont("dejavusansmono", int(radius * 1.2), bold=True)

        for coord, piece in game_state.board.items():
            px, py = self._cs.coord_to_pixel(coord)
            color = PLAYER_PIECE_COLORS[piece.player]
            pygame.draw.circle(screen, color, (px, py), radius)
            pygame.draw.circle(screen, GRID_LINE_COLOR, (px, py), radius, 2)

            glyph = PIECE_GLYPHS.get(piece.piece_type, "?")
            glyph_surface = piece_font.render(glyph, True, PIECE_TEXT_COLOR)
            glyph_rect = glyph_surface.get_rect(center=(px, py))
            screen.blit(glyph_surface, glyph_rect)

    def _draw_hover_hint(self, screen: pygame.Surface, game_state: GameState) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = self._cs.pixel_to_coord(mouse_x, mouse_y)
        if hovered is None:
            return

        piece = game_state.board.get(hovered)
        if piece is None or piece.player != game_state.current_player:
            return

        if self._fx_surface is None:
            return

        self._fx_surface.fill((0, 0, 0, 0))
        corners = self._cs.cell_corners(hovered)
        pygame.draw.polygon(self._fx_surface, HOVER_FILL_COLOR, corners)
        pygame.draw.polygon(self._fx_surface, HOVER_OUTLINE_COLOR, corners, 2)
        screen.blit(self._fx_surface, (0, 0))

    def draw(self, screen: pygame.Surface, game_state: GameState) -> None:
        """Draw board background + labels + pieces."""
        current_size = (screen.get_width(), screen.get_height())
        if self._board_surface is None or self._surface_size != current_size:
            self._cs.set_viewport(*current_size)
            self._board_surface = self._build_board_surface(
                current_size[0], current_size[1]
            )
            self._fx_surface = pygame.Surface(current_size, pygame.SRCALPHA)
            self._surface_size = current_size
        screen.blit(self._board_surface, (0, 0))
        self._draw_hover_hint(screen, game_state)
        self._draw_pieces(screen, game_state)
