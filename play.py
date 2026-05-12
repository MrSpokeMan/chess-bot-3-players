import tkinter as tk
from tkinter import messagebox

import chess
import torch

from life_board import LifeBoard
from utils import board_to_tensor
from model import ChessNet


# ==========================================
# AI
# ==========================================
class AIPlayer:
    def __init__(self, model_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ChessNet().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()

    def get_best_move(self, life_board):
        best_move = None
        board = life_board.board
        best_eval = 1e9 if board.turn == chess.BLACK else -1e9

        for move in board.legal_moves:
            life_board.push(move)
            tensor = board_to_tensor(life_board).unsqueeze(0).to(self.device)

            with torch.no_grad():
                val = self.model(tensor).item()

            life_board.pop()

            if board.turn == chess.WHITE:
                if val > best_eval:
                    best_eval, best_move = val, move
            else:
                if val < best_eval:
                    best_eval, best_move = val, move

        return best_move


# ==========================================
# GUI
# ==========================================
class ChessGUI:
    CELL = 60

    def __init__(self, root, ai):
        self.root = root
        self.ai = ai
        self.life_board = LifeBoard()

        self.selected_square = None
        self.last_move = None

        self.bg = "#202124"
        self.light = "#f0d9b5"
        self.dark = "#b58863"
        self.highlight = "#f6f669"
        self.arrow_color = "#4aa3ff"

        root.configure(bg=self.bg)

        frame = tk.Frame(root, bg=self.bg)
        frame.pack(padx=20, pady=20)

        size = self.CELL * 8
        self.canvas = tk.Canvas(
            frame, width=size, height=size, bg=self.bg, highlightthickness=0
        )
        self.canvas.grid(row=0, column=1)

        self.left_panel = tk.Frame(frame, bg=self.bg, width=120)
        self.left_panel.grid(row=0, column=0, padx=10, sticky="n")

        self.right_panel = tk.Frame(frame, bg=self.bg, width=120)
        self.right_panel.grid(row=0, column=2, padx=10, sticky="n")

        tk.Label(
            self.left_panel, text="White queue", fg="#aaa", bg=self.bg,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        self.white_queue_label = tk.Label(
            self.left_panel, text="", fg="white", bg=self.bg, font=("Arial", 20),
            wraplength=110, justify="left",
        )
        self.white_queue_label.pack(anchor="w")

        tk.Label(
            self.right_panel, text="Black queue", fg="#aaa", bg=self.bg,
            font=("Arial", 10, "bold"),
        ).pack(anchor="w")
        self.black_queue_label = tk.Label(
            self.right_panel, text="", fg="white", bg=self.bg, font=("Arial", 20),
            wraplength=110, justify="left",
        )
        self.black_queue_label.pack(anchor="w")

        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()
        self.update_queue_display()

    # ------------------------------------------------------------------
    # drawing
    # ------------------------------------------------------------------

    def draw_board(self):
        self.canvas.delete("all")
        cell = self.CELL

        for r in range(8):
            for c in range(8):
                x1, y1 = c * cell, (7 - r) * cell
                x2, y2 = x1 + cell, y1 + cell
                sq = chess.square(c, r)

                color = self.light if (r + c) % 2 == 0 else self.dark
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.life_board.piece_at(sq)
                if piece:
                    self.canvas.create_text(
                        x1 + cell // 2,
                        y1 + cell // 2,
                        text=piece.unicode_symbol(),
                        font=("Segoe UI Symbol", 36),
                        fill="#111" if piece.color == chess.WHITE else "#000",
                    )
                    self._draw_life_bar(x1, y1, x2, y2, sq, piece)

        self.draw_last_move()
        self.draw_arrow(self.last_move)

    def _draw_life_bar(self, x1, y1, x2, y2, sq, piece):
        if piece.piece_type == chess.KING:
            return

        state = self.life_board.piece_state_at(sq)
        if state is None or state.max_life <= 1:
            return

        ratio = state.life / state.max_life
        bar_color = (
            "#4caf50" if ratio > 0.6
            else "#ff9800" if ratio > 0.3
            else "#f44336"
        )
        bar_h = 4
        bar_w = int(ratio * (x2 - x1))
        self.canvas.create_rectangle(
            x1, y2 - bar_h, x1 + bar_w, y2, fill=bar_color, outline=""
        )

        self.canvas.create_text(
            x2 - 3, y1 + 3,
            text=str(state.life),
            font=("Arial", 7, "bold"),
            fill="#222",
            anchor="ne",
        )

    def draw_last_move(self):
        if not self.last_move:
            return
        for sq in [self.last_move.from_square, self.last_move.to_square]:
            c = chess.square_file(sq)
            r = chess.square_rank(sq)
            x1, y1 = c * self.CELL, (7 - r) * self.CELL
            x2, y2 = x1 + self.CELL, y1 + self.CELL
            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=self.highlight, stipple="gray25", outline=""
            )

    def draw_arrow(self, move):
        if not move:
            return
        cell = self.CELL
        f, t = move.from_square, move.to_square
        fc, fr = chess.square_file(f), chess.square_rank(f)
        tc, tr = chess.square_file(t), chess.square_rank(t)
        self.canvas.create_line(
            fc * cell + cell // 2, (7 - fr) * cell + cell // 2,
            tc * cell + cell // 2, (7 - tr) * cell + cell // 2,
            width=3, fill=self.arrow_color, arrow=tk.LAST,
        )

    def update_queue_display(self):
        queue = self.life_board.respawn_queue
        white = "".join(s.chess_piece.unicode_symbol() for s in queue if s.chess_piece.color == chess.WHITE)
        black = "".join(s.chess_piece.unicode_symbol() for s in queue if s.chess_piece.color == chess.BLACK)
        self.white_queue_label.config(text=white or "—")
        self.black_queue_label.config(text=black or "—")

    # ------------------------------------------------------------------
    # interaction
    # ------------------------------------------------------------------

    def on_click(self, event):
        cell = self.CELL
        col, row = event.x // cell, 7 - (event.y // cell)
        square = chess.square(col, row)

        if self.selected_square is None:
            piece = self.life_board.piece_at(square)
            if piece and piece.color == self.life_board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)

            piece = self.life_board.piece_at(self.selected_square)
            if piece and piece.piece_type == chess.PAWN and (row == 7 or row == 0):
                move.promotion = chess.QUEEN

            if move in self.life_board.legal_moves:
                self.life_board.push(move)
                self.last_move = move

                self.draw_board()
                self.update_queue_display()
                self.root.update()

                if not self.life_board.is_game_over():
                    self.ai_move()

            self.selected_square = None
            self.draw_board()
            self.check_game_over()

    def ai_move(self):
        self.root.title("AI thinking...")
        move = self.ai.get_best_move(self.life_board)

        if move:
            self.life_board.push(move)
            self.last_move = move

        self.root.title("Chess AI")
        self.draw_board()
        self.update_queue_display()

    def check_game_over(self):
        if self.life_board.is_game_over():
            res = self.life_board.result()
            messagebox.showinfo("Game Over", f"Result: {res}")

            self.life_board.reset()
            self.last_move = None

            self.draw_board()
            self.update_queue_display()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess AI")

    try:
        ai = AIPlayer("models/chess_model-life-board_1_loss_0.2578.pth")
        gui = ChessGUI(root, ai)
        root.mainloop()
    except FileNotFoundError:
        print("Model file not found.")
