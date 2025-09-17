#!/usr/bin/env python3
import warnings
import os

# Suppress all warnings
warnings.filterwarnings("ignore")
os.environ["PYTHONWARNINGS"] = "ignore"

# Suppress urllib3 warnings specifically
try:
    import urllib3
    urllib3.disable_warnings()
    warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)
except:
    pass

from interpreter import interpreter

# Preload your controllers into the same Python process the model will use.
init_code = r"""
from controllers.browser_controller import BrowserController
from controllers.scrapling_controller import ScraplingController
from controllers.os_controller import OSController
from controllers.app_controller_macos import MacApp, launch_any_app, windsurf, chrome, safari, vscode, terminal, finder, brave
from controllers.memory import save_doc, list_docs, get_doc, search_docs, get_stats, quick_save

browser = BrowserController("policy.yaml", headed=True)
scraper = ScraplingController("policy.yaml")
osctl   = OSController("policy.yaml")
windsurf = MacApp("Windsurf")

# Memory functions are available directly
memory_stats = get_stats()

print(f"[setup] browser, osctl, windsurf, scraper, and memory ({memory_stats['total_docs']} docs, {memory_stats['embedding_count']} embeddings) are ready.")
"""

# Run the init code inside the model's Python environment
interpreter.computer.run("python", init_code)

# Guide the model on how to use these controllers
interpreter.system_message = """
CRITICAL: You have access to advanced automation controllers. You MUST use them instead of basic shell commands.

Available controllers (already imported and ready to use):

🧮 CALCULATIONS - Use Python's built-in calculator:
result = 80121 * 89  # Direct calculation in Python

🌐 ADVANCED WEB SCRAPING - Use ScraplingController for adaptive web scraping:
scraper.fetch_basic("https://trends.google.com")  # Basic HTTP fetch
scraper.fetch_stealth("https://news.google.com")  # Stealth mode (bypasses anti-bot)
scraper.scrape_trending_news()  # Get trending news from multiple sources
scraper.scrape_elements(url, ["h1", ".article"])  # Extract specific elements
scraper.get_page_text(url)  # Get clean text content

📱 BROWSER AUTOMATION - Use BrowserController for interaction:
browser.goto("https://docs.new")  # Open Google Docs
browser.type("body", "content")   # Type in page elements
browser.click("button")  # Click elements
browser.screenshot()  # Take screenshots

📱 APP CONTROL - Open and control ANY macOS application:
launch_any_app("Messages")  # Open Messages (iMessage)
launch_any_app("Calculator")  # Open Calculator
launch_any_app("Mail")  # Open Mail app
launch_any_app("Spotify")  # Open Spotify
windsurf_app = windsurf()  # Get Windsurf controller
windsurf_app.activate()  # Focus app
windsurf_app.type_text("content")  # Type in any app
windsurf_app.keystroke("cmd+v")  # Send keystrokes

🔧 SYSTEM OPERATIONS - Use osctl for file/system tasks:
osctl.run_shell("echo hello")  # Run shell commands safely
osctl.write_file("/path/file.txt", "content")  # Write files

💾 MEMORY - Use memory functions for data storage:
save_doc("namespace", "title", "content")
search_docs("query")

🚫 NEVER USE THESE COMMANDS DIRECTLY:
- open -a Calculator (use launch_any_app("Calculator"))
- open -a Messages (use launch_any_app("Messages"))
- open -a "Google Chrome" (use browser.goto())
- osascript commands (use windsurf methods)
- curl/wget (use scraper.fetch_basic() or scraper.fetch_stealth())

✅ EXAMPLES FOR ANY REQUEST:

🧮 CALCULATIONS:
result = 2 + 2  # Any math equation
result = (80121 * 89) / 100  # Complex calculations

📱 OPEN ANY APP:
launch_any_app("Messages")  # iMessage
launch_any_app("Calculator")
launch_any_app("Spotify")
launch_any_app("Discord")

🌐 SCRAPE ANY WEBSITE:
page = scraper.fetch_stealth("https://news.ycombinator.com")
trending = scraper.scrape_trending_news()
articles = scraper.scrape_elements(url, ["h1", ".title", ".article"])

📄 BROWSER AUTOMATION:
browser.goto("https://docs.new")  # Any website
browser.type("input", "search term")  # Type anywhere
browser.click("button")  # Click anything

🌟 SCRAPLING SUPERPOWERS:
- ADAPTIVE: Elements relocate automatically when sites change
- STEALTH: Bypasses anti-bot protection
- MULTIPLE SOURCES: Gets trending news from Google Trends, Reddit, etc.
- SELF-HEALING: Continues working even when websites update

ALWAYS use the automation controllers above. They are more reliable than shell commands.
"""

# Optionally set a specific model (or rely on env OPENAI_API_KEY / ANTHROPIC_API_KEY)
# interpreter.llm.model = "gpt-4o"  # or "claude-3-5-sonnet-latest"

# Remove approval requirement for seamless experience
interpreter.auto_run = True

# Custom startup message
print("¯\\_(ツ)_/¯ Cristal Super Interpreter")
print("- slfdspln")
print()

interpreter.chat()
