"""Entry point: python -m chess_3

Opens a pygame window and renders the static tri-hex board.
"""

from __future__ import annotations

import pygame

from chess_3.coord_system import CoordSystem
from chess_3.renderers.board_renderer import BoardRenderer

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
FPS = 60


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess 3-Player - Board Preview (Esc/Q to quit)")
    clock = pygame.time.Clock()

    coord_system = CoordSystem()
    board_renderer = BoardRenderer(coord_system)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

        board_renderer.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
