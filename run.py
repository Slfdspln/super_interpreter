from interpreter import interpreter

# Preload your controllers into the same Python process the model will use.
init_code = r"""
from controllers.browser_controller import BrowserController
from controllers.os_controller import OSController
from controllers.app_controller_macos import MacApp

browser = BrowserController("policy.yaml", headed=True)
osctl   = OSController("policy.yaml")
windsurf = MacApp("Windsurf")

print("[setup] browser, osctl, and windsurf are ready.")
"""

# Run the init code inside the model's Python environment
interpreter.computer.run("python", init_code)

# Guide the model on how to use these controllers
interpreter.system_message = """
You can run Python code locally. The following controllers are already imported:

- browser: BrowserController
    Methods:
      browser.goto(url: str) -> dict
      browser.click(selector: str) -> dict
      browser.type(selector: str, text: str, press_enter: bool=False) -> dict
      browser.scrape_text(selector: str) -> dict
      browser.screenshot(path: str="out/page.png") -> dict
      browser.new_tab(url: Optional[str]=None) -> dict

- osctl: OSController
    Methods:
      osctl.run_shell(cmd: str, cwd: str=None, timeout: int=60) -> dict
      osctl.open_in_editor(path: str, editor: str="code"|"cursor") -> dict
      osctl.write_file(path: str, content: str) -> dict

- windsurf: MacApp (for native macOS app automation)
    Methods:
      windsurf.activate() -> str (brings app to front)
      windsurf.open_path(path: str) -> dict (opens app with file/folder)
      windsurf.keystroke(text: str, modifiers: List[str]=None) -> str
      windsurf.type_text(text: str) -> str (types raw text)
      windsurf.menu_click(menu_path: List[str]) -> str (clicks menu items)
      windsurf.focus_main_window() -> str

Use short Python snippets to call these. Respect policy.yaml; actions may prompt for confirmation.
"""

# Optionally set a specific model (or rely on env OPENAI_API_KEY / ANTHROPIC_API_KEY)
# interpreter.llm.model = "gpt-4o"  # or "claude-3-5-sonnet-latest"

print("Super Interpreter ready. Say what you want to do.")
interpreter.chat()
