"""Main CLI entry point for CoFoundersLab scraper bot."""

import asyncio
import sys
import argparse
from pathlib import Path
from typing import NoReturn

from playwright.async_api import Page

from app_logger import get_logger, setup_logging
from browser_controller import BrowserController
from session_manager import SessionManager
from config import config
from telegram_alerts import send_alert

# Repost rule: if best matched post position is 4+ (below top 3), create a new post.

# Timeouts from config (ms) for use in wait_for_selector / goto
_TO = config.selector_timeout_ms
_PAGE_TO = config.page_load_timeout_ms

FEED_URL = "https://cofounderslab.com/feed"

log = get_logger(__name__)


async def login_command() -> int:
    """Execute login command.
    
    Always uses visible browser so you can complete manual login.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Login requires visible browser for manual login
    controller = BrowserController(headless=False)
    
    try:
        log.info("Starting login process...")
        await controller.initialize()
        context = await controller.get_authenticated_context()
        # Keep a page open so the browser window doesn't close (validation closes its page)
        keep_open_page = await context.new_page()
        try:
            await keep_open_page.goto("https://cofounderslab.com/feed", wait_until="domcontentloaded", timeout=_PAGE_TO)
        except Exception:
            pass  # Page is still open; window stays open
        # Always wait for user to type "start" before closing (browser stays open)
        log.info("Browser will stay open until you type 'start'. When ready, type 'start' and press Enter.")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: input("Type 'start' and press Enter when ready: "))
        # Save session now (after feed was open) so scrape gets full cookies/localStorage
        await controller.session_manager.save_session(context)
        log.info("LOGIN SUCCESSFUL — session saved. You can run scraping without logging in again.")
        return 0
        
    except KeyboardInterrupt:
        log.info("Login cancelled by user")
        return 1
    except Exception as e:
        log.error("Error during login: %s", e)
        send_alert(f"Login error: {e}", prefix="CoFounder Login")
        return 1
    finally:
        await controller.close()


async def scrape_command(headless: bool = False, max_checks: int | None = None) -> int:
    """Execute scrape command - automatically insert text from input.txt.
    
    Args:
        headless: If True, run browser in headless mode (invisible).
        max_checks: Max monitoring cycles (None=config default, 0=run once and exit, 1+=limited).
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    controller = BrowserController(headless=headless)
    session_manager = SessionManager()
    
    try:
        # Check if session exists
        if not await session_manager.session_exists():
            log.error("No saved session found. Run: python main.py login")
            send_alert("No saved session. Run: python main.py login", prefix="CoFounder Scrape")
            return 1
        
        # Check if input file exists (next to main.py / project root)
        _project_dir = Path(__file__).resolve().parent
        input_file = _project_dir / "input.txt"
        if not input_file.exists():
            log.error("input.txt not found. Create input.txt in the project root.")
            send_alert("input.txt not found in project root.", prefix="CoFounder Scrape")
            return 1
        
        # Read all text from input file as one post
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        
        if not text:
            log.error("input.txt is empty.")
            send_alert("input.txt is empty.", prefix="CoFounder Scrape")
            return 1
        
        log.info("Loaded text from input.txt (%s characters)", len(text))
        
        await controller.initialize()
        context = await controller.get_authenticated_context()
        
        log.info("AUTO-POST MODE")
        
        # Navigate to feed page
        page = await context.new_page()
        log.info("Navigating to feed page...")
        await page.goto("https://cofounderslab.com/feed", wait_until="networkidle", timeout=_PAGE_TO)
        
        log.info("Waiting for page to render...")
        await asyncio.sleep(3)
        
        # Selectors
        # More specific selector - only match post cards that have the post content structure
        post_cards_selector = 'div.rounded-xl.border.shadow-sm.mb-3 div.line-clamp-6'
        input_selector = 'input[placeholder="What\'s happening?"]'
        textarea_selector = 'textarea[name="text"]'
        post_button_selector = 'button:has-text("Post")'

        async def ensure_on_feed(p: Page) -> None:
            """Navigate to feed if not already there (so composer and feed content are present)."""
            try:
                current = p.url
                if "cofounderslab.com/feed" not in current:
                    log.info("Not on feed page (%s), navigating to feed...", current[:50])
                    await p.goto(FEED_URL, wait_until="networkidle", timeout=_PAGE_TO)
                    await asyncio.sleep(config.feed_render_wait_sec)
            except Exception as e:
                log.warning("ensure_on_feed: %s", e)

        async def recover_feed_page(p: Page) -> None:
            """Force a full reload of the feed page so the next check/create starts from a clean state."""
            try:
                log.info("Recovering feed page (full reload) for next cycle...")
                await p.goto(FEED_URL, wait_until="networkidle", timeout=_PAGE_TO)
                await asyncio.sleep(config.feed_render_wait_sec)
            except Exception as e:
                log.warning("recover_feed_page: %s", e)

        async def create_new_post(p: Page, post_text: str, log_prefix: str = "") -> bool:
            """Try to create a new post with retries. Returns True if successful."""
            await ensure_on_feed(p)
            for attempt in range(1, config.create_post_retries + 1):
                try:
                    await p.wait_for_selector(input_selector, timeout=_TO)
                    await p.click(input_selector)
                    await asyncio.sleep(1)
                    await p.wait_for_selector(textarea_selector, timeout=_TO)
                    await p.fill(textarea_selector, post_text)
                    await asyncio.sleep(2)
                    post_btn = await p.wait_for_selector(post_button_selector, timeout=_TO)
                    is_disabled = await post_btn.is_disabled()
                    if not is_disabled:
                        await post_btn.click()
                        if log_prefix:
                            log.info("%sNew post created", log_prefix)
                        await asyncio.sleep(5)
                        return True
                    if log_prefix:
                        log.warning("%sPost button is disabled", log_prefix)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    if log_prefix:
                        log.warning("%sAttempt %s/%s: %s", log_prefix, attempt, config.create_post_retries, e)
                    if attempt < config.create_post_retries:
                        # Retry from a fresh feed page so we don't keep failing in the same broken state
                        await recover_feed_page(p)
                        await asyncio.sleep(config.retry_delay_create_post_sec)
            return False

        # Use more text for matching - first 100 chars or 2 lines
        text_lines = text.split('\n')
        if len(text_lines) >= 2:
            match_text = f"{text_lines[0]}\n{text_lines[1]}"[:100]
        else:
            match_text = text[:100]
        
        # Function to check post position (best rank among all matching posts)
        async def check_post_position():
            # Get all post content elements
            await page.wait_for_selector(post_cards_selector, timeout=_TO)
            post_content_elements = await page.query_selector_all(post_cards_selector)
            
            # Get parent cards for each content element
            post_cards = []
            for element in post_content_elements:
                # Navigate up to find the parent card
                parent_handle = await element.evaluate_handle('el => el.closest("div.rounded-xl.border.shadow-sm.mb-3")')
                parent = parent_handle.as_element()
                if parent:
                    post_cards.append(parent)
            
            log.debug("Checking %s posts; looking for: %s...", len(post_cards), match_text[:50])
            
            matched_positions = []
            for idx, card in enumerate(post_cards, 1):
                try:
                    post_text_element = await card.query_selector('div.line-clamp-6')
                    if post_text_element:
                        post_content = await post_text_element.inner_text()
                        log.debug("Post %s: %s...", idx, post_content[:50])
                        
                        # More strict matching - check if match_text is in post content
                        if match_text in post_content:
                            matched_positions.append(idx)
                except Exception as e:
                    log.debug("Error checking post %s: %s", idx, e)
                    continue
            
            if not matched_positions:
                log.debug("No match found")
                return None, post_cards

            best_position = min(matched_positions)
            log.debug("MATCH FOUND at positions %s (best=%s)", matched_positions, best_position)
            return best_position, post_cards
        
        log.info("Checking if post already exists in feed...")
        post_position, post_cards = await check_post_position()
        log.info("Found %s posts in feed", len(post_cards))
        
        # Determine action based on position
        need_to_post = False
        if post_position is not None:
            log.info("YOUR POST FOUND AT POSITION: %s", post_position)
            
            if post_position <= 3:
                log.info("Post is in top 3 positions.")
            else:
                log.warning("Post is at position %s (below top 3) — reposting.", post_position)
                need_to_post = True
        else:
            log.info("Post not found in feed.")
            need_to_post = True
        
        # Create new post if needed
        if need_to_post:
            log.info("Creating new post...")
            if await create_new_post(page, text):
                log.info("Post submitted")
                await page.reload(wait_until="networkidle", timeout=_PAGE_TO)
                await asyncio.sleep(3)
                post_position, _ = await check_post_position()
                if post_position:
                    log.info("YOUR POST IS NOW AT POSITION: %s", post_position)
            else:
                log.error("Failed to create initial post after retries; will retry in monitoring.")
                send_alert("Failed to create initial post after retries. Will retry in monitoring.", prefix="CoFounder Scrape")
        
        # Monitoring (continuous or limited by max_checks)
        interval = config.monitor_interval_sec
        # Explicit --checks 0 = run once and exit. No --checks = use config (0 = unlimited 24/7).
        if max_checks is not None and max_checks == 0:
            log.info("Run once — no monitoring. Exiting after initial check/post.")
            return 0
        max_checks_effective = max_checks if max_checks is not None else config.max_monitor_checks
        if max_checks_effective > 0:
            log.info("LIMITED RUN — %s check(s), every %s seconds. Then exit.", max_checks_effective, interval)
        else:
            log.info("CONTINUOUS MONITORING ACTIVE — checking every %s seconds. Ctrl+C to stop.", interval)
        exit_due_to_logout = False
        post_not_found_previous_run = False  # only set True when we actually got None from check (not on timeout)
        check_count = 0

        while True:
            try:
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                log.info("Shutting down...")
                break
            
            if page.is_closed():
                log.info("Browser closed. Exiting...")
                break
            
            if max_checks_effective > 0 and check_count >= max_checks_effective:
                log.info("Reached max checks (%s). Exiting.", max_checks_effective)
                break

            try:
                # If we couldn't find post last run (confirmed), create new post before refresh
                if post_not_found_previous_run:
                    log.warning("Post was not found last run — creating new post immediately (before refresh)...")
                    ok = await create_new_post(page, text, log_prefix="  ")
                    if ok:
                        post_not_found_previous_run = False
                        await asyncio.sleep(3)
                    else:
                        send_alert("Post not found; create new post failed (before refresh).", prefix="CoFounder Monitor")
                        await recover_feed_page(page)

                log.info("Refreshing feed...")
                await page.reload(wait_until="networkidle", timeout=_PAGE_TO)
                await ensure_on_feed(page)
                await asyncio.sleep(config.feed_render_wait_sec)

                # Detect explicit login button (logged-out state) every cycle.
                # If found, re-import session and restart from a fresh context.
                try:
                    login_button_visible = await controller.auth_handler.is_login_button_visible(page)
                except Exception as e:
                    login_button_visible = False
                    log.debug("Login button detection failed: %s", e)

                if login_button_visible:
                    log.error("Detected login button on page (logged out). Re-importing session and restarting monitoring...")
                    try:
                        # Close existing browser/context cleanly, then start a fresh one
                        await controller.close()
                        await controller.initialize()
                        context = await controller.get_authenticated_context()
                        page = await context.new_page()
                        await ensure_on_feed(page)
                        post_not_found_previous_run = False
                        check_count = 0
                        # Skip the rest of this loop iteration; next cycle continues with fresh session
                        continue
                    except Exception as e:
                        log.error("Failed to re-import session after logout detection: %s", e)
                        send_alert(
                            f"Failed to re-import session after logout detection: {e}",
                            prefix="CoFounder Monitor",
                        )
                        exit_due_to_logout = True
                        break
                
                current_position, post_cards = await check_post_position()
                check_count += 1
                
                if current_position is None:
                    log.warning("Post not found in feed. Will create new post immediately before next refresh.")
                    post_not_found_previous_run = True
                    
                elif current_position <= 3:
                    post_not_found_previous_run = False
                    log.info("Position: %s (Top 3)", current_position)
                else:
                    post_not_found_previous_run = False
                    log.warning("Position: %s (below top 3) - reposting now.", current_position)
                    try:
                        if await create_new_post(page, text, log_prefix="  "):
                            log.info("Repost completed")
                            await page.reload(wait_until="networkidle", timeout=_PAGE_TO)
                            await asyncio.sleep(2)
                    except Exception as e:
                        log.error("Error during repost: %s", e)
                        send_alert(f"Repost error: {e}", prefix="CoFounder Monitor")
                        
            except Exception as e:
                log.error("Error during check: %s — continuing to next check.", e)
                send_alert(f"Check error: {e}", prefix="CoFounder Monitor")
                # Do NOT set post_not_found_previous_run here — timeout/error means we don't know;
                # setting it would trigger unnecessary "create new post" and more timeouts.
                try:
                    if not page.is_closed():
                        if not await controller.auth_handler.is_authenticated(page):
                            log.error("Session expired (logged out). Stopping monitor.")
                            send_alert(
                                "Session expired (logged out). Please run: python main.py login",
                                prefix="CoFounder Monitor",
                            )
                            exit_due_to_logout = True
                            break
                        # Recover feed so next cycle doesn't repeat the same timeout (e.g. stuck layout)
                        await recover_feed_page(page)
                except Exception:
                    pass
                continue
        
        return 1 if exit_due_to_logout else 0
        
    except KeyboardInterrupt:
        log.info("Stopped by user")
        return 1
    except Exception as e:
        log.error("Scrape error: %s", e)
        send_alert(f"Scrape error: {e}", prefix="CoFounder Scrape")
        return 1
    finally:
        await controller.close()
        await asyncio.sleep(0.5)


async def clear_session_command() -> int:
    """Execute clear-session command.
    
    Returns:
        Exit code (0 for success, 1 for error).
    """
    session_manager = SessionManager()
    
    try:
        await session_manager.clear_session()
        log.info("SESSION CLEARED — you will need to log in again on next run.")
        return 0
        
    except Exception as e:
        log.error("Error clearing session: %s", e)
        send_alert(f"Clear session error: {e}", prefix="CoFounder")
        return 1


def main() -> NoReturn:
    """Main CLI entry point."""
    setup_logging(log_level=config.log_level, log_file=config.log_file or None)
    parser = argparse.ArgumentParser(
        description="CoFoundersLab Scraper Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  login         Perform manual login and save session
  scrape        Run scraper with saved session (visible browser)
  clear-session Clear saved session data

Examples:
  python main.py login
  python main.py scrape
  python main.py scrape --headless
  python main.py scrape --headless --checks 0   (run once, no monitoring)
  python main.py scrape --headless --checks 5   (5 checks then exit)
  python main.py clear-session
        """
    )
    
    parser.add_argument(
        'command',
        choices=['login', 'scrape', 'clear-session'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (invisible)'
    )
    
    parser.add_argument(
        '--checks',
        type=int,
        default=None,
        metavar='N',
        help='Max monitoring cycles (0=run once and exit, 1+=limited runs). Omit for config default or unlimited.'
    )
    
    args = parser.parse_args()
    
    if args.command == 'login':
        exit_code = asyncio.run(login_command())
    elif args.command == 'scrape':
        exit_code = asyncio.run(scrape_command(headless=args.headless, max_checks=args.checks))
    elif args.command == 'clear-session':
        exit_code = asyncio.run(clear_session_command())
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
