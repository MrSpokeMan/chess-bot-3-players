class ThemeManager:
    THEMES = {
        "Classical": {
            "bg": "#1e1e1e",
            "panel_bg": "#252525",

            "text_white": "#ffffff",
            "text_black": "#2c2c2c",

            "light": "#f0d9b5",
            "dark": "#b58863",

            "highlight": "#7c4d00",
            "valid_move": "#6aa84f",
            "arrow": "#4aa3ff"
        },

        "Neon": {
            "bg": "#0a0a12",
            "panel_bg": "#141425",

            "text_white": "#00aeef",
            "text_black": "#ec008c",

            "light": "#1f1f3d",
            "dark": "#0f0f23",

            "highlight": "#3d3d5c",
            "valid_move": "#00ffcc",
            "arrow": "#ff007f"
        },

        "Medieval": {
            "bg": "#1a1410",
            "panel_bg": "#2a1f19",

            "text_white": "#f5f0e6",
            "text_black": "#2a1b12",

            "light": "#dcb35c",
            "dark": "#8b4513",

            "highlight": "#4b2e00",
            "valid_move": "#6b8e23",
            "arrow": "#C0A060"
        },

        "Dark": {
            "bg": "#0d0d0d",
            "panel_bg": "#1a1a1a",

            "text_white": "#e0e0e0",
            "text_black": "#121212",

            "light": "#404040",
            "dark": "#2b2b2b",

            "highlight": "#555555",
            "valid_move": "#4caf50",
            "arrow": "#40c4ff"
        },

        "Wrocław Tech": {
            "bg": "#000000",
            "panel_bg": "#0a0a0a",

            "text_white": "#F1D1A2",
            "text_black": "#3d0000",

            "light": "#F1D1A2",
            "dark": "#9C352D",

            "highlight": "#ff4d4d",
            "valid_move": "#d4611e",
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
        self.player_name = "Player 1"
        self.player_side = "White"
