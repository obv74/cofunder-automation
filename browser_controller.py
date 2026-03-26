"""Browser controller for orchestrating Playwright operations."""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright

from app_logger import get_logger
from config import config
from session_manager import SessionManager
from auth_handler import AuthenticationHandler

log = get_logger(__name__)


class BrowserController:
    """Orchestrates browser operations and session management."""
    
    def __init__(self, headless: bool = None):
        """Initialize browser controller.
        
        Args:
            headless: Override config headless setting. If None, uses config value.
        """
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.session_manager = SessionManager()
        self.auth_handler = AuthenticationHandler()
        self.headless = headless if headless is not None else config.headless
    
    async def initialize(self) -> None:
        """Initialize Playwright browser.
        
        Raises:
            RuntimeError: If browser fails to launch.
        """
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless
            )
            mode = "headless" if self.headless else "visible"
            log.info("Browser initialized (%s mode)", mode)
        except Exception as e:
            raise RuntimeError(f"Failed to launch browser: {e}")
    
    async def get_authenticated_context(self) -> BrowserContext:
        """Get authenticated browser context.
        
        Loads existing session if available, otherwise performs manual login.
        
        Returns:
            Authenticated browser context ready for scraping.
            
        Raises:
            RuntimeError: If unable to obtain authenticated context.
        """
        # Check for existing session
        if await self.session_manager.session_exists():
            log.info("Found existing session, attempting to load...")
            
            try:
                # Load session
                session_path = Path(config.session_path)
                with open(session_path, 'r', encoding='utf-8') as f:
                    storage_state = json.load(f)
                
                self.context = await self.browser.new_context(
                    storage_state=storage_state
                )
                
                # Validate session
                if await self._validate_session():
                    log.info("Session is valid and loaded")
                    return self.context
                else:
                    log.warning("Session is invalid or expired")
                    await self.context.close()
                    await self.session_manager.clear_session()
                    
            except (json.JSONDecodeError, FileNotFoundError) as e:
                log.warning("Session file corrupted: %s", e)
                await self.session_manager.clear_session()
            except Exception as e:
                log.error("Error loading session: %s", e)
                if self.context:
                    await self.context.close()
        
        log.info("No valid session found. Manual login required.")
        self.context = await self.auth_handler.perform_manual_login(self.browser)
        
        # Save the new session
        await self.session_manager.save_session(self.context)
        
        return self.context
    
    async def _validate_session(self) -> bool:
        """Validate that the loaded session is still valid.
        
        Returns:
            True if session is valid, False otherwise.
        """
        try:
            page = await self.context.new_page()
            
            # Navigate to feed (requires auth); if not logged in we get redirected to login
            for attempt in range(config.retry_attempts):
                try:
                    await page.goto(
                        "https://cofounderslab.com/feed",
                        timeout=30000,
                        wait_until="domcontentloaded"
                    )
                    break
                except Exception as e:
                    if attempt < config.retry_attempts - 1:
                        log.warning("Navigation attempt %s failed, retrying...", attempt + 1)
                        await asyncio.sleep(config.retry_delay)
                    else:
                        raise
            
            # Check if we're authenticated
            is_valid = await self.auth_handler.is_authenticated(page)
            await page.close()
            
            return is_valid
            
        except Exception as e:
            log.warning("Session validation failed: %s", e)
            return False
    
    async def close(self) -> None:
        """Close browser and cleanup resources. Safe to call when already closed or crashed."""
        closed = False
        if self.context:
            try:
                await self.context.close()
                closed = True
            except Exception:
                pass
            self.context = None
        if self.browser:
            try:
                await self.browser.close()
                closed = True
            except Exception:
                pass
            self.browser = None
        if self.playwright:
            try:
                await self.playwright.stop()
                closed = True
            except Exception:
                pass
            self.playwright = None
        if closed:
            log.info("Browser closed")
        await asyncio.sleep(0.25)
