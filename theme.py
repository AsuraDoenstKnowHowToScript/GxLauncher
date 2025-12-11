"""
Theme configuration for GxLauncher
Xbox Dark theme with crimson accents
"""

class Theme:
    """Central theme management"""
    
    # Core colors
    BG = "#0A0A0C"
    BG_ALT = "#12121A"
    CARD_BG = "#1A1A1E"
    CARD_HOVER = "#252529"
    
    # Text colors
    FG = "#FFFFFF"
    FG_DIM = "#8C8C92"
    FG_DISABLED = "#5C5C62"
    
    # Accent colors
    ACCENT = "#DC143C"  # Crimson
    ACCENT_HOVER = "#E63946"
    ACCENT_PRESSED = "#B8112D"
    RUBY = "#9B111E"
    
    # UI elements
    BORDER = "#2A2A2E"
    BORDER_FOCUS = "#DC143C"
    SUCCESS = "#107C10"
    WARNING = "#FFB900"
    ERROR = "#E81123"
    
    # Shadows
    SHADOW_LIGHT = "rgba(0, 0, 0, 0.2)"
    SHADOW_MEDIUM = "rgba(0, 0, 0, 0.4)"
    SHADOW_HEAVY = "rgba(0, 0, 0, 0.6)"
    
    @staticmethod
    def get_button_style(primary=False, danger=False):
        """Get button stylesheet"""
        if danger:
            bg = Theme.RUBY
            hover = Theme.ERROR
            pressed = "#8B0000"
        elif primary:
            bg = Theme.ACCENT
            hover = Theme.ACCENT_HOVER
            pressed = Theme.ACCENT_PRESSED
        else:
            bg = "transparent"
            hover = Theme.CARD_HOVER
            pressed = Theme.CARD_BG
            
        return f"""
            QPushButton {{
                background: {bg};
                color: {Theme.FG};
                border: 2px solid {Theme.ACCENT if primary or danger else Theme.BORDER};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {hover};
                border-color: {Theme.ACCENT};
            }}
            QPushButton:pressed {{
                background: {pressed};
            }}
            QPushButton:disabled {{
                background: {Theme.CARD_BG};
                color: {Theme.FG_DISABLED};
                border-color: {Theme.BORDER};
            }}
        """
    
    @staticmethod
    def get_input_style():
        """Get input field stylesheet"""
        return f"""
            QLineEdit, QSpinBox, QComboBox {{
                background: {Theme.CARD_BG};
                color: {Theme.FG};
                border: 2px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
            }}
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
                border-color: {Theme.ACCENT};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {Theme.FG_DIM};
                width: 0;
                height: 0;
            }}
        """
    
    @staticmethod
    def get_scrollbar_style():
        """Get scrollbar stylesheet"""
        return f"""
            QScrollBar:vertical {{
                background: {Theme.BG};
                width: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER};
                border-radius: 5px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {Theme.FG_DIM};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                background: {Theme.BG};
                height: 12px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:horizontal {{
                background: {Theme.BORDER};
                border-radius: 5px;
                min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {Theme.FG_DIM};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """