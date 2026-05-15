# ui_board.py
import tkinter as tk
from PIL import Image, ImageTk, ImageOps
import os
import chess

class ChessBoardUI(tk.Canvas):
    def __init__(self, parent, theme, on_square_click):
        super().__init__(parent, bg=theme["bg"], highlightthickness=0)
        self.theme = theme
        self.on_square_click = on_square_click
        
        self.cell_size = 60
        self.life_board = None  # Now expects a LifeBoard instance
        self.selected_square = None
        self.hovered_square = None
        self.valid_moves = []
        self.last_move = None

        self.piece_images = {}
        self.image_refs = {}

        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_hover)
        self.bind("<Leave>", self._on_leave)

    def update_size(self, size):
        self.cell_size = max(10, size // 8)
        self.load_piece_images()
        self.draw()

    def load_piece_images(self):
        self.piece_images.clear()
        self.image_refs.clear()

        assets_dir = os.path.join("assets", "pieces")
        if not os.path.exists(assets_dir):
            return

        color_prefix = {chess.WHITE: 'w', chess.BLACK: 'b'}
        piece_letters = {chess.PAWN: 'p', chess.KNIGHT: 'n', chess.BISHOP: 'b',
                         chess.ROOK: 'r', chess.QUEEN: 'q', chess.KING: 'k'}
        
        piece_size = int(self.cell_size * 0.85)

        t_white = self.theme.get("text_white", "#ffffff")
        t_black = self.theme.get("text_black", "#000000")

        for color in [chess.WHITE, chess.BLACK]:
            for p_type in piece_letters:
                filename = f'{color_prefix[color]}{piece_letters[p_type]}.png'
                path = os.path.join(assets_dir, filename)

                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((piece_size, piece_size), Image.Resampling.LANCZOS)

                    alpha = img.getchannel('A')
                    gray_piece = img.convert("L")

                    colored_img = ImageOps.colorize(gray_piece, black=t_black, white=t_white)
                    colored_img.putalpha(alpha)
                    
                    tk_img = ImageTk.PhotoImage(colored_img)
                    self.piece_images[(color, p_type)] = tk_img
                    self.image_refs[(color, p_type)] = tk_img

    def _on_click(self, event):
        col, row = event.x // self.cell_size, 7 - (event.y // self.cell_size)
        if 0 <= col <= 7 and 0 <= row <= 7:
            self.on_square_click(chess.square(col, row))

    def _on_hover(self, event):
        col, row = event.x // self.cell_size, 7 - (event.y // self.cell_size)
        if 0 <= col <= 7 and 0 <= row <= 7:
            sq = chess.square(col, row)
            if self.hovered_square != sq:
                self.hovered_square = sq
                self.config(cursor="hand2")
                self.draw()
        else:
            self._on_leave(event)

    def _on_leave(self, event):
        self.hovered_square = None
        self.config(cursor="")
        self.draw()

    def update_state(self, life_board, selected_square, valid_moves, last_move):
        self.life_board = life_board
        self.selected_square = selected_square
        self.valid_moves = valid_moves
        self.last_move = last_move
        self.draw()

    def draw(self):
        self.delete("all")
        if not self.life_board: return

        for r in range(8):
            for c in range(8):
                x1, y1 = c * self.cell_size, (7 - r) * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                color = self.theme["light"] if (r + c) % 2 == 0 else self.theme["dark"]
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

        if self.last_move:
            for sq in [self.last_move.from_square, self.last_move.to_square]:
                self._highlight_square(sq, self.theme["highlight"], stipple="gray25")

        if self.selected_square is not None:
            self._highlight_square(self.selected_square, self.theme["highlight"])
        if self.hovered_square is not None:
            self._highlight_square(self.hovered_square, "#ffffff", stipple="gray12")

        for move in self.valid_moves:
            self._draw_valid_move_indicator(move.to_square)

        for r in range(8):
            for c in range(8):
                sq = chess.square(c, r)
                piece = self.life_board.piece_at(sq)
                
                if piece:
                    x1, y1 = c * self.cell_size, (7 - r) * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    cx, cy = x1 + self.cell_size // 2, y1 + self.cell_size // 2
                    
                    if (piece.color, piece.piece_type) in self.piece_images:
                        self.create_image(cx, cy, image=self.piece_images[(piece.color, piece.piece_type)])
                    else:
                        self.create_text(
                            cx, cy, text=piece.unicode_symbol(),
                            font=("Segoe UI Symbol", int(self.cell_size * 0.6)),
                            fill=self.theme["text_white"] if piece.color == chess.WHITE else "#000000"
                        )
                        
                    self._draw_life_bar(x1, y1, x2, y2, sq, piece)

    def _draw_life_bar(self, x1, y1, x2, y2, sq, piece):
        if piece.piece_type == chess.KING:
            return

        state = self.life_board.piece_state_at(sq)
        if state is None or state.max_life <= 1:
            return

        ratio = state.life / state.max_life
        bar_color = "#4caf50" if ratio > 0.6 else "#ff9800" if ratio > 0.3 else "#f44336"
        
        bar_h = max(4, int(self.cell_size * 0.08)) 
        bar_w = int(ratio * (x2 - x1))
        
        self.create_rectangle(x1, y2 - bar_h, x1 + bar_w, y2, fill=bar_color, outline="")
        self.create_text(
            x2 - 3, y1 + 3,
            text=str(state.life),
            font=("Segoe UI Symbol", max(8, int(self.cell_size * 0.15)), "bold"),
            fill=self.theme["text_white"],
            anchor="ne",
        )

    def _highlight_square(self, sq, color, stipple=""):
        c, r = chess.square_file(sq), chess.square_rank(sq)
        x1, y1 = c * self.cell_size, (7 - r) * self.cell_size
        self.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, fill=color, outline="", stipple=stipple)

    def _draw_valid_move_indicator(self, sq):
        c, r = chess.square_file(sq), chess.square_rank(sq)
        cx, cy = (c + 0.5) * self.cell_size, ((7 - r) + 0.5) * self.cell_size
        radius = self.cell_size * 0.15
        self.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=self.theme["valid_move"], outline="")