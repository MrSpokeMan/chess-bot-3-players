import math
import random

import chess

# ==========================================
# Better Evaluation Function
# ==========================================
piece_values = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3.2,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}

# simple piece-square table (encourages center control)
center_bonus = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    1,
    2,
    2,
    2,
    2,
    1,
    0,
    0,
    1,
    2,
    3,
    3,
    2,
    1,
    0,
    0,
    1,
    2,
    3,
    3,
    2,
    1,
    0,
    0,
    1,
    2,
    2,
    2,
    2,
    1,
    0,
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]


def evaluate(board):
    if board.is_checkmate():
        return -1.0 if board.turn else 1.0

    score = 0.0

    # material
    for piece_type, val in piece_values.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * val
        score -= len(board.pieces(piece_type, chess.BLACK)) * val

    # center control
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            bonus = center_bonus[sq] * 0.05
            score += bonus if piece.color else -bonus

    # mobility
    mobility = len(list(board.legal_moves))
    score += 0.01 * mobility if board.turn else -0.01 * mobility

    return math.tanh(score / 10)


# ==========================================
# Move Ordering
# ==========================================
def order_moves(board):
    moves = list(board.legal_moves)
    scores = []

    for m in moves:
        s = 0
        if board.is_capture(m):
            s += 10
        if m.promotion:
            s += 8
        s += random.uniform(-0.05, 0.05)
        scores.append(s)

    return [m for _, m in sorted(zip(scores, moves), reverse=True)]


# ==========================================
# Alpha-Beta (slightly deeper)
# ==========================================
def alpha_beta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board)

    moves = order_moves(board)

    if maximizing:
        value = -1e9
        for move in moves:
            board.push(move)
            value = max(value, alpha_beta(board, depth - 1, alpha, beta, False))
            board.pop()
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = 1e9
        for move in moves:
            board.push(move)
            value = min(value, alpha_beta(board, depth - 1, alpha, beta, True))
            board.pop()
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


# ==========================================
# Stochastic Move Selection (IMPORTANT)
# ==========================================
def select_move(board, epsilon=0.2):
    moves = order_moves(board)

    # exploration
    if random.random() < epsilon:
        return random.choice(moves), 0

    best_move = None
    best_score = -1e9 if board.turn else 1e9

    for move in moves:
        board.push(move)
        score = alpha_beta(board, 3, -1e9, 1e9, not board.turn)
        board.pop()

        if board.turn:
            if score > best_score:
                best_score, best_move = score, move
        else:
            if score < best_score:
                best_score, best_move = score, move

    return best_move, best_score


# ==========================================
# Game Generation
# ==========================================
def generate_game(_):
    board = chess.Board()
    data = []

    while not board.is_game_over() and board.fullmove_number < 240:
        if board.can_claim_threefold_repetition():
            break

        move, score = select_move(board, epsilon=0.2)

        if move is None:
            move = random.choice(list(board.legal_moves))

        data.append((board.fen(), score))
        board.push(move)

    # reward shaping
    result = board.result()

    if result == "1-0":
        reward = 1.0
    elif result == "0-1":
        reward = -1.0
    else:
        print("To jest draw, i jest bardzo często")
        reward = -0.5

    return data, reward
