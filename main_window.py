"""
Main window for GxLauncher - Complete version
"""

import os
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QScrollArea, QLineEdit,
                             QComboBox, QFileDialog, QMessageBox, QGridLayout,
                             QApplication)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from core.theme import Theme
from core.database import Database
from core.config import Config
from core.utils import format_playtime
from core.updater import UpdateChecker
from ui.game_card import GameCard
from ui.sidebar import GameDetailsSidebar
from ui.dialogs import SettingsDialog, AddGameDialog, UpdateDialog

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, db: Database, config: Config):
        super().__init__()
        self.db = db
        self.config = config
        self.updater = UpdateChecker()
        self.current_filter = ""
        self.current_sort = "Nome"
        self.sidebar_visible = False
        
        self._setup_window()
        self._setup_ui()
        self._load_games()
        
        # Check for updates
        if config.get("auto_check_updates"):
            QTimer.singleShot(2000, self._check_updates)
    
    def _setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle("GxLauncher")
        self.setMinimumSize(1200, 800)
        
        # Restore window size
        width = self.config.get("window_width", 1400)
        height = self.config.get("window_height", 900)
        self.resize(width, height)
    
    def _setup_ui(self):
        """Setup main UI"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - main content
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # Header
        header = self._create_header()
        left_layout.addWidget(header)
        
        # Toolbar
        toolbar = self._create_toolbar()
        left_layout.addWidget(toolbar)
        
        # Search and filter bar
        filter_bar = self._create_filter_bar()
        left_layout.addWidget(filter_bar)
        
        # Games grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background: {Theme.BG};
                border: none;
            }}
            {Theme.get_scrollbar_style()}
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet(f"background: {Theme.BG};")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setContentsMargins(32, 32, 32, 32)
        self.grid_layout.setSpacing(24)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        left_layout.addWidget(self.scroll_area)
        
        # Footer
        footer = self._create_footer()
        left_layout.addWidget(footer)
        
        main_layout.addWidget(left_panel)
        
        # Right side - sidebar (hidden by default)
        self.sidebar = GameDetailsSidebar()
        self.sidebar.closed.connect(self._hide_sidebar)
        self.sidebar.game_updated.connect(self._on_game_updated)
        self.sidebar.game_removed.connect(self._on_game_removed)
        self.sidebar.launch_requested.connect(self._launch_game_from_sidebar)
        self.sidebar.hide()
        main_layout.addWidget(self.sidebar)
        
        # Apply global styles
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {Theme.BG};
            }}
        """)
    
    def _create_header(self):
        """Create header bar"""
        header = QWidget()
        header.setFixedHeight(60)
        header.setStyleSheet(f"""
            background: {Theme.CARD_BG};
            border-bottom: 1px solid {Theme.BORDER};
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 0, 32, 0)
        
        # Title
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        title = QLabel("GxLauncher")
        title.setStyleSheet(f"""
            color: {Theme.FG};
            font-size: 22px;
            font-weight: 300;
            letter-spacing: 1px;
        """)
        title_layout.addWidget(title)
        
        version = QLabel(f"v{UpdateChecker.CURRENT_VERSION}")
        version.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px;")
        title_layout.addWidget(version)
        
        subtitle = QLabel("ゲームランチャー")
        subtitle.setFont(QFont("Yu Gothic UI", 11))
        subtitle.setStyleSheet(f"color: {Theme.FG_DIM};")
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_widget)
        layout.addStretch()
        
        return header
    
    def _create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar = QWidget()
        toolbar.setFixedHeight(70)
        toolbar.setStyleSheet(f"background: {Theme.BG};")
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(32, 15, 32, 15)
        layout.setSpacing(12)
        
        layout.addStretch()
        
        # Add game button
        add_btn = QPushButton("+ Adicionar Jogo")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.clicked.connect(self._add_game)
        add_btn.setStyleSheet(Theme.get_button_style(primary=True))
        layout.addWidget(add_btn)
        
        # Import multiple button
        import_btn = QPushButton("Importar Múltiplos")
        import_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        import_btn.setFixedHeight(40)
        import_btn.clicked.connect(self._import_multiple)
        import_btn.setStyleSheet(Theme.get_button_style())
        layout.addWidget(import_btn)
        
        # Settings button
        settings_btn = QPushButton("⚙ Configurações")
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setFixedHeight(40)
        settings_btn.clicked.connect(self._open_settings)
        settings_btn.setStyleSheet(Theme.get_button_style())
        layout.addWidget(settings_btn)
        
        # Info button
        info_btn = QPushButton("ℹ Info")
        info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        info_btn.setFixedHeight(40)
        info_btn.clicked.connect(self._show_info)
        info_btn.setStyleSheet(Theme.get_button_style())
        layout.addWidget(info_btn)
        
        return toolbar
    
    def _create_filter_bar(self):
        """Create search and filter bar"""
        filter_bar = QWidget()
        filter_bar.setFixedHeight(60)
        filter_bar.setStyleSheet(f"background: {Theme.BG_ALT};")
        
        layout = QHBoxLayout(filter_bar)
        layout.setContentsMargins(32, 10, 32, 10)
        layout.setSpacing(12)
        
        # Search box
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar jogos...")
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setStyleSheet(Theme.get_input_style())
        layout.addWidget(self.search_input)
        
        # Sort by
        sort_label = QLabel("Ordenar:")
        sort_label.setStyleSheet(f"color: {Theme.FG_DIM};")
        layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Nome", "Tempo Jogado", "Último Jogado", "Data Adicionada"])
        self.sort_combo.setFixedHeight(40)
        self.sort_combo.setFixedWidth(180)
        self.sort_combo.currentTextChanged.connect(self._on_sort_changed)
        self.sort_combo.setStyleSheet(Theme.get_input_style())
        layout.addWidget(self.sort_combo)
        
        return filter_bar
    
    def _create_footer(self):
        """Create footer status bar"""
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet(f"""
            background: {Theme.CARD_BG};
            border-top: 1px solid {Theme.BORDER};
        """)
        
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(32, 0, 32, 0)
        
        self.status_label = QLabel("Pronto")
        self.status_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet(f"color: {Theme.FG_DIM}; font-size: 11px;")
        layout.addWidget(self.stats_label)
        
        return footer
    
    def _load_games(self):
        """Load and display games"""
        # Clear existing cards
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Get games with current filter and sort
        games = self._get_filtered_sorted_games()
        
        if not games:
            # Show empty state
            empty = QLabel("Nenhum jogo encontrado\n\nClique em '+ Adicionar Jogo' para começar")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(f"""
                color: {Theme.FG_DIM};
                font-size: 16px;
                padding: 100px;
            """)
            self.grid_layout.addWidget(empty, 0, 0)
            self.status_label.setText("Biblioteca vazia")
            self.stats_label.setText("")
            return
        
        # Calculate grid columns
        cols = self.config.get("grid_columns", 4)
        
        # Add game cards
        for i, game in enumerate(games):
            row = i // cols
            col = i % cols
            
            card = GameCard(game, self.config.config, self)
            card.clicked.connect(self._on_card_clicked)
            card.launch_requested.connect(self._on_game_launched)
            self.grid_layout.addWidget(card, row, col)
        
        # Update stats
        self._update_stats(games)
    
    def _get_filtered_sorted_games(self):
        """Get games with current filter and sort applied"""
        games = self.db.get_all_games()
        
        # Apply search filter
        if self.current_filter:
            games = [g for g in games if self.current_filter.lower() in g.get("name", "").lower()]
        
        # Apply sort
        sort_map = {
            "Nome": ("name", False),
            "Tempo Jogado": ("playtime", True),
            "Último Jogado": ("last_played", True),
            "Data Adicionada": ("added", True)
        }
        
        sort_key, reverse = sort_map.get(self.current_sort, ("name", False))
        
        if sort_key == "name":
            games = sorted(games, key=lambda g: g.get("name", "").lower(), reverse=reverse)
        else:
            games = sorted(games, key=lambda g: g.get(sort_key, 0), reverse=reverse)
        
        return games
    
    def _update_stats(self, games):
        """Update status bar statistics"""
        count = len(games)
        total_time = sum(g.get("playtime", 0) for g in games)
        
        self.status_label.setText(f"{count} {'jogo' if count == 1 else 'jogos'}")
        self.stats_label.setText(f"Tempo total: {format_playtime(total_time)}")
    
    def _on_search_changed(self, text):
        """Handle search input change"""
        self.current_filter = text
        self._load_games()
    
    def _on_sort_changed(self, text):
        """Handle sort selection change"""
        self.current_sort = text
        self._load_games()
    
    def _on_card_clicked(self, game):
        """Handle game card click"""
        self._show_sidebar(game)
    
    def _on_game_launched(self, game):
        """Handle game launch"""
        # Update last played
        self.db.update_game(game.get("id"), {"last_played": int(time.time())})
        
        if self.config.get("close_on_launch"):
            QTimer.singleShot(2000, QApplication.quit)
    
    def _show_sidebar(self, game):
        """Show sidebar with game details"""
        self.sidebar.show_game(game)
        if not self.sidebar_visible:
            self.sidebar.show()
            self.sidebar_visible = True
    
    def _hide_sidebar(self):
        """Hide sidebar"""
        self.sidebar.hide()
        self.sidebar_visible = False
    
    def _on_game_updated(self, game):
        """Handle game update from sidebar"""
        self.db.update_game(game.get("id"), game)
        self._load_games()
    
    def _on_game_removed(self, game_id):
        """Handle game removal"""
        self.db.remove_game(game_id)
        self._load_games()
    
    def _launch_game_from_sidebar(self, game):
        """Launch game from sidebar"""
        # Find the card and trigger launch
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, GameCard) and widget.game.get("id") == game.get("id"):
                widget.launch_game()
                break
    
    def _add_game(self):
        """Show add game dialog"""
        dialog = AddGameDialog(self)
        if dialog.exec():
            game_data = dialog.get_game_data()
            if game_data:
                # Generate ID
                game_data["id"] = str(int(time.time() * 1000))
                game_data["added"] = int(time.time())
                game_data["playtime"] = 0
                game_data["last_played"] = 0
                game_data["favorite"] = False
                game_data["tags"] = []
                
                if self.db.add_game(game_data):
                    self._load_games()
                    self.status_label.setText("Jogo adicionado com sucesso!")
                    QTimer.singleShot(3000, lambda: self.status_label.setText("Pronto"))
                else:
                    QMessageBox.warning(self, "Erro", "Este jogo já existe na biblioteca!")
    
    def _import_multiple(self):
        """Import multiple games at once"""
        folder = QFileDialog.getExistingDirectory(self, "Selecionar Pasta com Jogos")
        
        if not folder:
            return
        
        # Find all executables
        executables = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.exe'):
                    full_path = os.path.join(root, file)
                    executables.append(full_path)
        
        if not executables:
            QMessageBox.information(self, "Info", "Nenhum executável encontrado na pasta.")
            return
        
        # Add all found games
        added = 0
        timestamp = int(time.time() * 1000)
        for i, exe_path in enumerate(executables):
            game_name = os.path.splitext(os.path.basename(exe_path))[0]
            
            game_data = {
                "id": f"{timestamp}_{i}",
                "name": game_name,
                "path": exe_path,
                "cover": "",
                "playtime": 0,
                "last_played": 0,
                "added": int(time.time()),
                "favorite": False,
                "tags": [],
                "notes": ""
            }
            
            if self.db.add_game(game_data):
                added += 1
        
        self._load_games()
        QMessageBox.information(self, "Sucesso", f"{added} jogos adicionados à biblioteca!")
    
    def _open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config, self.db, self)
        if dialog.exec():
            self.config.save()
            self._load_games()
    
    def _show_info(self):
        """Show info dialog"""
        info_text = f"""
        <div style="text-align: center;">
            <h2 style="color: {Theme.ACCENT}; margin-bottom: 20px;">
                GxLauncher v{UpdateChecker.CURRENT_VERSION}
            </h2>
        </div>
        
        <p style="color: {Theme.FG}; line-height: 1.6;">
            <b style="color: {Theme.ACCENT};">Sobre:</b><br>
            Launcher de jogos moderno com tema Xbox Dark e rastreamento de tempo de jogo.
            <br><br>
            
            <b style="color: {Theme.ACCENT};">Recursos:</b><br>
            • Rastreamento automático de tempo de jogo<br>
            • Grid responsivo e customizável<br>
            • Importação em lote de jogos<br>
            • Sistema de busca e filtros<br>
            • Backup e restauração de biblioteca<br>
            • Verificação automática de atualizações<br>
            <br>
            
            <b style="color: {Theme.ACCENT};">Dicas:</b><br>
            • Clique duplo no card para jogar<br>
            • Clique simples para ver detalhes<br>
            • Recomendado: capas 600x900px (2:3)<br>
            <br>
            
            <b style="color: {Theme.ACCENT};">Desenvolvido por:</b><br>
            © 2024 Suny - Todos os direitos reservados
            <br><br>
            
            <span style="color: {Theme.FG_DIM}; font-size: 11px;">
                Construído com PyQt6 • Python 3.x
            </span>
        </p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Sobre o GxLauncher")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(info_text)
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: {Theme.BG};
            }}
            QLabel {{
                color: {Theme.FG};
                min-width: 450px;
            }}
            QPushButton {{
                {Theme.get_button_style(primary=True)}
                min-width: 100px;
            }}
        """)
        msg.exec()
    
    def _check_updates(self):
        """Check for updates"""
        last_check = self.config.get("last_update_check", 0)
        
        if not self.updater.should_check(last_check):
            return
        
        update_info = self.updater.check_for_updates()
        self.config.set("last_update_check", int(time.time()))
        self.config.save()
        
        if update_info:
            update_info["current"] = UpdateChecker.CURRENT_VERSION
            dialog = UpdateDialog(update_info, self)
            dialog.exec()
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save window size
        self.config.set("window_width", self.width())
        self.config.set("window_height", self.height())
        self.config.save()
        
        # Save any pending playtime updates
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, GameCard) and widget.process:
                if widget.start_time:
                    elapsed = int(time.time() - widget.start_time)
                    if elapsed > 5:
                        self.db.update_playtime(widget.game.get("id"), elapsed)
        
        event.accept()