"""
Configuration management for GxLauncher
"""

import json
import os
from typing import Dict, Any

class Config:
    """Manages application configuration"""
    
    CONFIG_FILE = "config.json"
    
    DEFAULT_CONFIG = {
        "grid_columns": 4,
        "card_size": "medium",
        "close_on_launch": False,
        "track_playtime": True,
        "show_playtime": True,
        "sort_by": "name",
        "sort_order": "asc",
        "window_width": 1400,
        "window_height": 900,
        "last_update_check": 0,
        "auto_check_updates": True,
        "show_sidebar": True,
        "theme": "dark"
    }
    
    def __init__(self):
        self.config = self._load()
    
    def _load(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**self.DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}")
        
        return self.DEFAULT_CONFIG.copy()
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default=None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def update(self, values: Dict[str, Any]) -> None:
        """Update multiple configuration values"""
        self.config.update(values)
    
    def reset(self) -> None:
        """Reset to default configuration"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()