#!/usr/bin/env python3
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ["PYTHONWARNINGS"] = "ignore::UserWarning"

from interpreter import interpreter

# Preload your controllers into the same Python process the model will use.
init_code = r"""
from controllers.browser_controller import BrowserController
from controllers.os_controller import OSController
from controllers.app_controller_macos import MacApp
from controllers.memory import save_doc, list_docs, get_doc, search_docs, get_stats, quick_save

browser = BrowserController("policy.yaml", headed=True)
osctl   = OSController("policy.yaml")
windsurf = MacApp("Windsurf")

# Memory functions are available directly
memory_stats = get_stats()

print(f"[setup] browser, osctl, windsurf, and memory ({memory_stats['total_docs']} docs, {memory_stats['embedding_count']} embeddings) are ready.")
"""

# Run the init code inside the model's Python environment
interpreter.computer.run("python", init_code)

# Guide the model on how to use these controllers
interpreter.system_message = """
You can run Python code locally. The following controllers are already imported:

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
