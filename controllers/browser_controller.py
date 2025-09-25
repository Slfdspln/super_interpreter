from playwright.sync_api import sync_playwright, Page, BrowserContext
from pathlib import Path
from typing import Optional, Dict, Any
import re, yaml, subprocess
import nest_asyncio

# Apply nest_asyncio to allow Playwright to run in existing asyncio loop
nest_asyncio.apply()

class BrowserController:
    _pw = None
    _browser = None
    _ctx: Optional[BrowserContext] = None
    _page: Optional[Page] = None

    def __init__(self, policy_path: str = "policy.yaml", headed: bool = True):
        self.policy = yaml.safe_load(Path(policy_path).read_text())
        self.allowed = set(self.policy["browser"]["allowed_domains"])
        self.confirm_navigation = bool(self.policy["browser"].get("confirm_navigation", True))
        self.max_tabs = int(self.policy["browser"].get("max_tabs", 4))
        self.headed = headed

    def _ensure(self):
        if not self._pw:
            self._pw = sync_playwright().start()
        if not self._browser:
            self._browser = self._pw.chromium.launch(headless=not self.headed)
        if not self._ctx:
            self._ctx = self._browser.new_context(accept_downloads=True)
        if not self._page:
            self._page = self._ctx.new_page()

    def _is_allowed(self, url: str) -> bool:
        domain = re.sub(r"^https?://", "", url).split("/")[0]
        return any(domain.endswith(d) for d in self.allowed)

    def goto(self, url: str) -> Dict[str, Any]:
        self._ensure()
        if not self._is_allowed(url):
            return {"ok": False, "error": f"domain not allowed: {url}"}
        if self.confirm_navigation:
            print(f"[confirm] Navigate to {url}? (y/N) ", end="")
            if input().strip().lower() != "y":
                return {"ok": False, "error": "navigation denied"}
        self._page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return {"ok": True, "title": self._page.title(), "url": self._page.url}

    def click(self, selector: str) -> Dict[str, Any]:
        self._ensure()
        self._page.click(selector, timeout=15000)
        return {"ok": True}

    def type(self, selector: str, text: str, press_enter: bool=False) -> Dict[str, Any]:
        self._ensure()
        self._page.fill(selector, text, timeout=15000)
        if press_enter:
            self._page.keyboard.press("Enter")
        return {"ok": True}

    def scrape_text(self, selector: str) -> Dict[str, Any]:
        self._ensure()
        texts = self._page.locator(selector).all_inner_texts()
        return {"ok": True, "texts": texts}

    def screenshot(self, path: str = "out/page.png") -> Dict[str, Any]:
        self._ensure()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        self._page.screenshot(path=str(p), full_page=True)
        return {"ok": True, "path": str(p.resolve())}

    def new_tab(self, url: Optional[str]=None) -> Dict[str, Any]:
        self._ensure()
        if len(self._ctx.pages) >= self.max_tabs:
            return {"ok": False, "error": "max_tabs exceeded"}
        self._page = self._ctx.new_page()
        if url:
            return self.goto(url)
        return {"ok": True}

    def type_in_google_docs(self, text: str) -> Dict[str, Any]:
        """Type text in Google Docs with proper selectors"""
        self._ensure()

        # Multiple selectors to try for Google Docs
        google_docs_selectors = [
            ".docs-texteventtarget-iframe",
            ".kix-page-content-wrap",
            ".docs-texteventtarget",
            "[contenteditable='true']",
            ".kix-paginateddocumentplugin"
        ]

        for selector in google_docs_selectors:
            try:
                # Wait for the element to be available
                element = self._page.wait_for_selector(selector, timeout=5000)
                if element:
                    element.fill(text)
                    return {"ok": True, "selector_used": selector}
            except Exception:
                continue

        # If all specific selectors fail, try typing directly
        try:
            self._page.keyboard.type(text)
            return {"ok": True, "method": "keyboard_direct"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_in_native_browser(self, url: str, browser: str = "chrome") -> Dict[str, Any]:
        """Open URL in native browser (Chrome, Brave, Safari)"""
        browser_map = {
            "chrome": "Google Chrome",
            "brave": "Brave Browser",
            "safari": "Safari",
            "firefox": "Firefox"
        }

        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        browser_name = browser_map.get(browser.lower(), browser)

        try:
            result = subprocess.run(['open', '-a', browser_name, url],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "ok": True,
                    "message": f"Opened {url} in {browser_name}",
                    "url": url,
                    "browser": browser_name
                }
            else:
                return {"ok": False, "error": f"Failed to open {browser_name}: {result.stderr}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_web_interface(self, port: int = 9000) -> Dict[str, Any]:
        """Navigate to Docker's web interface (like Portainer)"""
        docker_url = f"http://localhost:{port}"
        return self.goto(docker_url)

    def interact_with_docker_containers(self) -> Dict[str, Any]:
        """Enhanced Docker container interaction via web interface"""
        self._ensure()

        # Docker-specific selectors for robust interaction
        docker_selectors = {
            'container_row': '[data-testid="container-row"], .container-row, tr[data-container]',
            'start_button': '[data-testid="start-button"], .start-btn, button[title*="start" i]',
            'stop_button': '[data-testid="stop-button"], .stop-btn, button[title*="stop" i]',
            'restart_button': '[data-testid="restart-button"], .restart-btn, button[title*="restart" i]',
            'logs_button': '[data-testid="logs-button"], .logs-btn, button[title*="logs" i]',
            'terminal_button': '[data-testid="terminal-button"], .terminal-btn, button[title*="terminal" i]'
        }

        try:
            # Set longer timeouts for Docker operations
            self._page.set_default_timeout(30000)

            # Wait for page to be fully loaded
            self._page.wait_for_load_state("networkidle", timeout=30000)

            return {"ok": True, "selectors": docker_selectors}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_click_with_retry(self, selector: str, max_retries: int = 3) -> Dict[str, Any]:
        """Click Docker UI elements with retry logic for reliability"""
        self._ensure()

        for attempt in range(max_retries):
            try:
                # Wait for element to be visible and enabled
                element = self._page.wait_for_selector(selector, timeout=10000, state="visible")
                if element and element.is_enabled():
                    element.click()
                    return {"ok": True, "attempts": attempt + 1}

                # Try scrolling to element if not clickable
                if element:
                    element.scroll_into_view_if_needed()
                    element.click()
                    return {"ok": True, "attempts": attempt + 1}

            except Exception as e:
                if attempt == max_retries - 1:
                    return {"ok": False, "error": f"Failed after {max_retries} attempts: {str(e)}"}
                # Wait before retry
                import time
                time.sleep(1)

        return {"ok": False, "error": "All retry attempts failed"}

    def docker_type_with_clear(self, selector: str, text: str) -> Dict[str, Any]:
        """Type in Docker UI fields with proper clearing"""
        self._ensure()

        try:
            element = self._page.wait_for_selector(selector, timeout=10000)
            if element:
                # Clear field completely
                element.click()
                self._page.keyboard.press("Control+a")  # Select all
                self._page.keyboard.press("Delete")     # Delete

                # Type new text
                element.type(text)
                return {"ok": True, "text": text}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_wait_for_status_change(self, container_selector: str, expected_status: str, timeout: int = 30) -> Dict[str, Any]:
        """Wait for Docker container status to change"""
        self._ensure()

        try:
            # Wait for status change with custom timeout
            status_locator = self._page.locator(f"{container_selector} .status, {container_selector} [data-status]")
            status_locator.wait_for(lambda el: expected_status.lower() in el.text_content().lower(), timeout=timeout * 1000)

            final_status = status_locator.text_content()
            return {"ok": True, "final_status": final_status}

        except Exception as e:
            return {"ok": False, "error": f"Status change timeout: {str(e)}"}

    def docker_handle_confirmation_dialogs(self) -> Dict[str, Any]:
        """Handle Docker confirmation dialogs automatically"""
        self._ensure()

        confirmation_selectors = [
            'button[data-testid="confirm"]',
            'button.confirm-btn',
            'button:has-text("Yes")',
            'button:has-text("Confirm")',
            'button:has-text("Delete")',
            'button:has-text("Remove")'
        ]

        for selector in confirmation_selectors:
            try:
                element = self._page.wait_for_selector(selector, timeout=2000)
                if element and element.is_visible():
                    element.click()
                    return {"ok": True, "confirmed_with": selector}
            except:
                continue

        return {"ok": False, "error": "No confirmation dialog found"}

    def docker_get_container_list(self) -> Dict[str, Any]:
        """Get list of all Docker containers from web interface"""
        self._ensure()

        try:
            # Multiple possible selectors for container lists
            container_selectors = [
                '[data-testid="container-row"]',
                '.container-row',
                'tr[data-container]',
                '.docker-container-item'
            ]

            containers = []
            for selector in container_selectors:
                try:
                    elements = self._page.locator(selector).all()
                    if elements:
                        for element in elements:
                            container_info = {
                                'name': element.locator('.container-name, [data-name]').text_content() or 'Unknown',
                                'status': element.locator('.status, [data-status]').text_content() or 'Unknown',
                                'image': element.locator('.image, [data-image]').text_content() or 'Unknown'
                            }
                            containers.append(container_info)
                        break
                except:
                    continue

            return {"ok": True, "containers": containers, "count": len(containers)}

        except Exception as e:
            return {"ok": False, "error": str(e)}
