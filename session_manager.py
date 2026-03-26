"""Session management for browser context persistence."""

import json
from pathlib import Path
from typing import Optional
from playwright.async_api import BrowserContext

from app_logger import get_logger
from config import config

log = get_logger(__name__)


class SessionManager:
    """Manages browser session persistence."""
    
    def __init__(self, session_path: Optional[str] = None):
        """Initialize session manager.
        
        Args:
            session_path: Path to session file. Defaults to config value.
        """
        self.session_path = Path(session_path or config.session_path)
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def session_exists(self) -> bool:
        """Check if a saved session file exists.
        
        Returns:
            True if session file exists and is readable, False otherwise.
        """
        return self.session_path.exists() and self.session_path.is_file()
    
    async def save_session(self, context: BrowserContext) -> None:
        """Save browser context state to file.
        
        Args:
            context: Browser context to save.
            
        Raises:
            IOError: If unable to write session file.
        """
        try:
            state = await context.storage_state()
            with open(self.session_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            log.info("Session saved to %s", self.session_path)
        except Exception as e:
            raise IOError(f"Failed to save session: {e}")
    
    async def clear_session(self) -> None:
        """Delete saved session file.
        
        Returns:
            None. Does not raise error if file doesn't exist.
        """
        try:
            if self.session_path.exists():
                self.session_path.unlink()
                log.info("Session cleared: %s", self.session_path)
            else:
                log.info("No session file to clear")
        except Exception as e:
            log.warning("Failed to clear session: %s", e)
