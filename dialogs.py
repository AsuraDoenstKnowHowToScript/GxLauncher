"""
Dialog windows for GxLauncher
"""

import os
import webbrowser
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QSpinBox, QCheckBox,
                             QFileDialog, QMessageBox, QGroupBox, QComboBox,
                             QTextEdit, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from core.theme import Theme
from core.utils import validate_game_path, resolve_shortcut

class AddGameDialog(QDialog):
    """Dialog for adding a new game"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game_data = {}
        self.setWindowTitle("Adicionar Jogo")
        self.setFixedSize(550, 400)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Adicionar Novo Jogo")
        title.setStyleSheet(f"color: {Theme.FG}; font-size: 20px; font-weight: 600;")
        layout.addWidget(title)
        
        # Path selection
        path_label = QLabel("Executável do Jogo:")
        path_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 12px; font-weight: 600;")
        layout.addWidget(path_label)
        
        path_row = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Selecione o arquivo .exe ou .lnk...")
        self.path_input.setReadOnly(True)
        path_row.addWidget(self.path_input)
        
        browse_btn = QPushButton("Procurar")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._browse_game)
        path_row.addWidget(browse_btn)
        
        layout.addLayout(path_row)
        
        # Or paste path
        paste_btn = QPushButton("Ou Colar Caminho")
        paste_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        paste_btn.clicked.connect(self._paste_path)
        layout.addWidget(paste_btn)
        
        # Game name
        name_label = QLabel("Nome do Jogo:")
        name_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 12px; font-weight: 600;")
        layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome que aparecerá na biblioteca...")
        layout.addWidget(self.name_input)
        
        # Cover selection
        cover_label = QLabel("Capa (Opcional):")
        cover_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 12px; font-weight: 600;")
        layout.addWidget(cover_label)
        
        cover_row = QHBoxLayout()
        self.cover_input = QLineEdit()
        self.cover_input.setPlaceholderText("Nenhuma capa selecionada...")
        self.cover_input.setReadOnly(True)
        cover_row.addWidget(self.cover_input)
        
        cover_btn = QPushButton("Selecionar")
        cover_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cover_btn.clicked.connect(self._browse_cover)
        cover_row.addWidget(cover_btn)
        
        layout.addLayout(cover_row)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        add_btn = QPushButton("Adicionar")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self._add_game)
        btn_layout.addWidget(add_btn)
        
        layout.addLayout(btn_layout)
    
    def _apply_styles(self):
        """Apply dialog styles"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {Theme.BG};
            }}
            QLabel {{
                color: {Theme.FG};
            }}
            {Theme.get_input_style()}
            QPushButton {{
                {Theme.get_button_style(primary=True)}
                min-width: 100px;
            }}
        """)
    
    def _browse_game(self):
        """Browse for game executable"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Jogo",
            "", "Executáveis (*.exe *.lnk);;Todos os Arquivos (*.*)"
        )
        
        if filepath:
            self.path_input.setText(filepath)
            # Auto-fill name if empty
            if not self.name_input.text():
                resolved = resolve_shortcut(filepath)
                name = os.path.splitext(os.path.basename(resolved))[0]
                self.name_input.setText(name)
    
    def _paste_path(self):
        """Paste path from clipboard"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        path = clipboard.text().strip().strip('"')
        
        if path and os.path.exists(path):
            self.path_input.setText(path)
            if not self.name_input.text():
                resolved = resolve_shortcut(path)
                name = os.path.splitext(os.path.basename(resolved))[0]
                self.name_input.setText(name)
        else:
            QMessageBox.warning(self, "Aviso", "Caminho inválido na área de transferência!")
    
    def _browse_cover(self):
        """Browse for cover image"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Capa",
            "", "Imagens (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        
        if filepath:
            self.cover_input.setText(filepath)
    
    def _add_game(self):
        """Validate and add game"""
        path = self.path_input.text().strip()
        name = self.name_input.text().strip()
        cover = self.cover_input.text().strip()
        
        if not path:
            QMessageBox.warning(self, "Aviso", "Selecione o executável do jogo!")
            return
        
        if not validate_game_path(path):
            QMessageBox.warning(self, "Aviso", "Arquivo não encontrado ou inválido!")
            return
        
        if not name:
            QMessageBox.warning(self, "Aviso", "Digite o nome do jogo!")
            return
        
        self.game_data = {
            "name": name,
            "path": resolve_shortcut(path),
            "cover": cover,
            "notes": ""
        }
        
        self.accept()
    
    def get_game_data(self):
        """Get the game data"""
        return self.game_data


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, config, db, parent=None):
        super().__init__(parent)
        self.config = config
        self.db = db
        self.setWindowTitle("Configurações")
        self.setFixedSize(600, 700)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup settings UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Configurações")
        title.setStyleSheet(f"color: {Theme.FG}; font-size: 20px; font-weight: 600;")
        layout.addWidget(title)
        
        # Visual settings
        visual_group = QGroupBox("Visual")
        visual_layout = QVBoxLayout()
        
        # Grid columns
        cols_row = QHBoxLayout()
        cols_row.addWidget(QLabel("Colunas do Grid:"))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(3, 8)
        self.cols_spin.setValue(self.config.get("grid_columns", 4))
        cols_row.addWidget(self.cols_spin)
        cols_row.addStretch()
        visual_layout.addLayout(cols_row)
        
        self.show_playtime_check = QCheckBox("Mostrar tempo de jogo nos cards")
        self.show_playtime_check.setChecked(self.config.get("show_playtime", True))
        visual_layout.addWidget(self.show_playtime_check)
        
        visual_group.setLayout(visual_layout)
        layout.addWidget(visual_group)
        
        # Functionality settings
        func_group = QGroupBox("Funcionalidade")
        func_layout = QVBoxLayout()
        
        self.close_on_launch_check = QCheckBox("Fechar launcher ao abrir jogo")
        self.close_on_launch_check.setChecked(self.config.get("close_on_launch", False))
        func_layout.addWidget(self.close_on_launch_check)
        
        self.track_playtime_check = QCheckBox("Rastrear tempo de jogo automaticamente")
        self.track_playtime_check.setChecked(self.config.get("track_playtime", True))
        func_layout.addWidget(self.track_playtime_check)
        
        self.auto_update_check = QCheckBox("Verificar atualizações automaticamente")
        self.auto_update_check.setChecked(self.config.get("auto_check_updates", True))
        func_layout.addWidget(self.auto_update_check)
        
        func_group.setLayout(func_layout)
        layout.addWidget(func_group)
        
        # Data management
        data_group = QGroupBox("Gerenciamento de Dados")
        data_layout = QVBoxLayout()
        
        backup_btn = QPushButton("📦 Fazer Backup da Biblioteca")
        backup_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        backup_btn.clicked.connect(self._backup_library)
        data_layout.addWidget(backup_btn)
        
        restore_btn = QPushButton("📥 Restaurar Biblioteca")
        restore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restore_btn.clicked.connect(self._restore_library)
        data_layout.addWidget(restore_btn)
        
        reset_btn = QPushButton("🔄 Resetar Estatísticas")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.clicked.connect(self._reset_stats)
        data_layout.addWidget(reset_btn)
        
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)
        
        layout.addStretch()
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Salvar")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _apply_styles(self):
        """Apply dialog styles"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {Theme.BG};
            }}
            QLabel {{
                color: {Theme.FG};
            }}
            QGroupBox {{
                color: {Theme.FG};
                border: 2px solid {Theme.BORDER};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 20px;
                font-weight: 600;
                font-size: 14px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
            }}
            QCheckBox {{
                color: {Theme.FG};
                spacing: 10px;
                font-size: 13px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid {Theme.BORDER};
                background: {Theme.CARD_BG};
            }}
            QCheckBox::indicator:checked {{
                background: {Theme.ACCENT};
                border-color: {Theme.ACCENT};
            }}
            {Theme.get_input_style()}
            QPushButton {{
                {Theme.get_button_style()}
                text-align: left;
                padding: 12px 20px;
            }}
        """)
    
    def _save_settings(self):
        """Save settings"""
        self.config.set("grid_columns", self.cols_spin.value())
        self.config.set("show_playtime", self.show_playtime_check.isChecked())
        self.config.set("close_on_launch", self.close_on_launch_check.isChecked())
        self.config.set("track_playtime", self.track_playtime_check.isChecked())
        self.config.set("auto_check_updates", self.auto_update_check.isChecked())
        self.accept()
    
    def _backup_library(self):
        """Backup library"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Salvar Backup",
            "games_backup.json",
            "JSON Files (*.json)"
        )
        
        if filepath:
            if self.db.export_library(filepath):
                QMessageBox.information(self, "Sucesso", "Backup criado com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao criar backup!")
    
    def _restore_library(self):
        """Restore library"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Backup",
            "", "JSON Files (*.json)"
        )
        
        if filepath:
            reply = QMessageBox.question(
                self, "Confirmar",
                "Deseja mesclar com a biblioteca atual ou substituir?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Cancel:
                return
            
            merge = reply == QMessageBox.StandardButton.Yes
            
            if self.db.import_library(filepath, merge):
                QMessageBox.information(self, "Sucesso", "Biblioteca restaurada!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao restaurar biblioteca!")
    
    def _reset_stats(self):
        """Reset all statistics"""
        reply = QMessageBox.question(
            self, "Confirmar",
            "Resetar TODAS as estatísticas de tempo? Esta ação não pode ser desfeita!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.reset_stats():
                QMessageBox.information(self, "Sucesso", "Estatísticas resetadas!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao resetar estatísticas!")


class UpdateDialog(QDialog):
    """Update notification dialog"""
    
    def __init__(self, update_info, parent=None):
        super().__init__(parent)
        self.update_info = update_info
        self.setWindowTitle("Atualização Disponível")
        self.setFixedSize(550, 450)
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup update dialog UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Icon and title
        title = QLabel(f"🎉 Nova versão disponível: v{self.update_info['version']}")
        title.setStyleSheet(f"""
            color: {Theme.ACCENT};
            font-size: 18px;
            font-weight: 600;
        """)
        layout.addWidget(title)
        
        # Current version
        current = QLabel(f"Versão atual: v{self.update_info.get('current', 'Unknown')}")
        current.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 13px;")
        layout.addWidget(current)
        
        # Changelog
        changelog_label = QLabel("O que há de novo:")
        changelog_label.setStyleSheet(f"color: {Theme.FG}; font-size: 14px; font-weight: 600;")
        layout.addWidget(changelog_label)
        
        changelog = QTextEdit()
        changelog.setReadOnly(True)
        changelog.setPlainText(self.update_info.get('changelog', 'Nenhuma descrição disponível.'))
        changelog.setMaximumHeight(200)
        layout.addWidget(changelog)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        later_btn = QPushButton("Lembrar Depois")
        later_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        later_btn.clicked.connect(self.reject)
        btn_layout.addWidget(later_btn)
        
        download_btn = QPushButton("Baixar Atualização")
        download_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        download_btn.clicked.connect(self._download_update)
        btn_layout.addWidget(download_btn)
        
        layout.addLayout(btn_layout)
    
    def _apply_styles(self):
        """Apply dialog styles"""
        self.setStyleSheet(f"""
            QDialog {{
                background: {Theme.BG};
            }}
            QLabel {{
                color: {Theme.FG};
            }}
            QTextEdit {{
                background: {Theme.CARD_BG};
                color: {Theme.FG};
                border: 2px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 10px;
                font-size: 12px;
            }}
            QPushButton {{
                {Theme.get_button_style(primary=True)}
                min-width: 140px;
            }}
        """)
    
    def _download_update(self):
        """Open download URL"""
        url = self.update_info.get('url', '')
        if url:
            webbrowser.open(url)
        self.accept()