"""
Database management for GxLauncher
Handles game library storage and operations
"""

import json
import os
import time
from typing import List, Dict, Optional, Any

class Database:
    """Manages game library database"""
    
    DB_FILE = "games.json"
    
    def __init__(self):
        self.games: List[Dict[str, Any]] = []
        self._ensure_db_exists()
        self.load()
    
    def _ensure_db_exists(self) -> None:
        """Create database file if it doesn't exist"""
        if not os.path.exists(self.DB_FILE):
            with open(self.DB_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def load(self) -> bool:
        """Load games from database"""
        try:
            with open(self.DB_FILE, 'r', encoding='utf-8') as f:
                self.games = json.load(f)
                # Ensure all games have required fields
                for game in self.games:
                    self._ensure_game_fields(game)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading database: {e}")
            self.games = []
            return False
    
    def save(self) -> bool:
        """Save games to database"""
        try:
            with open(self.DB_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving database: {e}")
            return False
    
    def _ensure_game_fields(self, game: Dict[str, Any]) -> None:
        """Ensure game has all required fields"""
        defaults = {
            "id": str(int(time.time() * 1000)),
            "name": "Unknown Game",
            "path": "",
            "cover": "",
            "playtime": 0,
            "last_played": 0,
            "added": int(time.time()),
            "favorite": False,
            "tags": [],
            "notes": ""
        }
        
        for key, value in defaults.items():
            if key not in game:
                game[key] = value
    
    def add_game(self, game_data: Dict[str, Any]) -> bool:
        """Add a new game to the library"""
        # Check if game already exists
        if self.get_game_by_path(game_data.get("path", "")):
            return False
        
        game = game_data.copy()
        self._ensure_game_fields(game)
        self.games.append(game)
        return self.save()
    
    def update_game(self, game_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing game"""
        game = self.get_game_by_id(game_id)
        if game:
            game.update(updates)
            return self.save()
        return False
    
    def remove_game(self, game_id: str) -> bool:
        """Remove a game from the library"""
        self.games = [g for g in self.games if g.get("id") != game_id]
        return self.save()
    
    def get_game_by_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get game by ID"""
        for game in self.games:
            if game.get("id") == game_id:
                return game
        return None
    
    def get_game_by_path(self, path: str) -> Optional[Dict[str, Any]]:
        """Get game by executable path"""
        for game in self.games:
            if game.get("path") == path:
                return game
        return None
    
    def get_all_games(self) -> List[Dict[str, Any]]:
        """Get all games"""
        return self.games.copy()
    
    def search_games(self, query: str) -> List[Dict[str, Any]]:
        """Search games by name"""
        query = query.lower()
        return [g for g in self.games if query in g.get("name", "").lower()]
    
    def filter_games(self, favorites_only: bool = False, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Filter games by criteria"""
        filtered = self.games.copy()
        
        if favorites_only:
            filtered = [g for g in filtered if g.get("favorite", False)]
        
        if tags:
            filtered = [g for g in filtered if any(t in g.get("tags", []) for t in tags)]
        
        return filtered
    
    def sort_games(self, by: str = "name", reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort games by specified field"""
        sort_keys = {
            "name": lambda g: g.get("name", "").lower(),
            "playtime": lambda g: g.get("playtime", 0),
            "last_played": lambda g: g.get("last_played", 0),
            "added": lambda g: g.get("added", 0)
        }
        
        key_func = sort_keys.get(by, sort_keys["name"])
        return sorted(self.games, key=key_func, reverse=reverse)
    
    def update_playtime(self, game_id: str, seconds: int) -> bool:
        """Update game playtime"""
        game = self.get_game_by_id(game_id)
        if game:
            game["playtime"] = game.get("playtime", 0) + seconds
            game["last_played"] = int(time.time())
            return self.save()
        return False
    
    def get_total_playtime(self) -> int:
        """Get total playtime across all games"""
        return sum(g.get("playtime", 0) for g in self.games)
    
    def export_library(self, filepath: str) -> bool:
        """Export library to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.games, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error exporting library: {e}")
            return False
    
    def import_library(self, filepath: str, merge: bool = True) -> bool:
        """Import library from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            
            if not isinstance(imported, list):
                return False
            
            if merge:
                # Merge with existing, skip duplicates
                existing_paths = {g.get("path") for g in self.games}
                for game in imported:
                    if game.get("path") not in existing_paths:
                        self._ensure_game_fields(game)
                        self.games.append(game)
            else:
                # Replace entirely
                self.games = imported
                for game in self.games:
                    self._ensure_game_fields(game)
            
            return self.save()
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error importing library: {e}")
            return False
    
    def reset_stats(self) -> bool:
        """Reset all playtime statistics"""
        for game in self.games:
            game["playtime"] = 0
            game["last_played"] = 0
        return self.save()