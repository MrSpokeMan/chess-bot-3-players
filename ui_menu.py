import customtkinter as ctk
from themes import ThemeManager

class StartMenu(ctk.CTkFrame):
    def __init__(self, parent, config, on_start_callback):
        super().__init__(parent, fg_color="transparent")
        self.config = config
        self.on_start = on_start_callback

        title = ctk.CTkLabel(self, text="Chess AI", 
                             font=ctk.CTkFont(family="Helvetica", size=36, weight="bold"))
        title.pack(pady=(60, 40))

        settings_frame = ctk.CTkFrame(self, corner_radius=15)
        settings_frame.pack(pady=20, padx=40, fill="both", expand=True)

        ctk.CTkLabel(settings_frame, text="SELECT BOARD THEME", 
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(pady=(20, 10))
        
        self.theme_var = ctk.StringVar(value=self.config.theme_name)
        themes_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        themes_frame.pack(pady=10)
        
        for theme in ThemeManager.THEMES.keys():
            rad = ctk.CTkRadioButton(themes_frame, text=theme, variable=self.theme_var, 
                                     value=theme, font=ctk.CTkFont(size=14))
            rad.pack(side="left", padx=15)

        ctk.CTkLabel(settings_frame, text="GAME RULES", 
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="gray").pack(pady=(30, 10))
        
        self.timer_switch = ctk.CTkSwitch(settings_frame, text="Enable Match Timers", 
                                          font=ctk.CTkFont(size=14))
        self.timer_switch.pack(pady=10)
        if self.config.use_timers:
            self.timer_switch.select()

        start_btn = ctk.CTkButton(self, text="INITIATE SEQUENCE", 
                                  font=ctk.CTkFont(size=16, weight="bold"), 
                                  height=50, corner_radius=8, command=self._start_game)
        start_btn.pack(pady=40)

    def _start_game(self):
        self.config.theme_name = self.theme_var.get()
        self.config.use_timers = self.timer_switch.get() == 1
        self.on_start()
        