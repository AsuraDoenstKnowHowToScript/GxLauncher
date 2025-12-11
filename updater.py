"""
Update checker for GxLauncher
"""

import time
from typing import Optional, Dict, Any

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class UpdateChecker:
    """Checks for updates from GitHub releases"""
    
    GITHUB_REPO = "suny/gxlauncher"
    CURRENT_VERSION = "2.0.0"
    CHECK_INTERVAL = 86400  # 24 hours
    
    def __init__(self):
        self.latest_version: Optional[str] = None
        self.update_info: Optional[Dict[str, Any]] = None
    
    def should_check(self, last_check: int) -> bool:
        """Determine if enough time has passed to check again"""
        return (time.time() - last_check) > self.CHECK_INTERVAL
    
    def check_for_updates(self, timeout: int = 5) -> Optional[Dict[str, Any]]:
        """Check GitHub for latest release"""
        if not HAS_REQUESTS:
            return None
        
        try:
            url = f"https://api.github.com/repos/{self.GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                latest = data.get("tag_name", "").replace("v", "")
                
                if self._compare_versions(latest, self.CURRENT_VERSION):
                    self.latest_version = latest
                    self.update_info = {
                        "version": latest,
                        "changelog": data.get("body", "No description available"),
                        "url": data.get("html_url", ""),
                        "published": data.get("published_at", ""),
                        "download_url": self._get_download_url(data)
                    }
                    return self.update_info
            
            return None
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return None
    
    def _compare_versions(self, new: str, current: str) -> bool:
        """Compare version strings (e.g., 2.1.0 > 2.0.0)"""
        try:
            new_parts = [int(x) for x in new.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(new_parts), len(current_parts))
            new_parts.extend([0] * (max_len - len(new_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return new_parts > current_parts
        except (ValueError, AttributeError):
            return False
    
    def _get_download_url(self, release_data: Dict[str, Any]) -> str:
        """Extract download URL from release assets"""
        assets = release_data.get("assets", [])
        
        # Look for .exe or .zip file
        for asset in assets:
            name = asset.get("name", "").lower()
            if name.endswith(('.exe', '.zip')):
                return asset.get("browser_download_url", "")
        
        # Fallback to release page
        return release_data.get("html_url", "")
    
    @staticmethod
    def get_current_version() -> str:
        """Get current application version"""
        return UpdateChecker.CURRENT_VERSION