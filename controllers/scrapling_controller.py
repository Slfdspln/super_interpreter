"""
Scrapling Controller - Adaptive Web Scraping
Uses Scrapling library for advanced, self-healing web scraping
"""

import warnings
warnings.filterwarnings("ignore")

from scrapling.fetchers import Fetcher, StealthyFetcher, PlayWrightFetcher
from typing import Dict, Any, List, Optional
import yaml
import re
from pathlib import Path

class ScraplingController:
    def __init__(self, policy_path: str = "policy.yaml"):
        """Initialize Scrapling controller with policy settings"""
        try:
            self.policy = yaml.safe_load(Path(policy_path).read_text())
            self.allowed = set(self.policy["browser"]["allowed_domains"])
        except Exception:
            # Fallback if policy file doesn't exist
            self.allowed = {"docs.google.com", "news.google.com", "trends.google.com",
                           "reddit.com", "hacker-news.firebaseio.com", "hn.algolia.com"}

        # Enable adaptive mode for all fetchers
        StealthyFetcher.adaptive = True

    def _is_allowed(self, url: str) -> bool:
        """Check if URL domain is allowed by policy"""
        domain = re.sub(r"^https?://", "", url).split("/")[0]
        return any(domain.endswith(d) for d in self.allowed)

    def fetch_basic(self, url: str) -> Dict[str, Any]:
        """Basic HTTP fetch using Scrapling's Fetcher"""
        try:
            if not self._is_allowed(url):
                return {"ok": False, "error": f"Domain not allowed: {url}"}

            fetcher = Fetcher()
            page = fetcher.get(url)

            # Extract title using CSS selector
            title_element = page.css_first('title')
            title = title_element.text if title_element else "No title"

            return {
                "ok": True,
                "status": page.status,
                "title": title,
                "url": page.url,
                "content": page.text[:1000],  # First 1000 chars
                "page": page  # Full page object for further operations
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def fetch_stealth(self, url: str, headless: bool = True) -> Dict[str, Any]:
        """Stealth fetch to bypass anti-bot protection"""
        try:
            if not self._is_allowed(url):
                return {"ok": False, "error": f"Domain not allowed: {url}"}

            fetcher = StealthyFetcher()
            page = fetcher.get(url, headless=headless, network_idle=True)

            # Extract title using CSS selector
            title_element = page.css_first('title')
            title = title_element.text if title_element else "No title"

            return {
                "ok": True,
                "status": page.status,
                "title": title,
                "url": page.url,
                "content": page.text[:1000],
                "page": page
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def fetch_dynamic(self, url: str, headless: bool = True, wait_time: int = 3) -> Dict[str, Any]:
        """Dynamic fetch with full browser automation"""
        try:
            if not self._is_allowed(url):
                return {"ok": False, "error": f"Domain not allowed: {url}"}

            fetcher = PlayWrightFetcher()
            page = fetcher.get(url, headless=headless, network_idle=True)

            # Extract title using CSS selector
            title_element = page.css_first('title')
            title = title_element.text if title_element else "No title"

            return {
                "ok": True,
                "status": page.status,
                "title": title,
                "url": page.url,
                "content": page.text[:1000],
                "page": page
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def scrape_elements(self, url: str, css_selectors: List[str], adaptive: bool = True) -> Dict[str, Any]:
        """Scrape specific elements with adaptive capability"""
        try:
            # Try stealth fetch first for better success rate
            page_result = self.fetch_stealth(url)
            if not page_result["ok"]:
                return page_result

            page = page_result["page"]
            results = {}

            for selector in css_selectors:
                try:
                    # Use adaptive mode to handle website changes
                    elements = page.css(selector, adaptive=adaptive)
                    if elements:
                        results[selector] = [elem.text.strip() for elem in elements if elem.text.strip()]
                    else:
                        results[selector] = []
                except Exception as e:
                    results[selector] = {"error": str(e)}

            # Extract title using CSS selector
            title_element = page.css_first('title')
            title = title_element.text if title_element else "No title"

            return {
                "ok": True,
                "url": url,
                "title": title,
                "results": results
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def scrape_trending_news(self) -> Dict[str, Any]:
        """Scrape trending news from multiple sources"""
        try:
            news_sources = [
                {
                    "name": "Google Trends",
                    "url": "https://trends.google.com/trends/trendingsearches/daily",
                    "selectors": [".feed-item-header", ".summary-text", ".related-queries"]
                },
                {
                    "name": "Reddit Popular",
                    "url": "https://www.reddit.com/r/popular/.json",
                    "type": "json"
                }
            ]

            results = {}

            for source in news_sources:
                try:
                    if source.get("type") == "json":
                        # Handle JSON APIs
                        page_result = self.fetch_basic(source["url"])
                        if page_result["ok"]:
                            results[source["name"]] = {
                                "status": "success",
                                "content": "JSON data retrieved"
                            }
                    else:
                        # Handle HTML scraping
                        scrape_result = self.scrape_elements(source["url"], source["selectors"])
                        if scrape_result["ok"]:
                            results[source["name"]] = scrape_result["results"]
                        else:
                            results[source["name"]] = {"error": scrape_result["error"]}
                except Exception as e:
                    results[source["name"]] = {"error": str(e)}

            return {
                "ok": True,
                "sources": results,
                "summary": self._summarize_trending(results)
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _summarize_trending(self, results: Dict) -> str:
        """Create a summary of trending topics"""
        trends = []

        for source, data in results.items():
            if isinstance(data, dict) and "error" not in data:
                for selector, items in data.items():
                    if isinstance(items, list) and items:
                        trends.extend(items[:3])  # Top 3 from each source

        if trends:
            return f"Current trending topics: {', '.join(trends[:5])}"
        else:
            return "Unable to retrieve trending topics at this time"

    def scrape_google_docs_ready(self) -> Dict[str, Any]:
        """Check if Google Docs is ready for content input"""
        try:
            page_result = self.fetch_dynamic("https://docs.new")
            if page_result["ok"]:
                page = page_result["page"]

                # Look for the document editor
                editor_selectors = [
                    ".kix-page-content-wrap",
                    ".docs-texteventtarget-iframe",
                    ".kix-paginateddocumentplugin"
                ]

                for selector in editor_selectors:
                    elements = page.css(selector)
                    if elements:
                        return {
                            "ok": True,
                            "ready": True,
                            "message": "Google Docs editor is ready",
                            "selector": selector
                        }

                return {
                    "ok": True,
                    "ready": False,
                    "message": "Google Docs not fully loaded"
                }
            else:
                return page_result
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def adaptive_scrape(self, url: str, selectors: List[str], fallback_selectors: List[str] = None) -> Dict[str, Any]:
        """Advanced adaptive scraping with fallback selectors"""
        try:
            # First attempt with primary selectors
            result = self.scrape_elements(url, selectors, adaptive=True)

            if result["ok"] and any(result["results"].values()):
                return result

            # If no results and fallback selectors provided, try them
            if fallback_selectors:
                fallback_result = self.scrape_elements(url, fallback_selectors, adaptive=True)
                if fallback_result["ok"]:
                    return {
                        "ok": True,
                        "url": url,
                        "title": fallback_result["title"],
                        "results": fallback_result["results"],
                        "fallback_used": True
                    }

            return result
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_page_text(self, url: str, max_length: int = 5000) -> Dict[str, Any]:
        """Get clean text content from a page"""
        try:
            page_result = self.fetch_stealth(url)
            if page_result["ok"]:
                page = page_result["page"]
                text = page.text[:max_length]
                # Extract title using CSS selector
                title_element = page.css_first('title')
                title = title_element.text if title_element else "No title"

                return {
                    "ok": True,
                    "url": url,
                    "title": title,
                    "text": text,
                    "length": len(text)
                }
            else:
                return page_result
        except Exception as e:
            return {"ok": False, "error": str(e)}