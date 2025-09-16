import json, subprocess, os
from typing import List, Optional, Dict, Any

def _run_jxa(src: str, *args: str) -> str:
    cmd = ["osascript", "-l", "JavaScript", "-e", src, "--"] + list(args)
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or "JXA error")
    return res.stdout.strip()

class MacApp:
    """macOS native app automation via JXA (Accessibility)."""
    def __init__(self, app_name: str):
        self.app_name = app_name

    # ---------- App / window ----------
    def activate(self) -> str:
        jxa = r"""
        function run(argv){ Application(argv[0]).activate(); return "OK"; }"""
        return _run_jxa(jxa, self.app_name)

    def windows(self) -> Dict[str, Any]:
        jxa = r"""
        function run(argv){
          const appName = argv[0];
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});
          const wins = [];
          for (const w of p.windows()){
            wins.push({title: String(w.name())});
          }
          return JSON.stringify({ok:true, windows:wins});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name))

    def focus_window(self, title_substring: str) -> Dict[str, Any]:
        jxa = r"""
        function run(argv){
          const [appName, needle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});
          for (const w of p.windows()){
            if (String(w.name()).includes(needle)){
              w.actions.byName("AXRaise").perform(w);
              Application(appName).activate();
              return JSON.stringify({ok:true});
            }
          }
          return JSON.stringify({ok:false,error:"No window matched"});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, title_substring))

    # ---------- Menus ----------
    def menu_click(self, path: List[str]) -> Dict[str, Any]:
        # Example: ["File","New File"] or ["Go","Go to File…"]
        jxa = r"""
        function run(argv){
          const appName = argv[0];
          const path = JSON.parse(argv[1]);
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});
          try {
            let menu = p.menuBars[0].menuBarItems[path[0]].menus[0];
            for (let i=1;i<path.length;i++){
              const name = path[i];
              if (i === path.length-1){
                menu.menuItems[name].click();
                return JSON.stringify({ok:true});
              } else {
                menu = menu.menuItems[name].menus[0];
              }
            }
          } catch(e) {
            return JSON.stringify({ok:false,error:"Menu path not found: " + e.message});
          }
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, json.dumps(path)))

    # ---------- Buttons / tabs / generic UI by title ----------
    def click_ui(self, role: str, title_substring: str) -> Dict[str, Any]:
        # role examples: "button", "tab group", "radio button", "tab", "text field"
        jxa = r"""
        function run(argv){
          const [appName, role, needle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function walk(el, depth=0){
            if (depth > 10) return false; // Prevent infinite recursion
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();
              const elValue = el.value ? String(el.value()).toLowerCase() : "";

              if (elRole === role.toLowerCase() &&
                  (elTitle.includes(needle.toLowerCase()) || elValue.includes(needle.toLowerCase()))){
                if (el.actions && el.actions.byName("AXPress").exists){
                  el.actions.byName("AXPress").perform();
                  return true;
                }
              }

              // Try children
              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  if (walk(c, depth + 1)) return true;
                }
              }
            } catch(e) {
              // Ignore accessibility errors and continue
            }
            return false;
          }

          for (const w of p.windows()){
            if (walk(w)) return JSON.stringify({ok:true});
          }
          return JSON.stringify({ok:false,error:`UI element not found: role=${role}, title=${needle}`});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, role, title_substring))

    def find_ui_elements(self, role: Optional[str] = None) -> Dict[str, Any]:
        """Find all UI elements, optionally filtered by role"""
        jxa = r"""
        function run(argv){
          const [appName, targetRole] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          const elements = [];

          function walk(el, depth=0){
            if (depth > 8) return; // Limit depth
            try {
              const elRole = String(el.role());
              const elTitle = String(el.title ? el.title() : el.name());

              if (!targetRole || elRole.toLowerCase() === targetRole.toLowerCase()){
                elements.push({
                  role: elRole,
                  title: elTitle,
                  value: el.value ? String(el.value()) : null
                });
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  walk(c, depth + 1);
                }
              }
            } catch(e) {
              // Ignore accessibility errors
            }
          }

          for (const w of p.windows()){
            walk(w);
          }
          return JSON.stringify({ok:true, elements:elements});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, role or ""))

    # ---------- Typing / keystrokes ----------
    def keystroke(self, text: str, modifiers: Optional[List[str]] = None) -> str:
        # Use osascript with AppleScript instead of JXA for better compatibility
        mods = modifiers or []
        mod_string = ""
        if "command" in mods:
            mod_string += "command down, "
        if "shift" in mods:
            mod_string += "shift down, "
        if "option" in mods or "alt" in mods:
            mod_string += "option down, "
        if "control" in mods:
            mod_string += "control down, "

        mod_string = mod_string.rstrip(", ")

        if mod_string:
            script = f'tell application "System Events" to keystroke "{text}" using {{{mod_string}}}'
        else:
            script = f'tell application "System Events" to keystroke "{text}"'

        cmd = ["osascript", "-e", script]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(res.stderr.strip() or "AppleScript keystroke error")
        return "OK"

    def type_text(self, text: str) -> str:
        jxa = r"""
        function run(argv){
          const se = Application("System Events");
          se.keystroke(argv[0]);
          return "OK";
        }"""
        return _run_jxa(jxa, text)

    def type_in_field(self, field_name: str, text: str) -> Dict[str, Any]:
        """Type text in a specific text field"""
        jxa = r"""
        function run(argv){
          const [appName, fieldName, text] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function findTextField(el, depth=0){
            if (depth > 8) return null;
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

              if ((elRole === "text field" || elRole === "text area") &&
                  elTitle.includes(fieldName.toLowerCase())){
                return el;
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  const result = findTextField(c, depth + 1);
                  if (result) return result;
                }
              }
            } catch(e) {}
            return null;
          }

          for (const w of p.windows()){
            const field = findTextField(w);
            if (field){
              field.focused = true;
              se.keystroke(text);
              return JSON.stringify({ok:true});
            }
          }
          return JSON.stringify({ok:false,error:"Text field not found"});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, field_name, text))

    # ---------- File operations ----------
    def open_path(self, path: str) -> Dict[str, Any]:
        subprocess.run(["open", "-a", self.app_name, path], check=False)
        return {"ok": True}

    def save_file(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Save current file, optionally with specific name"""
        try:
            # Cmd+S to save
            self.keystroke("s", ["command"])

            if filename:
                # If filename provided, type it (assumes save dialog opens)
                import time
                time.sleep(0.5)  # Wait for save dialog
                self.type_text(filename)
                time.sleep(0.2)
                self.keystroke("return", [])  # Press Enter

            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- Windsurf-specific helpers ----------
    def windsurf_new_file(self) -> Dict[str, Any]:
        """Create new file in Windsurf"""
        return self.menu_click(["File", "New File"])

    def windsurf_open_file(self) -> Dict[str, Any]:
        """Open file dialog in Windsurf"""
        return self.menu_click(["File", "Open File..."])

    def windsurf_command_palette(self) -> Dict[str, Any]:
        """Open Windsurf command palette"""
        try:
            self.keystroke("p", ["command", "shift"])
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def windsurf_terminal(self) -> Dict[str, Any]:
        """Toggle Windsurf terminal"""
        try:
            self.keystroke("`", ["control"])
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def windsurf_run_command(self, command: str) -> Dict[str, Any]:
        """Open command palette and run a command"""
        try:
            # Open command palette
            self.keystroke("p", ["command", "shift"])
            import time
            time.sleep(0.3)

            # Type command
            self.type_text(command)
            time.sleep(0.2)

            # Press Enter
            self.keystroke("return", [])
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- Information gathering ----------
    def get_window_info(self) -> Dict[str, Any]:
        """Get detailed information about current windows and UI elements"""
        try:
            windows = self.windows()
            if not windows.get("ok"):
                return windows

            # Get UI elements
            elements = self.find_ui_elements()

            return {
                "ok": True,
                "app_name": self.app_name,
                "windows": windows.get("windows", []),
                "ui_elements_count": len(elements.get("elements", [])),
                "available_buttons": [e for e in elements.get("elements", []) if e["role"].lower() == "button"],
                "available_tabs": [e for e in elements.get("elements", []) if "tab" in e["role"].lower()]
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

# Convenience constructor
def windsurf() -> MacApp:
    return MacApp("Windsurf")

# Other common apps
def chrome() -> MacApp:
    return MacApp("Google Chrome")

def safari() -> MacApp:
    return MacApp("Safari")

def vscode() -> MacApp:
    return MacApp("Visual Studio Code")

def terminal() -> MacApp:
    return MacApp("Terminal")

def finder() -> MacApp:
    return MacApp("Finder")