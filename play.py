import tkinter as tk
from tkinter import messagebox

import chess
import torch

from main import board_to_tensor
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

    def get_best_move(self, board):
        best_move = None
        best_eval = 1e9 if board.turn == chess.BLACK else -1e9

        for move in board.legal_moves:
            board.push(move)
            tensor = board_to_tensor(board).to(self.device)

            with torch.no_grad():
                val = self.model(tensor).item()

            board.pop()

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
    def __init__(self, root, ai):
        self.root = root
        self.ai = ai
        self.board = chess.Board()

        self.selected_square = None
        self.last_move = None

        self.captured_by_white = []
        self.captured_by_black = []

        # Colors (modern palette)
        self.bg = "#202124"
        self.light = "#f0d9b5"
        self.dark = "#b58863"
        self.highlight = "#f6f669"
        self.arrow_color = "#4aa3ff"

        root.configure(bg=self.bg)

        # Layout
        frame = tk.Frame(root, bg=self.bg)
        frame.pack(padx=20, pady=20)

        self.canvas = tk.Canvas(
            frame, width=480, height=480, bg=self.bg, highlightthickness=0
        )
        self.canvas.grid(row=0, column=1)

        self.left_panel = tk.Frame(frame, bg=self.bg)
        self.left_panel.grid(row=0, column=0, padx=10)

        self.right_panel = tk.Frame(frame, bg=self.bg)
        self.right_panel.grid(row=0, column=2, padx=10)

        self.white_label = tk.Label(
            self.left_panel,
            text="White",
            fg="white",
            bg=self.bg,
            font=("Arial", 12, "bold"),
        )
        self.white_label.pack(anchor="w")

        self.white_captures = tk.Label(
            self.left_panel, text="", fg="white", bg=self.bg, font=("Arial", 20)
        )
        self.white_captures.pack(anchor="w")

        self.black_label = tk.Label(
            self.right_panel,
            text="Black",
            fg="white",
            bg=self.bg,
            font=("Arial", 12, "bold"),
        )
        self.black_label.pack(anchor="w")

        self.black_captures = tk.Label(
            self.right_panel, text="", fg="white", bg=self.bg, font=("Arial", 20)
        )
        self.black_captures.pack(anchor="w")

        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()
        self.update_captured_display()

    def draw_board(self):
        self.canvas.delete("all")

        for r in range(8):
            for c in range(8):
                x1, y1 = c * 60, (7 - r) * 60
                x2, y2 = x1 + 60, y1 + 60

                color = self.light if (r + c) % 2 == 0 else self.dark

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board.piece_at(chess.square(c, r))
                if piece:
                    self.canvas.create_text(
                        x1 + 30,
                        y1 + 30,
                        text=piece.unicode_symbol(),
                        font=("Segoe UI Symbol", 36),
                        fill="#111" if piece.color == chess.WHITE else "#000",
                    )

        self.draw_last_move()
        self.draw_arrow(self.last_move)

    def draw_last_move(self):
        if not self.last_move:
            return

        for sq in [self.last_move.from_square, self.last_move.to_square]:
            c = chess.square_file(sq)
            r = chess.square_rank(sq)

            x1, y1 = c * 60, (7 - r) * 60
            x2, y2 = x1 + 60, y1 + 60

            self.canvas.create_rectangle(
                x1, y1, x2, y2, fill=self.highlight, stipple="gray25", outline=""
            )

    def draw_arrow(self, move):
        if not move:
            return

        f, t = move.from_square, move.to_square

        fc, fr = chess.square_file(f), chess.square_rank(f)
        tc, tr = chess.square_file(t), chess.square_rank(t)

        x1, y1 = fc * 60 + 30, (7 - fr) * 60 + 30
        x2, y2 = tc * 60 + 30, (7 - tr) * 60 + 30

        self.canvas.create_line(
            x1, y1, x2, y2, width=3, fill=self.arrow_color, arrow=tk.LAST
        )

    def handle_capture(self, move):
        if not self.board.is_capture(move):
            return

        captured_piece = self.board.piece_at(move.to_square)

        if captured_piece is None:
            offset = -8 if self.board.turn == chess.WHITE else 8
            captured_piece = self.board.piece_at(move.to_square + offset)

        if captured_piece:
            if self.board.turn == chess.WHITE:
                self.captured_by_white.append(captured_piece.unicode_symbol())
            else:
                self.captured_by_black.append(captured_piece.unicode_symbol())

    def update_captured_display(self):
        self.white_captures.config(text=" ".join(self.captured_by_white))
        self.black_captures.config(text=" ".join(self.captured_by_black))

    def on_click(self, event):
        col, row = event.x // 60, 7 - (event.y // 60)
        square = chess.square(col, row)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)

            if self.board.piece_at(self.selected_square).piece_type == chess.PAWN and (
                row == 7 or row == 0
            ):
                move.promotion = chess.QUEEN

            if move in self.board.legal_moves:
                self.handle_capture(move)

                self.board.push(move)
                self.last_move = move

                self.draw_board()
                self.update_captured_display()
                self.root.update()

                if not self.board.is_game_over():
                    self.ai_move()

            self.selected_square = None
            self.draw_board()
            self.check_game_over()

    def ai_move(self):
        self.root.title("AI thinking...")
        move = self.ai.get_best_move(self.board)

        if move:
            self.handle_capture(move)
            self.board.push(move)
            self.last_move = move

        self.root.title("Chess AI")
        self.draw_board()
        self.update_captured_display()

    def check_game_over(self):
        if self.board.is_game_over():
            res = self.board.result()
            messagebox.showinfo("Game Over", f"Result: {res}")

            self.board.reset()
            self.captured_by_white.clear()
            self.captured_by_black.clear()
            self.last_move = None

            self.draw_board()
            self.update_captured_display()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess AI")

    try:
        ai = AIPlayer("chess_model_epoch_14.pth")
        gui = ChessGUI(root, ai)
        root.mainloop()
    except FileNotFoundError:
        print("Model file not found.")
