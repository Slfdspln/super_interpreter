import json, subprocess, shlex, os
from typing import List, Optional

def _run_jxa(jxa_source: str, *args: str) -> str:
    # Call JXA (JavaScript for Automation)
    cmd = ["osascript", "-l", "JavaScript", "-e", jxa_source, "--"] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or "JXA error")
    return res.stdout.strip()

class MacApp:
    def __init__(self, app_name: str):
        self.app_name = app_name

    # --- App lifecycle / focus ---
    def activate(self):
        jxa = r"""
        function run(argv){
          const appName = argv[0];
          Application(appName).activate();
          return "OK";
        }"""
        return _run_jxa(jxa, self.app_name)

    def open_path(self, path: str):
        # open the app with a file/folder
        subprocess.run(["open", "-a", self.app_name, path], check=False)
        return {"ok": True}

    # --- Typing & keystrokes ---
    def keystroke(self, text: str, modifiers: Optional[List[str]] = None):
        # modifiers: ["command", "shift", "option", "control"]
        mods = modifiers or []
        jxa = r"""
        function run(argv){
          const [text, modsCSV] = argv;
          const mods = modsCSV ? modsCSV.split(",").filter(Boolean) : [];
          const se = Application("System Events");
          se.keystroke(text, { using: mods });
          return "OK";
        }"""
        return _run_jxa(jxa, text, ",".join(mods))

    def type_text(self, text: str):
        # Types raw text (no modifiers)
        jxa = r"""
        function run(argv){
          const text = argv[0];
          const se = Application("System Events");
          se.keystroke(text);
          return "OK";
        }"""
        return _run_jxa(jxa, text)

    # --- Menus (more robust than keystrokes for commands) ---
    def menu_click(self, menu_path: List[str]):
        # Example: ["File", "New File"]
        jxa = r"""
        function run(argv){
          const appName = argv[0];
          const path = JSON.parse(argv[1]); // ["File","New File"]
          const se = Application("System Events");
          const proc = se.processes[appName];
          if (!proc.exists()) { return "Process not found"; }
          let menuBar = proc.menuBars[0];
          let menu = null;
          for (let i=0;i<path.length;i++){
            const name = path[i];
            if (i==0){
              menu = menuBar.menuBarItems[name].menus[0];
            } else if (i == path.length-1){
              menu.menuItems[name].click();
            } else {
              menu = menu.menuItems[name].menus[0];
            }
          }
          return "OK";
        }"""
        return _run_jxa(jxa, self.app_name, json.dumps(menu_path))

    # --- Bring window to front (sometimes needed after open) ---
    def focus_main_window(self):
        jxa = r"""
        function run(argv){
          const appName = argv[0];
          const app = Application(appName);
          app.activate();
          return "OK";
        }"""
        return _run_jxa(jxa, self.app_name)

# Convenience helpers for Windsurf (bundle name usually "Windsurf")
def windsurf() -> MacApp:
    return MacApp("Windsurf")