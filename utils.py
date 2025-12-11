"""
Utility functions for GxLauncher
"""

import os
import subprocess
from typing import Optional

try:
    import win32com.client
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

def resolve_shortcut(path: str) -> str:
    """Resolve .lnk shortcut to actual target path"""
    if not path.lower().endswith('.lnk'):
        return path
    
    if not HAS_WIN32:
        return path
    
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        return shortcut.Targetpath
    except Exception as e:
        print(f"Error resolving shortcut: {e}")
        return path

def format_playtime(seconds: int) -> str:
    """Format playtime seconds into readable string"""
    if seconds < 60:
        return "< 1min"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes}min"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

def format_date(timestamp: int) -> str:
    """Format unix timestamp to readable date"""
    if timestamp == 0:
        return "Nunca"
    
    from datetime import datetime
    dt = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    
    # Today
    if dt.date() == now.date():
        return f"Hoje às {dt.strftime('%H:%M')}"
    
    # Yesterday
    if (now - dt).days == 1:
        return f"Ontem às {dt.strftime('%H:%M')}"
    
    # This year
    if dt.year == now.year:
        return dt.strftime("%d/%m às %H:%M")
    
    # Other years
    return dt.strftime("%d/%m/%Y")

def launch_game(path: str, track: bool = True) -> Optional[subprocess.Popen]:
    """Launch a game executable"""
    resolved_path = resolve_shortcut(path)
    
    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Game not found: {resolved_path}")
    
    if track:
        return subprocess.Popen([resolved_path])
    else:
        os.startfile(resolved_path)
        return None

def open_file_location(path: str) -> bool:
    """Open the folder containing the file"""
    resolved_path = resolve_shortcut(path)
    
    if not os.path.exists(resolved_path):
        return False
    
    try:
        folder = os.path.dirname(resolved_path)
        os.startfile(folder)
        return True
    except Exception as e:
        print(f"Error opening location: {e}")
        return False

def validate_game_path(path: str) -> bool:
    """Validate that a game path exists and is executable"""
    if not path:
        return False
    
    resolved = resolve_shortcut(path)
    
    if not os.path.exists(resolved):
        return False
    
    # Check if it's a valid executable
    return resolved.lower().endswith(('.exe', '.lnk'))

def get_file_size(path: str) -> str:
    """Get formatted file size"""
    try:
        size = os.path.getsize(path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem operations"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename