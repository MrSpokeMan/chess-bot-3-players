import os
import customtkinter as ctk
from PIL import Image
from themes import ThemeManager

class StartMenu(ctk.CTkFrame):
    def __init__(self, parent, config, on_start_callback, on_ai_vs_ai_callback):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_start = on_start_callback
        self.on_ai_vs_ai = on_ai_vs_ai_callback

        self.grid_columnconfigure(0, weight=2) 
        self.grid_columnconfigure(1, weight=3) 
        self.grid_rowconfigure(0, weight=1)

        self.left_container = ctk.CTkFrame(self, fg_color="transparent")
        self.left_container.grid(row=0, column=0, sticky="nsew")

        try:
            logo_path = os.path.join("assets", "logo.png")
            logo_img = ctk.CTkImage(light_image=Image.open(logo_path),
                                    dark_image=Image.open(logo_path),
                                    size=(250, 250))
            self.logo_label = ctk.CTkLabel(self.left_container, image=logo_img, text="")
            self.logo_label.pack(expand=True, pady=(20, 0), anchor="s") 
        except Exception:
            pass 

        self.title = ctk.CTkLabel(
            self.left_container, 
            text="IMMORTAL\nKINGS", 
            font=ctk.CTkFont(family="Segoe UI Symbol", size=40, weight="bold")
        )
        self.title.pack(expand=True, pady=(0, 20), anchor="n")

        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=(0, 40))

        self.right_content = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.right_content.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)

        settings_frame = ctk.CTkFrame(self.right_content, corner_radius=20, fg_color=("#ebebeb", "#1e1e1e"))
        settings_frame.pack(fill="x", pady=10)

        sections = [
            ("PLAYER IDENTIFIER", self._create_name_entry),
            ("ASSIGNED SIDE", self._create_side_selector),
            ("INTERFACE THEME", self._create_theme_menu)
        ]

        for label_text, creator_func in sections:
            ctk.CTkLabel(settings_frame, text=label_text, text_color="gray",
                         font=ctk.CTkFont(family="Segoe UI Symbol", size=14, weight="bold")).pack(pady=(15, 0))
            creator_func(settings_frame)

        self.start_btn = ctk.CTkButton(self.right_content, text="INITIATE SEQUENCE",
                                      font=ctk.CTkFont(family="Segoe UI Symbol", size=16, weight="bold"),
                                      height=50, fg_color="#d32f2f", hover_color="#b71c1c",
                                      command=self._start_game)
        self.start_btn.pack(fill="x", pady=(10, 0))

        self.ai_vs_ai_btn = ctk.CTkButton(
            self.right_content, text="WATCH AI BATTLE",
            font=ctk.CTkFont(family="Segoe UI Symbol", size=16, weight="bold"),
            height=50, fg_color="#1565c0", hover_color="#0d47a1",
            command=self.on_ai_vs_ai
        )
        self.ai_vs_ai_btn.pack(fill="x", pady=(8, 0))

    def _create_name_entry(self, p):
        self.name_entry = ctk.CTkEntry(p, placeholder_text="Enter Name...", width=320, height=35)
        self.name_entry.pack(pady=(5, 15))

    def _create_side_selector(self, p):
        self.side_var = ctk.StringVar(value="White")
        self.side_selector = ctk.CTkSegmentedButton(p, values=["White", "Black"], variable=self.side_var, height=35)
        self.side_selector.pack(pady=(5, 15), padx=20, fill="x")

    def _create_theme_menu(self, p):
        self.theme_var = ctk.StringVar(value=self.config.theme_name)
        self.theme_menu = ctk.CTkOptionMenu(p, values=list(ThemeManager.THEMES.keys()), variable=self.theme_var)
        self.theme_menu.pack(pady=(5, 25), padx=20, fill="x")
    
    def _start_game(self):
        self.config.theme_name = self.theme_var.get()
        self.config.player_name = self.name_entry.get() or "Player 1"
        self.config.player_side = self.side_var.get()
        self.on_start()
