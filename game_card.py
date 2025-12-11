"""
Game card widget for GxLauncher
"""

import os
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QPainterPath, QFont
from PyQt6.QtCore import QRectF
from core.theme import Theme
from core.utils import format_playtime, launch_game

class GameCard(QWidget):
    """Interactive game card with hover animations"""
    
    clicked = pyqtSignal(dict)
    launch_requested = pyqtSignal(dict)
    
    def __init__(self, game: dict, config: dict, parent=None):
        super().__init__(parent)
        self.game = game
        self.config = config
        self.process = None
        self.start_time = None
        self._border_opacity = 0
        self._is_loading = False
        
        self.setFixedSize(220, 360)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()
        self._setup_animations()
    
    def _setup_ui(self):
        """Setup card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Card container
        self.card = QWidget()
        self.card.setObjectName("card")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        
        # Cover image
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(196, 270)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._load_cover()
        card_layout.addWidget(self.cover_label)
        
        # Game name
        name_label = QLabel(self.game.get("name", "Unknown"))
        name_label.setWordWrap(True)
        name_label.setFixedWidth(196)
        name_label.setMaximumHeight(40)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"""
            color: {Theme.FG};
            font-size: 13px;
            font-weight: 600;
            padding: 4px;
        """)
        card_layout.addWidget(name_label)
        
        # Playtime label
        if self.config.get("show_playtime") and self.game.get("playtime", 0) > 0:
            time_label = QLabel(f"⏱ {format_playtime(self.game['playtime'])}")
            time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px;")
            card_layout.addWidget(time_label)
        
        # Loading spinner
        self.spinner = QLabel("⏳")
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 24px;")
        self.spinner.hide()
        card_layout.addWidget(self.spinner)
        
        layout.addWidget(self.card)
        self._apply_styles()
    
    def _load_cover(self):
        """Load and display cover image"""
        cover_path = self.game.get("cover", "")
        
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path).scaled(
                196, 270,
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Create rounded mask
            rounded = QPixmap(pixmap.size())
            rounded.fill(Qt.GlobalColor.transparent)
            
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(QRectF(rounded.rect()), 8, 8)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            
            self.cover_label.setPixmap(rounded)
        else:
            self.cover_label.setStyleSheet(f"""
                background: {Theme.CARD_BG};
                border: 2px dashed {Theme.BORDER};
                border-radius: 8px;
                color: {Theme.FG_DIM};
                font-size: 12px;
            """)
            self.cover_label.setText("No Cover")
    
    def _setup_animations(self):
        """Setup hover animations"""
        self.border_animation = QPropertyAnimation(self, b"border_opacity")
        self.border_animation.setDuration(200)
        self.border_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def _apply_styles(self):
        """Apply card styles"""
        self.update_border_style()
    
    def get_border_opacity(self):
        return self._border_opacity
    
    def set_border_opacity(self, value):
        self._border_opacity = value
        self.update_border_style()
    
    border_opacity = pyqtProperty(int, get_border_opacity, set_border_opacity)
    
    def update_border_style(self):
        """Update card border based on hover state"""
        if self._border_opacity > 0:
            alpha = int(self._border_opacity * 2.55)
            border = f"rgba(220, 20, 60, {alpha})"
            shadow = f"0 0 20px rgba(220, 20, 60, {alpha * 0.4})"
        else:
            border = Theme.BORDER
            shadow = "none"
        
        self.card.setStyleSheet(f"""
            #card {{
                background: {Theme.CARD_BG};
                border-radius: 10px;
                border: 2px solid {border};
            }}
        """)
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        self.border_animation.stop()
        self.border_animation.setStartValue(self._border_opacity)
        self.border_animation.setEndValue(100)
        self.border_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        self.border_animation.stop()
        self.border_animation.setStartValue(self._border_opacity)
        self.border_animation.setEndValue(0)
        self.border_animation.start()
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.game)
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click to launch game"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.launch_game()
        super().mouseDoubleClickEvent(event)
    
    def launch_game(self):
        """Launch the game"""
        if self._is_loading:
            return
        
        self._is_loading = True
        self.spinner.show()
        
        try:
            if self.config.get("track_playtime"):
                self.start_time = time.time()
                self.process = launch_game(self.game["path"], track=True)
                QTimer.singleShot(2000, self._hide_loading)
                QTimer.singleShot(3000, self._check_process)
            else:
                launch_game(self.game["path"], track=False)
                QTimer.singleShot(2000, self._hide_loading)
            
            self.launch_requested.emit(self.game)
        except Exception as e:
            print(f"Error launching game: {e}")
            self._hide_loading()
    
    def _hide_loading(self):
        """Hide loading spinner"""
        self.spinner.hide()
        self._is_loading = False
    
    def _check_process(self):
        """Check if game process is still running"""
        if self.process and self.process.poll() is None:
            QTimer.singleShot(1000, self._check_process)
        elif self.start_time:
            elapsed = int(time.time() - self.start_time)
            if elapsed > 5:  # Only count if played for more than 5 seconds
                self.game["playtime"] = self.game.get("playtime", 0) + elapsed
                self.game["last_played"] = int(time.time())
            self.start_time = None
            self.process = None
    
    def update_game_data(self, game: dict):
        """Update card with new game data"""
        self.game = game
        self._load_cover()