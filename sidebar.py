"""
Sidebar panel for game details
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QTextEdit, QFileDialog,
                             QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from core.theme import Theme
from core.utils import format_playtime, format_date, open_file_location

class GameDetailsSidebar(QWidget):
    """Sidebar showing detailed game information"""
    
    closed = pyqtSignal()
    game_updated = pyqtSignal(dict)
    game_removed = pyqtSignal(str)
    launch_requested = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_game = None
        self.setFixedWidth(350)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(50)
        header.setStyleSheet(f"background: {Theme.CARD_BG}; border-bottom: 1px solid {Theme.BORDER};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Detalhes do Jogo")
        title.setStyleSheet(f"color: {Theme.FG}; font-size: 16px; font-weight: 600;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Theme.FG_DIM};
                border: none;
                border-radius: 4px;
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: {Theme.CARD_HOVER};
                color: {Theme.FG};
            }}
        """)
        close_btn.clicked.connect(self.closed.emit)
        header_layout.addWidget(close_btn)
        
        layout.addWidget(header)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"""
            QScrollArea {{
                background: {Theme.BG};
                border: none;
            }}
            {Theme.get_scrollbar_style()}
        """)
        
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        # Cover image
        self.cover_widget = QWidget()
        cover_layout = QVBoxLayout(self.cover_widget)
        cover_layout.setContentsMargins(0, 0, 0, 0)
        
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(310, 400)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setStyleSheet(f"""
            background: {Theme.CARD_BG};
            border-radius: 8px;
            border: 2px solid {Theme.BORDER};
        """)
        cover_layout.addWidget(self.cover_label)
        
        change_cover_btn = QPushButton("Trocar Capa")
        change_cover_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_cover_btn.clicked.connect(self._change_cover)
        cover_layout.addWidget(change_cover_btn)
        
        self.content_layout.addWidget(self.cover_widget)
        
        # Game name (editable)
        name_label = QLabel("Nome")
        name_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px; font-weight: 600;")
        self.content_layout.addWidget(name_label)
        
        self.name_edit = QTextEdit()
        self.name_edit.setFixedHeight(60)
        self.name_edit.setPlaceholderText("Nome do jogo...")
        self.content_layout.addWidget(self.name_edit)
        
        # Statistics
        stats_label = QLabel("Estatísticas")
        stats_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px; font-weight: 600;")
        self.content_layout.addWidget(stats_label)
        
        self.stats_widget = QWidget()
        stats_layout = QVBoxLayout(self.stats_widget)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        self.playtime_label = QLabel()
        self.last_played_label = QLabel()
        self.added_label = QLabel()
        
        for label in [self.playtime_label, self.last_played_label, self.added_label]:
            label.setStyleSheet(f"color: {Theme.FG}; font-size: 13px;")
            stats_layout.addWidget(label)
        
        self.content_layout.addWidget(self.stats_widget)
        
        # Notes
        notes_label = QLabel("Notas")
        notes_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px; font-weight: 600;")
        self.content_layout.addWidget(notes_label)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(100)
        self.notes_edit.setPlaceholderText("Adicione suas notas...")
        self.content_layout.addWidget(self.notes_edit)
        
        # Action buttons
        self.content_layout.addStretch()
        
        play_btn = QPushButton("JOGAR")
        play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        play_btn.setFixedHeight(45)
        play_btn.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        play_btn.clicked.connect(self._launch_game)
        self.content_layout.addWidget(play_btn)
        
        btn_row1 = QHBoxLayout()
        
        save_btn = QPushButton("Salvar")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_changes)
        btn_row1.addWidget(save_btn)
        
        location_btn = QPushButton("Abrir Pasta")
        location_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        location_btn.clicked.connect(self._open_location)
        btn_row1.addWidget(location_btn)
        
        self.content_layout.addLayout(btn_row1)
        
        remove_btn = QPushButton("Remover Jogo")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(self._remove_game)
        self.content_layout.addWidget(remove_btn)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
    
    def _apply_styles(self):
        """Apply sidebar styles"""
        self.setStyleSheet(f"""
            QWidget {{
                background: {Theme.BG};
            }}
            QTextEdit {{
                background: {Theme.CARD_BG};
                color: {Theme.FG};
                border: 2px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }}
            QTextEdit:focus {{
                border-color: {Theme.ACCENT};
            }}
            QPushButton {{
                {Theme.get_button_style()}
            }}
        """)
        
        # Specific styles for action buttons
        play_style = Theme.get_button_style(primary=True)
        remove_style = Theme.get_button_style(danger=True)
        
        for btn in self.findChildren(QPushButton):
            if btn.text() == "JOGAR":
                btn.setStyleSheet(play_style)
            elif btn.text() == "Remover Jogo":
                btn.setStyleSheet(remove_style)
    
    def show_game(self, game: dict):
        """Display game details"""
        self.current_game = game
        
        # Load cover
        cover_path = game.get("cover", "")
        if cover_path and os.path.exists(cover_path):
            pixmap = QPixmap(cover_path).scaled(
                310, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(pixmap)
        else:
            self.cover_label.clear()
            self.cover_label.setText("Sem Capa")
        
        # Set name
        self.name_edit.setText(game.get("name", ""))
        
        # Set statistics
        playtime = game.get("playtime", 0)
        last_played = game.get("last_played", 0)
        added = game.get("added", 0)
        
        self.playtime_label.setText(f"⏱ Tempo jogado: {format_playtime(playtime)}")
        self.last_played_label.setText(f"🕐 Último jogo: {format_date(last_played)}")
        self.added_label.setText(f"📅 Adicionado: {format_date(added)}")
        
        # Set notes
        self.notes_edit.setText(game.get("notes", ""))
    
    def _change_cover(self):
        """Change game cover"""
        if not self.current_game:
            return
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Capa",
            "", "Imagens (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        
        if filepath:
            self.current_game["cover"] = filepath
            pixmap = QPixmap(filepath).scaled(
                310, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(pixmap)
    
    def _save_changes(self):
        """Save changes to game"""
        if not self.current_game:
            return
        
        self.current_game["name"] = self.name_edit.toPlainText().strip()
        self.current_game["notes"] = self.notes_edit.toPlainText()
        
        self.game_updated.emit(self.current_game)
        
        QMessageBox.information(self, "Sucesso", "Alterações salvas!")
    
    def _launch_game(self):
        """Launch the game"""
        if self.current_game:
            self.launch_requested.emit(self.current_game)
    
    def _open_location(self):
        """Open game folder"""
        if not self.current_game:
            return
        
        if not open_file_location(self.current_game.get("path", "")):
            QMessageBox.warning(self, "Erro", "Não foi possível abrir a pasta.")
    
    def _remove_game(self):
        """Remove the game"""
        if not self.current_game:
            return
        
        reply = QMessageBox.question(
            self, "Confirmar Remoção",
            f"Deseja remover '{self.current_game.get('name')}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.game_removed.emit(self.current_game.get("id"))
            self.closed.emit()