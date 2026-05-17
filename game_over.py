import customtkinter as ctk
import os
import sys

class GameOverModal(ctk.CTkToplevel):
    def __init__(self, parent, winner_name, total_moves, result_type, theme, on_close):
        super().__init__(parent)
        self.title("Match Summary")
        self.on_close = on_close
        
        self.attributes("-topmost", True)  
        self.configure(fg_color=theme["bg"])
        self.resizable(False, False)
        
        self.update_idletasks()
        width, height = 400, 520
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.transient(parent)
        self.grab_set() 

        self._set_modal_icon()

        ctk.CTkLabel(self, text="GAME OVER", 
                     font=ctk.CTkFont(family="Segoe UI Symbol", size=36, weight="bold"),
                     text_color=theme["text_white"]).pack(pady=(40, 5))
        
        ctk.CTkLabel(self, text=result_type.upper(), 
                     font=ctk.CTkFont(family="Segoe UI Symbol", size=14, weight="bold"),
                     text_color=theme["valid_move"]).pack(pady=(0, 20))
        
        stats_frame = ctk.CTkFrame(self, fg_color=theme["panel_bg"], corner_radius=15)
        stats_frame.pack(pady=20, padx=40, fill="both", expand=True)

        self._add_stat(stats_frame, "VICTORY", winner_name.upper(), theme)
        self._add_stat(stats_frame, "TOTAL MOVES", str(total_moves), theme)
        self._add_stat(stats_frame, "MATCH STATUS", "COMPLETED", theme)

        self.btn = ctk.CTkButton(self, text="RETURN TO MENU", height=50, corner_radius=8,
                                 font=ctk.CTkFont(family="Segoe UI Symbol", size=14, weight="bold"),
                                 fg_color=theme["dark"], hover_color="#333333",
                                 command=self.close_modal)
        self.btn.pack(pady=30, padx=40, fill="x")

    def _add_stat(self, parent, label, value, theme):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(pady=12)
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(family="Segoe UI Symbol", size=10, weight="bold"), 
                     text_color="gray").pack()
        ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(family="Segoe UI Symbol", size=20, weight="bold"), 
                     text_color=theme["text_white"]).pack()
        
    def close_modal(self):
        self.grab_release()
        self.destroy()
        if self.on_close:
            self.master.after(100, self.on_close)

    def _set_modal_icon(self):
        icon_path = os.path.join("assets", "logo.ico") # Using .ico as requested
        
        if os.path.exists(icon_path):
            try:
                if sys.platform.startswith("win"):
                    self.after(200, lambda: self.wm_iconbitmap(icon_path))
                else:
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    self.photo = ImageTk.PhotoImage(img)
                    self.wm_iconphoto(True, self.photo)
            except Exception as e:
                print(f"Modal icon failed to load: {e}")