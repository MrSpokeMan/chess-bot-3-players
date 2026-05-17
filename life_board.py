from dataclasses import dataclass, replace as dc_replace
from typing import Optional

import chess

PIECE_STATS: dict[int, dict[str, int]] = {
    chess.PAWN:   {"life": 1, "strength": 1},
    chess.KNIGHT: {"life": 2, "strength": 2},
    chess.BISHOP: {"life": 3, "strength": 2},
    chess.ROOK:   {"life": 4, "strength": 3},
    chess.QUEEN:  {"life": 5, "strength": 5},
    chess.KING:   {"life": 99, "strength": 3},
}

# rook squares before/after castling: (from_sq, to_sq) keyed by king destination
_CASTLE_ROOK: dict[int, tuple[int, int]] = {
    chess.G1: (chess.H1, chess.F1),
    chess.C1: (chess.A1, chess.D1),
    chess.G8: (chess.H8, chess.F8),
    chess.C8: (chess.A8, chess.D8),
}


@dataclass
class PieceState:
    piece_id: int
    chess_piece: chess.Piece
    life: int
    max_life: int
    strength: int
    spawn_square: int


class LifeBoard:
    def __init__(self) -> None:
        self.board = chess.Board()
        self._states: dict[int, PieceState] = {}
        self._sq_to_id: dict[int, int] = {}
        self._queue: list[int] = []
        self._next_id = 0
        self._history: list[tuple] = []
        self._init_pieces()

    # ------------------------------------------------------------------
    # setup
    # ------------------------------------------------------------------

    def _alloc_id(self) -> int:
        pid = self._next_id
        self._next_id += 1
        return pid

    def _init_pieces(self) -> None:
        for sq in chess.SQUARES:
            piece = self.board.piece_at(sq)
            if piece:
                pid = self._alloc_id()
                stats = PIECE_STATS[piece.piece_type]
                self._states[pid] = PieceState(
                    piece_id=pid,
                    chess_piece=piece,
                    life=stats["life"],
                    max_life=stats["life"],
                    strength=stats["strength"],
                    spawn_square=sq,
                )
                self._sq_to_id[sq] = pid

    # ------------------------------------------------------------------
    # public API (mirrors chess.Board)
    # ------------------------------------------------------------------

    @property
    def turn(self) -> bool:
        return self.board.turn

    @property
    def legal_moves(self):
        return self.board.legal_moves

    def piece_at(self, square: int) -> Optional[chess.Piece]:
        return self.board.piece_at(square)

    def piece_state_at(self, square: int) -> Optional[PieceState]:
        pid = self._sq_to_id.get(square)
        return self._states.get(pid) if pid is not None else None

    def is_capture(self, move: chess.Move) -> bool:
        return self.board.is_capture(move)

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def result(self) -> str:
        return self.board.result()
    
    def outcome(self) -> Optional[chess.Outcome]:
        return self.board.outcome()
        
    @property
    def fullmove_number(self) -> int:
        return self.board.fullmove_number

    @property
    def respawn_queue(self) -> list[PieceState]:
        return [self._states[pid] for pid in self._queue]

    def reset(self) -> None:
        self.board.reset()
        self._states.clear()
        self._sq_to_id.clear()
        self._queue.clear()
        self._history.clear()
        self._next_id = 0
        self._init_pieces()

    def _snapshot(self) -> tuple:
        return (
            {pid: dc_replace(s) for pid, s in self._states.items()},
            self._sq_to_id.copy(),
            self._queue.copy(),
        )

    def pop(self) -> None:
        self.board.pop()
        self._states, self._sq_to_id, self._queue = self._history.pop()

    # ------------------------------------------------------------------
    # core: push with life mechanics
    # ------------------------------------------------------------------

    def push(self, move: chess.Move) -> None:
        self._history.append(self._snapshot())
        is_capture = self.board.is_capture(move)
        is_en_passant = self.board.is_en_passant(move)
        is_castling = self.board.is_castling(move)
        turn = self.board.turn

        if is_capture:
            target_sq = (
                move.to_square + (-8 if turn == chess.WHITE else 8)
                if is_en_passant
                else move.to_square
            )
            attacker_id = self._sq_to_id.get(move.from_square)
            target_id = self._sq_to_id.get(target_sq)

            self.board.push(move)

            if attacker_id is not None and target_id is not None:
                self._sq_to_id.pop(move.from_square, None)
                self._sq_to_id.pop(target_sq, None)
                self._sq_to_id[move.to_square] = attacker_id

                if move.promotion:
                    promoted = self.board.piece_at(move.to_square)
                    if promoted:
                        self._states[attacker_id].chess_piece = promoted

                target_state = self._states[target_id]
                target_state.life -= self._states[attacker_id].strength

                if target_state.life <= 0:
                    del self._states[target_id]
                else:
                    self._try_respawn(target_id)
        else:
            self.board.push(move)

            pid = self._sq_to_id.pop(move.from_square, None)
            if pid is not None:
                self._sq_to_id[move.to_square] = pid

                if move.promotion:
                    promoted = self.board.piece_at(move.to_square)
                    if promoted:
                        self._states[pid].chess_piece = promoted

                if is_castling:
                    rook_from, rook_to = _CASTLE_ROOK[move.to_square]
                    rook_id = self._sq_to_id.pop(rook_from, None)
                    if rook_id is not None:
                        self._sq_to_id[rook_to] = rook_id

        self._flush_queue()

    # ------------------------------------------------------------------
    # respawn helpers
    # ------------------------------------------------------------------

    def _place_piece(self, square: int, piece: chess.Piece) -> None:
        # board.set_piece_at() calls clear_stack() which wipes the undo history.
        # We preserve the stacks manually so push/pop stays functional.
        saved_moves = self.board.move_stack[:]
        saved_stack = self.board._stack[:]
        self.board.set_piece_at(square, piece)
        self.board.move_stack.extend(saved_moves)
        self.board._stack.extend(saved_stack)

    def _try_respawn(self, piece_id: int) -> None:
        state = self._states[piece_id]
        if self.board.piece_at(state.spawn_square) is None:
            self._place_piece(state.spawn_square, state.chess_piece)
            self._sq_to_id[state.spawn_square] = piece_id
        else:
            self._queue.append(piece_id)

    def _flush_queue(self) -> None:
        still_waiting: list[int] = []
        for piece_id in self._queue:
            state = self._states.get(piece_id)
            if state is None:
                continue
            if self.board.piece_at(state.spawn_square) is None:
                self._place_piece(state.spawn_square, state.chess_piece)
                self._sq_to_id[state.spawn_square] = piece_id
            else:
                still_waiting.append(piece_id)
        self._queue = still_waiting
