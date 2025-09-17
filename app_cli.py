import typer, json
from typing import List, Optional
from controllers.app_controller_macos import MacApp, windsurf, chrome, safari, vscode
from controllers.universal_app_controller import create_universal_app_controller

app = typer.Typer(help="Universal macOS app automation (Accessibility API).")
universal = create_universal_app_controller()

@app.command("activate")
def activate(app_name: str):
    """Activate and bring any app to front"""
    result = universal.activate_app(app_name)
    print(json.dumps(result, indent=2))

@app.command("open")
def open_(path: str, app_name: str):
    """Open file or folder in any app"""
    result = universal.open_file_in_editor(app_name, path)
    print(json.dumps(result, indent=2))

@app.command("menu")
def menu(app_name: str, items: List[str]):
    """Click menu items in any app. Usage: --items File "New File" """
    result = universal.click_menu(app_name, items)
    print(json.dumps(result, indent=2))

@app.command("type")
def type_(text: str, app_name: str):
    """Type text in any app"""
    result = universal.type_text(app_name, text)
    print(json.dumps(result, indent=2))

@app.command("keystroke")
def keystroke(key: str, app_name: str,
              command: bool=False, shift: bool=False, option: bool=False, control: bool=False):
    """Send keystroke with modifiers to any app"""
    mods = []
    if command: mods.append("command")
    if shift: mods.append("shift")
    if option: mods.append("option")
    if control: mods.append("control")
    result = universal.send_keystroke(app_name, key, mods)
    print(json.dumps(result, indent=2))

@app.command("click-ui")
def click_ui(role: str, title: str, app_name: str):
    """Click UI element by role and title in any app. Roles: button, tab, radio button, etc."""
    result = universal.click_ui_element(app_name, role, title)
    print(json.dumps(result, indent=2))

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

# New Universal Commands
@app.command("launch")
def launch(app_name: str, path: Optional[str] = None):
    """Launch any macOS application"""
    result = universal.launch_app(app_name, path)
    print(json.dumps(result, indent=2))

@app.command("quit")
def quit_app(app_name: str):
    """Quit any application"""
    result = universal.quit_app(app_name)
    print(json.dumps(result, indent=2))

@app.command("execute")
def execute(command: str, app_name: str):
    """Execute command in terminal app (Terminal, Windsurf, VS Code, etc.)"""
    result = universal.execute_in_terminal_app(app_name, command)
    print(json.dumps(result, indent=2))

@app.command("list-apps")
def list_apps(query: Optional[str] = None):
    """List all installed applications, optionally filtered by query"""
    if query:
        apps = universal.search_apps(query)
        print(f"Apps matching '{query}':")
    else:
        apps = universal.get_app_list()
        print("All installed applications:")

    for app in apps[:50]:  # Limit to first 50
        print(f"  - {app['name']} ({app['directory']})")

    if len(apps) > 50:
        print(f"  ... and {len(apps) - 50} more")

@app.command("running-apps")
def running_apps():
    """List currently running applications"""
    apps = universal.get_running_apps()
    print("Currently running applications:")
    for app in apps:
        print(f"  - {app}")

@app.command("app-info")
def app_info(app_name: str):
    """Get detailed information about an application"""
    result = universal.get_app_info(app_name)
    print(json.dumps(result, indent=2))

@app.command("batch")
def batch_operations(operations_file: str):
    """Execute batch operations from JSON file"""
    try:
        import json
        with open(operations_file, 'r') as f:
            operations = json.load(f)

        results = universal.batch_app_operation(operations)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    app()