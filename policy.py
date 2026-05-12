import math
import random

import chess

from life_board import LifeBoard
from utils import board_to_tensor

DEPTH = 3

piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3.2,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}

center_bonus = [
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
    0, 1, 2, 2, 2, 2, 1, 0,
    0, 1, 2, 3, 3, 2, 1, 0,
    0, 1, 2, 3, 3, 2, 1, 0,
    0, 1, 2, 2, 2, 2, 1, 0,
    0, 1, 1, 1, 1, 1, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0,
]


def evaluate(life_board: LifeBoard) -> float:
    board = life_board.board
    if board.is_checkmate():
        return -1.0 if board.turn else 1.0

    score = 0.0

    for piece_type, val in piece_values.items():
        for sq in board.pieces(piece_type, chess.WHITE):
            state = life_board.piece_state_at(sq)
            score += val * (state.life / state.max_life if state else 1.0)
        for sq in board.pieces(piece_type, chess.BLACK):
            state = life_board.piece_state_at(sq)
            score -= val * (state.life / state.max_life if state else 1.0)

    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            bonus = center_bonus[sq] * 0.05
            score += bonus if piece.color else -bonus

    mobility = len(list(board.legal_moves))
    score += 0.01 * mobility if board.turn else -0.01 * mobility

    return math.tanh(score / 10)


def order_moves(life_board: LifeBoard) -> list:
    moves = list(life_board.legal_moves)
    scores = []
    for m in moves:
        s = 0
        if life_board.is_capture(m):
            s += 10
        if m.promotion:
            s += 8
        s += random.uniform(-0.05, 0.05)
        scores.append(s)
    return [m for _, m in sorted(zip(scores, moves), reverse=True)]


def alpha_beta(life_board: LifeBoard, depth, alpha, beta, maximizing) -> float:
    if depth == 0 or life_board.is_game_over():
        return evaluate(life_board)

    moves = order_moves(life_board)

    if maximizing:
        value = -1e9
        for move in moves:
            life_board.push(move)
            value = max(value, alpha_beta(life_board, depth - 1, alpha, beta, False))
            life_board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = 1e9
        for move in moves:
            life_board.push(move)
            value = min(value, alpha_beta(life_board, depth - 1, alpha, beta, True))
            life_board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


def select_move(life_board: LifeBoard, epsilon=0.2):
    moves = order_moves(life_board)

    if random.random() < epsilon:
        return random.choice(moves), 0

    best_move = None
    best_score = -1e9 if life_board.turn else 1e9

    for move in moves:
        life_board.push(move)
        score = alpha_beta(life_board, DEPTH, -1e9, 1e9, not life_board.turn)
        life_board.pop()

        if life_board.turn:
            if score > best_score:
                best_score, best_move = score, move
        else:
            if score < best_score:
                best_score, best_move = score, move

    return best_move, best_score


def generate_game(_):
    life_board = LifeBoard()
    data = []

    while not life_board.is_game_over() and life_board.board.fullmove_number < 240:
        if life_board.board.can_claim_threefold_repetition():
            break

        move, score = select_move(life_board, epsilon=0.2)

        if move is None:
            moves = list(life_board.legal_moves)
            if not moves:
                break
            move = random.choice(moves)

        # store tensor as numpy so it survives multiprocessing pickle
        data.append((board_to_tensor(life_board).numpy(), score))
        life_board.push(move)

    result = life_board.board.result()

    if result == "1-0":
        reward = 1.0
    elif result == "0-1":
        reward = -1.0
    else:
        print("To jest draw, i jest bardzo często")
        reward = -0.5

    return data, reward
