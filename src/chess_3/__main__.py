"""Entry point: python -m chess_3

Opens a pygame window and renders the static tri-hex board.
"""

from __future__ import annotations

from pathlib import Path

import pygame

from chess_3.coord_system import CoordSystem
from chess_3.coords import Coord
from chess_3.game_state import GameState
from chess_3.piece import Piece
from chess_3.piece_config import PieceConfig
from chess_3.renderers.board_renderer import BoardRenderer

WINDOW_WIDTH = 1440
WINDOW_HEIGHT = 900
FPS = 60


def _create_initial_state() -> GameState:
    state = GameState()
    config_path = Path(__file__).resolve().parent / "assets" / "pieces.toml"
    cfg = PieceConfig(config_path)

    major_order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for player in range(3):
        left_section = player * 2
        right_section = left_section + 1

        # Two 4-wide sections form one 8-wide player base.
        for idx, piece_type in enumerate(major_order):
            section = left_section if idx < 4 else right_section
            col = idx % 4
            back_rank = Coord(section, 0, col)
            pawn_rank = Coord(section, 1, col)

            state.board[back_rank] = Piece.from_config(piece_type, player, cfg.get(piece_type))
            state.board[pawn_rank] = Piece.from_config("pawn", player, cfg.get("pawn"))

    return state


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Chess 3-Player - Board Preview (Esc/Q quit, F11 fullscreen)")
    clock = pygame.time.Clock()

    coord_system = CoordSystem(WINDOW_WIDTH, WINDOW_HEIGHT)
    board_renderer = BoardRenderer(coord_system)
    game_state = _create_initial_state()
    fullscreen = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            elif event.type == pygame.WINDOWSIZECHANGED and not fullscreen:
                current = pygame.display.get_surface()
                if current is not None:
                    screen = current

        board_renderer.draw(screen, game_state)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
