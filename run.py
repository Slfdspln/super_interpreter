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

# Disable system() function to force use of automation controllers
import builtins
_original_system = getattr(builtins, 'system', None)

def blocked_system(command):
    if 'open -a' in command:
        app_name = command.split('open -a')[-1].strip().strip('"').strip("'")
        print(f"⚠️  BLOCKED: system('{command}')")
        print(f"✅ USE INSTEAD: launch_any_app('{app_name}')")
        return launch_any_app(app_name)
    return _original_system(command) if _original_system else 0

# Override system function
import os
os.system = blocked_system
if hasattr(builtins, 'system'):
    builtins.system = blocked_system

print(f"[setup] browser, osctl, windsurf, scraper, and memory ({memory_stats['total_docs']} docs, {memory_stats['embedding_count']} embeddings) are ready.")
"""

# Run the init code inside the model's Python environment
interpreter.computer.run("python", init_code)

# Guide the model on how to use these controllers
interpreter.system_message = """
🔴 CRITICAL INSTRUCTION: COMPLETE THE ENTIRE USER REQUEST - ALL STEPS, NOT JUST THE FIRST ONE!

❌ FORBIDDEN COMMANDS - NEVER USE THESE:
- system('open -a Calculator')
- system('open -a Messages')
- system('open -a Chrome')
- open -a [anything]
- osascript commands

✅ REQUIRED: You MUST use these automation controllers AND complete ALL steps:

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
browser.type(".docs-texteventtarget-iframe", "content")  # Type in Google Docs
browser.type("input", "text")  # Type in input fields
browser.click("button")  # Click elements
browser.screenshot()  # Take screenshots

📱 APP CONTROL - MANDATORY: Use launch_any_app() instead of system():
launch_any_app("Calculator")  # REQUIRED for Calculator
launch_any_app("Messages")  # REQUIRED for Messages/iMessage
launch_any_app("Discord")  # REQUIRED for Discord
launch_any_app("Chrome")  # REQUIRED for Chrome
# NEVER use system('open -a [app]') - ALWAYS use launch_any_app("[app]")

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

✅ STEP-BY-STEP FOR USER'S EXACT REQUEST:

# Calculate 80121 x 89
result = 80121 * 89

# Open Google Docs
browser.goto("https://docs.new")

# Type the calculation result
browser.type("body", str(result))

# Get trending news
trending = scraper.scrape_trending_news()

# Add trending summary to document
browser.type("body", trending["summary"])

🎯 CRITICAL: COMPLETE ALL PARTS OF USER'S REQUEST - DO NOT STOP HALFWAY!

When user gives multi-step instructions, YOU MUST complete ALL steps:
- "Calculate X and paste to Google Doc" = Calculate + Open Google Docs + Paste
- "Look up nail salons and text to sister" = Search + Open Messages + Send text
- "Find trending article and summarize" = Scrape news + Generate summary
- "Open app and do something" = Launch app + Perform action

NEVER stop after just one step - complete the ENTIRE request using these controllers:

EXAMPLES:
- Calculate: result = 2 + 2
- Open Google Docs: browser.goto("https://docs.new")
- Type in doc: browser.type("body", "content")
- Launch app: launch_any_app("Messages")
- Scrape web: scraper.fetch_stealth("https://example.com")
- Get trending: scraper.scrape_trending_news()

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
