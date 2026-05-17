import customtkinter as ctk
import tkinter.messagebox as messagebox
import chess
import torch
import sys
import os

from game_over import GameOverModal
from life_board import LifeBoard
from utils import board_to_tensor
from model import ChessNet

from themes import ThemeManager, GameConfig
from ui_menu import StartMenu
from ui_board import ChessBoardUI

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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

class GameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Immortal Kings")
        self.geometry("1250x600")
        self.minsize(1250, 600)
        
        self._setup_app_icon()

        self.config = GameConfig()
        self.life_board = LifeBoard()
        try:
            self.ai = AIPlayer("models/chess_model-life-board_1_loss_0.2578.pth")
        except FileNotFoundError:
            print("Warning: Model file not found. AI moves will fail.")
            self.ai = None

        self.selected_square = None
        self.last_move = None
        self.ai_vs_ai_mode = False
        self._ai_step_id = None

        self.show_menu()

    def show_menu(self):
        for widget in self.winfo_children():
            widget.destroy()
            
        self.configure(fg_color="#121212")
        self.menu_frame = StartMenu(self, self.config, self.start_game, self.start_ai_vs_ai)
        self.menu_frame.pack(fill="both", expand=True, padx=100, pady=50)

    def _build_game_ui(self, left_title, left_subtitle, right_title, right_subtitle, click_handler):
        self.theme = ThemeManager.get_theme(self.config.theme_name)
        self.configure(fg_color=self.theme["bg"])

        title_font = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        subtitle_font = ctk.CTkFont(family="Segoe UI", size=14)
        queue_font = ctk.CTkFont(family="Segoe UI Symbol", size=34)

        self.game_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.game_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.left_panel = ctk.CTkFrame(self.game_frame, width=300, corner_radius=20, fg_color=self.theme["panel_bg"])
        self.left_panel.pack(side="left", fill="y", padx=(0, 20))
        self.left_panel.pack_propagate(False)

        ctk.CTkLabel(self.left_panel, text=left_title, font=title_font, text_color=self.theme["text_white"]).pack(anchor="w", padx=28, pady=(30, 5))
        ctk.CTkLabel(self.left_panel, text=left_subtitle, font=subtitle_font, text_color="#8a8a8a").pack(anchor="w", padx=30)
        ctk.CTkLabel(self.left_panel, text="WHITE QUEUE", font=subtitle_font, text_color="#9c9c9c").pack(anchor="w", padx=30, pady=(45, 8))

        self.lbl_white_queue = ctk.CTkLabel(self.left_panel, text="—", font=queue_font, text_color=self.theme["text_white"])
        self.lbl_white_queue.pack(anchor="w", padx=30)

        self.right_panel = ctk.CTkFrame(self.game_frame, width=300, corner_radius=20, fg_color=self.theme["panel_bg"])
        self.right_panel.pack(side="right", fill="y", padx=(20, 0))
        self.right_panel.pack_propagate(False)

        ctk.CTkLabel(self.right_panel, text=right_title, font=title_font, text_color=self.theme["text_white"]).pack(anchor="w", padx=28, pady=(30, 5))
        ctk.CTkLabel(self.right_panel, text=right_subtitle, font=subtitle_font, text_color="#8a8a8a").pack(anchor="w", padx=30)
        ctk.CTkLabel(self.right_panel, text="BLACK QUEUE", font=subtitle_font, text_color="#9c9c9c").pack(anchor="w", padx=30, pady=(45, 8))

        self.lbl_black_queue = ctk.CTkLabel(self.right_panel, text="—", font=queue_font, text_color=self.theme["text_white"])
        self.lbl_black_queue.pack(anchor="w", padx=30)

        back_btn = ctk.CTkButton(self.right_panel, text="ABORT MATCH", height=44, corner_radius=12, font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), fg_color="#ab3333", hover_color="#802424", command=self.reset_to_menu)
        back_btn.pack(side="bottom", pady=20, padx=20)

        self.board_container = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        self.board_container.pack(side="left", fill="both", expand=True)

        self.board_ui = ChessBoardUI(self.board_container, self.theme, click_handler)
        self.board_ui.place(relx=0.5, rely=0.5, anchor="center")

        self.board_container.bind("<Configure>", self.on_container_resize)

    def start_game(self):
        self.menu_frame.destroy()
        self.ai_vs_ai_mode = False
        self._build_game_ui(
            left_title=self.config.player_name,
            left_subtitle="Human Player",
            right_title="AI OPPONENT",
            right_subtitle="Neural Network",
            click_handler=self.handle_click,
        )
        self.human_color = chess.WHITE if self.config.player_side == "White" else chess.BLACK
        self.ai_color = not self.human_color
        if self.human_color == chess.BLACK:
            self.after(300, self.ai_move)
        self.update_view()

    def start_ai_vs_ai(self):
        self.menu_frame.destroy()
        self.ai_vs_ai_mode = True
        self._build_game_ui(
            left_title="WHITE AI",
            left_subtitle="Neural Network",
            right_title="BLACK AI",
            right_subtitle="Neural Network",
            click_handler=lambda sq: None,
        )
        self.update_view()
        self._ai_step_id = self.after(500, self._ai_vs_ai_step)

    def _ai_vs_ai_step(self):
        self._ai_step_id = None
        if not self.ai or self.check_game_over():
            return
        move = self.ai.get_best_move(self.life_board)
        if move:
            self.life_board.push(move)
            self.last_move = move
        self.update_view()
        if not self.check_game_over():
            self._ai_step_id = self.after(2000, self._ai_vs_ai_step)

    def on_container_resize(self, event):
        size = min(event.width, event.height)
        
        self.board_ui.configure(width=size, height=size)
        self.board_ui.update_size(size)

    def handle_click(self, square):
        if self.life_board.board.turn != self.human_color:
            return

        piece = self.life_board.piece_at(square)

        if self.selected_square is not None:
            move = chess.Move(self.selected_square, square)
            
            if piece and piece.piece_type == chess.PAWN and (chess.square_rank(square) == 7 or chess.square_rank(square) == 0):
                move.promotion = chess.QUEEN

            if move in self.life_board.board.legal_moves:
                self.life_board.push(move)
                self.last_move = move
                self.selected_square = None
                self.update_view()
                self.update() 
                
                if self.life_board.board.turn == self.ai_color and not self.check_game_over():
                    self.ai_move()
            else:
                if piece and piece.color == self.life_board.board.turn:
                    self.selected_square = square
                else:
                    self.selected_square = None

        else:
            if piece and piece.color == self.life_board.board.turn:
                self.selected_square = square

        self.update_view()

    def ai_move(self):
        def ai_move(self):
            if not self.ai:
                return

            if self.life_board.board.turn != self.ai_color:
                return
        
        self.title("Immortal Kings...")
        move = self.ai.get_best_move(self.life_board)

        if move:
            self.life_board.push(move)
            self.last_move = move

        self.title("Immortal Kings")
        self.update_view()
        self.check_game_over()

    def check_game_over(self):
        if self.life_board.is_game_over():
            outcome = self.life_board.outcome()
            result = self.life_board.result()
            
            if outcome:
                reason = outcome.termination.name.replace("_", " ").title()
            else:
                reason = "Game Over"

            if self.ai_vs_ai_mode:
                if result == "1-0":
                    winner = "White AI"
                elif result == "0-1":
                    winner = "Black AI"
                else:
                    winner = "Draw"
            elif result == "1-0":
                winner = self.config.player_name if self.config.player_side == "White" else "AI Opponent"
            elif result == "0-1":
                winner = self.config.player_name if self.config.player_side == "Black" else "AI Opponent"
            else:
                winner = "Draw"

            GameOverModal(
                parent=self,
                winner_name=winner,
                total_moves=self.life_board.board.fullmove_number,
                result_type=reason,
                theme=self.theme,
                on_close=self.reset_to_menu
            )
            return True
        return False

    def update_view(self):
        queue = self.life_board.respawn_queue
        white = "".join(s.chess_piece.unicode_symbol() for s in queue if s.chess_piece.color == chess.WHITE)
        black = "".join(s.chess_piece.unicode_symbol() for s in queue if s.chess_piece.color == chess.BLACK)
        self.lbl_white_queue.configure(text=white or "—")
        self.lbl_black_queue.configure(text=black or "—")

        valid_moves = []
        if self.selected_square is not None:
            valid_moves = [m for m in self.life_board.board.legal_moves if m.from_square == self.selected_square]

        self.board_ui.update_state(
            life_board=self.life_board, 
            selected_square=self.selected_square, 
            valid_moves=valid_moves, 
            last_move=self.last_move
        )

    def reset_to_menu(self):
        if self._ai_step_id is not None:
            self.after_cancel(self._ai_step_id)
            self._ai_step_id = None
        self.ai_vs_ai_mode = False
        self.life_board.reset()
        self.last_move = None
        self.selected_square = None
        self.show_menu()
    
    def _setup_app_icon(self):
        try:
            if sys.platform.startswith("win"):
                import ctypes

                myappid = "immortal.kings.chess.v1"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

                icon_path = os.path.join("assets", "logo.ico")

                if os.path.exists(icon_path):
                    self.iconbitmap(icon_path)

            else:
                from PIL import Image, ImageTk

                icon_path = os.path.join("assets", "logo.png")

                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    self.photo = ImageTk.PhotoImage(img)
                    self.iconphoto(True, self.photo)

        except Exception as e:
            print(f"Icon initialization failed: {e}")

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()