import typer, json
from typing import List, Optional
from controllers.app_controller_macos import MacApp, windsurf, chrome, safari, vscode

app = typer.Typer(help="Native macOS app automation (Accessibility API).")

@app.command("activate")
def activate(app_name: str = "Windsurf"):
    """Activate and bring app to front"""
    result = MacApp(app_name).activate()
    print(result)

@app.command("open")
def open_(path: str, app_name: str = "Windsurf"):
    """Open file or folder in app"""
    result = MacApp(app_name).open_path(path)
    print(json.dumps(result))

@app.command("menu")
def menu(app_name: str, items: List[str]):
    """Click menu items. Usage: --items File "New File" """
    result = MacApp(app_name).menu_click(items)
    print(json.dumps(result))

@app.command("type")
def type_(text: str, app_name: str = "Windsurf"):
    """Type text"""
    result = MacApp(app_name).type_text(text)
    print(result)

@app.command("keystroke")
def keystroke(text: str, app_name: str = "Windsurf",
              command: bool=False, shift: bool=False, option: bool=False, control: bool=False):
    """Send keystroke with modifiers"""
    mods = []
    if command: mods.append("command")
    if shift: mods.append("shift")
    if option: mods.append("option")
    if control: mods.append("control")
    result = MacApp(app_name).keystroke(text, mods)
    print(result)

@app.command("click-ui")
def click_ui(role: str, title: str, app_name: str = "Windsurf"):
    """Click UI element by role and title. Roles: button, tab, radio button, etc."""
    result = MacApp(app_name).click_ui(role, title)
    print(json.dumps(result))

@app.command("find-ui")
def find_ui(app_name: str = "Windsurf", role: Optional[str] = None, limit: int = 10):
    """Find UI elements, optionally filtered by role"""
    result = MacApp(app_name).find_ui_elements(role)
    if result.get("ok"):
        elements = result["elements"][:limit]
        print(f"Found {len(result['elements'])} elements (showing {len(elements)}):")
        for i, elem in enumerate(elements):
            print(f"  {i+1}. {elem['role']}: '{elem['title']}'")
    else:
        print(json.dumps(result))

@app.command("windows")
def windows(app_name: str = "Windsurf"):
    """List all windows for app"""
    result = MacApp(app_name).windows()
    print(json.dumps(result, indent=2))

@app.command("focus-window")
def focus_window(title: str, app_name: str = "Windsurf"):
    """Focus window by title substring"""
    result = MacApp(app_name).focus_window(title)
    print(json.dumps(result))

@app.command("info")
def info(app_name: str = "Windsurf"):
    """Get comprehensive app/window information"""
    result = MacApp(app_name).get_window_info()
    if result.get("ok"):
        print(f"App: {result['app_name']}")
        print(f"Windows ({len(result['windows'])}):")
        for w in result['windows']:
            print(f"  - {w['title']}")
        print(f"UI Elements: {result['ui_elements_count']}")
        print(f"Buttons: {len(result['available_buttons'])}")
        print(f"Tabs: {len(result['available_tabs'])}")
    else:
        print(json.dumps(result))

@app.command("save")
def save(filename: Optional[str] = None, app_name: str = "Windsurf"):
    """Save current file, optionally with filename"""
    result = MacApp(app_name).save_file(filename)
    print(json.dumps(result))

# Windsurf-specific commands
windsurf_app = typer.Typer(help="Windsurf-specific automation commands")
app.add_typer(windsurf_app, name="windsurf")

@windsurf_app.command("new-file")
def windsurf_new_file():
    """Create new file in Windsurf"""
    result = windsurf().windsurf_new_file()
    print(json.dumps(result))

@windsurf_app.command("command-palette")
def windsurf_command_palette():
    """Open Windsurf command palette"""
    result = windsurf().windsurf_command_palette()
    print(json.dumps(result))

@windsurf_app.command("terminal")
def windsurf_terminal():
    """Toggle Windsurf terminal"""
    result = windsurf().windsurf_terminal()
    print(json.dumps(result))

@windsurf_app.command("run-command")
def windsurf_run_command(command: str):
    """Open command palette and run a command"""
    result = windsurf().windsurf_run_command(command)
    print(json.dumps(result))

if __name__ == "__main__":
    app()