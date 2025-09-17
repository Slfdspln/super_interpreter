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
from controllers.os_controller import OSController
from controllers.app_controller_macos import MacApp
from controllers.memory import save_doc, list_docs, get_doc, search_docs, get_stats, quick_save
from controllers.universal_app_controller import create_universal_app_controller
from controllers.document_automation_controller import create_document_automation_controller
from controllers.browser_use_controller import create_browser_use_controller, quick_browser_task
import asyncio

browser = BrowserController("policy.yaml", headed=True)
osctl   = OSController("policy.yaml")
windsurf = MacApp("Windsurf")
universal_app = create_universal_app_controller()
doc_automation = create_document_automation_controller("User")
browser_controller = create_browser_use_controller()

# Memory functions are available directly
memory_stats = get_stats()

def calculate_with_calculator(expression):
    # FULLY AUTOMATED: Open calculator and press all buttons automatically
    print(f"🧮 Automating calculator for: {expression}")
    result = doc_automation.automated_calculator_operation(expression)
    return {"expression": expression, "result": result, "message": f"Calculated {expression} = {result}"}

def browser_task_sync(task_description):
    # Execute browser automation task (synchronous wrapper)
    return asyncio.run(quick_browser_task(task_description))

def quick_calculate(expression):
    # Quick calculation without GUI automation - instant results
    result = doc_automation.evaluate_expression(expression)
    return {"expression": expression, "result": result, "message": f"Calculated: {expression} = {result}"}

print(f"[setup] browser, osctl, windsurf, universal_app, doc_automation, and memory ({memory_stats['total_docs']} docs, {memory_stats['embedding_count']} embeddings) are ready.")
print("🧮 Calculator automation: calculate_with_calculator(expression)")
print("🌐 Browser automation: browser_task_sync(task)")
print("⚡ Quick math: quick_calculate(expression)")
"""

# Run the init code inside the model's Python environment
interpreter.computer.run("python", init_code)

# Guide the model on how to use these controllers
interpreter.system_message = """
You can run Python code locally. The following controllers are already imported:

🧮 AUTOMATED CALCULATOR FUNCTIONS (USE THESE FOR CALCULATIONS):
- calculate_with_calculator(expression) - FULLY AUTOMATED: Opens calculator + presses all buttons
- quick_calculate(expression) - INSTANT calculation results (fastest option)

🌐 BROWSER AUTOMATION FUNCTIONS (USE THESE FOR WEB TASKS):
- browser_task_sync(task) - AI browser automation for ANY web task
- browser_task_sync('find trending news') - Smart news discovery
- browser_task_sync('create google doc') - Automated document creation

IMPORTANT: For calculations, ALWAYS use calculate_with_calculator() or quick_calculate()
For web automation, ALWAYS use browser_task_sync()
NEVER use manual commands like 'open -a Calculator' or manual web scraping.

Original controllers:

- browser: BrowserController (Playwright web automation)
    Methods:
      browser.goto(url: str) -> dict
      browser.click(selector: str) -> dict
      browser.type(selector: str, text: str, press_enter: bool=False) -> dict
      browser.scrape_text(selector: str) -> dict
      browser.screenshot(path: str="out/page.png") -> dict
      browser.new_tab(url: Optional[str]=None) -> dict

- osctl: OSController (System operations)
    Methods:
      osctl.run_shell(cmd: str, cwd: str=None, timeout: int=60) -> dict
      osctl.open_in_editor(path: str, editor: str="code"|"cursor") -> dict
      osctl.write_file(path: str, content: str) -> dict

- windsurf: MacApp (Native macOS app automation via Accessibility API)
    Methods:
      windsurf.activate() -> str
      windsurf.open_path(path: str) -> dict
      windsurf.keystroke(text: str, modifiers: List[str]=None) -> str
      windsurf.type_text(text: str) -> str
      windsurf.menu_click(menu_path: List[str]) -> dict
      windsurf.click_ui(role: str, title: str) -> dict
      windsurf.find_ui_elements(role: str=None) -> dict
      windsurf.focus_window(title: str) -> dict
      windsurf.get_window_info() -> dict
      windsurf.windsurf_command_palette() -> dict
      windsurf.windsurf_new_file() -> dict
      windsurf.save_file(filename: str=None) -> dict

- Memory system (SQLite + embeddings for knowledge storage)
    Functions:
      save_doc(namespace: str, title: str, content: str, meta: dict={}) -> int
      get_doc(doc_id: int) -> dict
      list_docs(namespace: str=None) -> list
      search_docs(query: str, namespace: str=None) -> list (semantic + text search)
      quick_save(namespace: str, content: str, title: str=None) -> int
      get_stats() -> dict

Use short Python snippets to call these. Memory system supports semantic search with embeddings when OpenAI API key is available. Respect policy.yaml; actions may prompt for confirmation.
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
