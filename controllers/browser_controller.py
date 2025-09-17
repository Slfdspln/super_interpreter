from playwright.sync_api import sync_playwright, Page, BrowserContext
from pathlib import Path
from typing import Optional, Dict, Any
import re, yaml, subprocess

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
