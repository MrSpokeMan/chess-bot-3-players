import numpy as np
import torch

from life_board import LifeBoard

_PIECES = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]

# 25 channels:
#   0-11  : piece presence (one-hot per piece-type × color)
#   12-23 : life ratio (life/max_life) for matching piece channel, 0 if empty
#   24    : turn (+1 white, -1 black)


def board_to_tensor(life_board: LifeBoard) -> torch.Tensor:
    board = life_board.board
    tensor = np.zeros((25, 8, 8), dtype=np.float32)

    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            r, c = divmod(i, 8)
            ch = _PIECES.index(piece.symbol())
            tensor[ch][r][c] = 1.0

            state = life_board.piece_state_at(i)
            tensor[ch + 12][r][c] = (state.life / state.max_life) if state else 1.0

    tensor[24].fill(1.0 if board.turn else -1.0)
    return torch.from_numpy(tensor)
