import typer, json
from typing import List
from controllers.app_controller_macos import MacApp

app = typer.Typer(help="Native macOS app automation (Accessibility API).")

@app.command("activate")
def activate(app_name: str = "Windsurf"):
    print(MacApp(app_name).activate())

@app.command("open")
def open_(path: str, app_name: str = "Windsurf"):
    print(json.dumps(MacApp(app_name).open_path(path)))

@app.command("menu")
def menu(app_name: str, items: List[str]):
    # Usage: python app_cli.py menu --app-name Windsurf --items File "New File"
    print(MacApp(app_name).menu_click(items))

@app.command("type")
def type_(text: str, app_name: str = "Windsurf"):
    print(MacApp(app_name).type_text(text))

@app.command("keystroke")
def keystroke(text: str, app_name: str = "Windsurf",
              command: bool=False, shift: bool=False, option: bool=False, control: bool=False):
    mods = []
    if command: mods.append("command")
    if shift: mods.append("shift")
    if option: mods.append("option")
    if control: mods.append("control")
    print(MacApp(app_name).keystroke(text, mods))

if __name__ == "__main__":
    app()