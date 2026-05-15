class ThemeManager:
    THEMES = {
        "Classical": {
            "bg": "#2b2b2b",
            "panel_bg": "#1e1e1e",

            "text_white": "#ffffff",
            "text_black": "#111111",

            "light": "#F0D9B5",
            "dark": "#B58863",

            "highlight": "#7C4D00",
            "valid_move": "#6aa84f",
            "arrow": "#4aa3ff"
        },

        "Neon": {
            "bg": "#050510",
            "panel_bg": "#0b0b1a",

            "text_white": "#00fff0",
            "text_black": "#ff2bd6",

            "light": "#2b00ff",
            "dark": "#0a0047",

            "highlight": "#007070",
            "valid_move": "#00ffcc",
            "arrow": "#ff007f"
        },

        "Medieval": {
            "bg": "#1a1410",
            "panel_bg": "#120e0b",

            "text_white": "#F5F0E6",
            "text_black": "#1A0F08",

            "light": "#E7D2B0",
            "dark": "#8B5A2B",

            "highlight": "#4B2E00",
            "valid_move": "#6B8E23",
            "arrow": "#C0A060"
        },

        "Dark": {
            "bg": "#121212",
            "panel_bg": "#1b1b1b",

            "text_white": "#bdbdbd",
            "text_black": "#0a0a0a",

            "light": "#5a5a5a",
            "dark": "#3a3a3a",

            "highlight": "#000000",
            "valid_move": "#4caf50",
            "arrow": "#40c4ff"
        },

        "PWR": {
            "bg": "#000000",
            "panel_bg": "#0a0a0a",

            "text_white": "#BE7200",
            "text_black": "#2b0f0c",

            "light": "#F1D1A2",
            "dark": "#9A342D",

            "highlight": "#6D3100",
            "valid_move": "#290300",
            "arrow": "#F1D1A2"
        }
    }

    @classmethod
    def get_theme(cls, theme_name):
        theme = cls.THEMES.get(theme_name)
        if not theme:
            return cls.THEMES["Classical"]
        return theme
    

class GameConfig:
    def __init__(self):
        self.theme_name = "Classical"
        self.use_timers = False
        self.human_time = 600  # seconds
        self.ai_time = 600     # seconds
