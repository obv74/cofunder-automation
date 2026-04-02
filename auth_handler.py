"""Authentication handler for manual login flow."""

import asyncio
from playwright.async_api import Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError

from app_logger import get_logger
from config import config

log = get_logger(__name__)


class AuthenticationHandler:
    """Handles manual login flow and authentication detection."""
    
    def __init__(self):
        """Initialize authentication handler."""
        self.login_url = config.login_url
        self.timeout = config.login_timeout
    
    async def perform_manual_login(self, browser: Browser) -> BrowserContext:
        """Launch browser and wait for manual login.
        
        Args:
            browser: Playwright browser instance.
            
        Returns:
            Authenticated browser context.
            
        Raises:
            TimeoutError: If login not completed within timeout.
            RuntimeError: If browser is closed during login.
        """
        log.info("MANUAL LOGIN REQUIRED — opening %s", self.login_url)
        log.info("Complete login in the browser (2FA, popups, etc.). When you see 'Login detected!', type 'start' in the terminal.")
        
        # Create new context
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to login page
            await page.goto(self.login_url, timeout=30000)
            
            # Wait for authentication
            authenticated = False
            start_time = asyncio.get_running_loop().time()
            
            while not authenticated:
                # Check if timeout exceeded
                elapsed = (asyncio.get_running_loop().time() - start_time) * 1000
                if elapsed > self.timeout:
                    raise TimeoutError(
                        f"Login timeout after {self.timeout/1000} seconds. "
                        "Please try again."
                    )
                
                # Check if browser/page is closed
                if page.is_closed():
                    raise RuntimeError("Browser was closed during login")
                
                # Check authentication status
                authenticated = await self.is_authenticated(page)
                
                if not authenticated:
                    await asyncio.sleep(1)  # Check every second
            
            # Login detected; main.py will prompt for "start" before closing
            log.info("Login detected! Return to the terminal and type 'start' when ready.")
            return context
            
        except PlaywrightTimeoutError:
            await context.close()
            raise TimeoutError("Failed to load login page. Please check your internet connection.")
        except Exception:
            await context.close()
            raise
    
    async def is_authenticated(self, page: Page) -> bool:
        """Check if user is authenticated.
        
        Only returns True when on a page that clearly indicates a completed login
        (e.g. feed). The homepage (cofounderslab.com/) can be seen by both
        logged-in and logged-out users, so we do not treat it as authenticated.
        
        Args:
            page: Playwright page instance.
            
        Returns:
            True if authenticated, False otherwise.
        """
        current_url = page.url.lower()

        # Must be on cofounderslab
        if "cofounderslab.com" not in current_url:
            return False

        # Login/signup routes are always unauthenticated.
        if "/login" in current_url or "/signup" in current_url or "/sign-in" in current_url:
            return False

        # If login CTA is visible, user is logged out even if URL still looks like /feed.
        if await self.is_login_button_visible(page):
            return False

        # Positive authenticated signal: post composer input shown on feed.
        try:
            composer = page.locator('input[placeholder="What\'s happening?"]')
            if await composer.first.is_visible():
                return True
        except Exception:
            pass

        # Fallback URL-based check for common authenticated areas.
        if "cofounderslab.com/feed" in current_url:
            return True
        if "/messages" in current_url or "/profile" in current_url or "/dashboard" in current_url:
            return True

        # Homepage (/) or unknown path: do not assume logged in.
        return False

    async def is_login_button_visible(self, page: Page) -> bool:
        """Detect the specific 'Login' button element on the page.

        This checks for the CoFoundersLab login button with the exact Tailwind
        class combination and inner text "Login" that appears when the user is
        logged out.
        """
        try:
            # Prefer resilient text/role selectors over fragile utility-class chains.
            candidates = [
                page.get_by_role("button", name="Login"),
                page.get_by_text("Login", exact=True),
                page.get_by_text("Sign in", exact=False),
                page.locator("a[href*='/login']"),
                page.locator("button:has-text('Login')"),
            ]
            for locator in candidates:
                try:
                    if await locator.first.is_visible():
                        return True
                except Exception:
                    continue
            return False
        except Exception:
            return False
