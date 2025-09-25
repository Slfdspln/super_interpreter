import json, subprocess, os, time
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

    # ---------- Enhanced UI Interaction Methods ----------

    def click_coordinates(self, x: int, y: int) -> Dict[str, Any]:
        """Click at specific coordinates within the app window"""
        jxa = r"""
        function run(argv){
          const [appName, x, y] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          try {
            Application(appName).activate();
            delay(0.2);
            se.click([parseInt(x), parseInt(y)]);
            return JSON.stringify({ok:true, coordinates: [parseInt(x), parseInt(y)]});
          } catch(e) {
            return JSON.stringify({ok:false,error:"Click failed: " + e.message});
          }
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, str(x), str(y)))

    def double_click_ui(self, role: str, title_substring: str) -> Dict[str, Any]:
        """Double-click a UI element"""
        jxa = r"""
        function run(argv){
          const [appName, role, needle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function walk(el, depth=0){
            if (depth > 10) return false;
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

              if (elRole === role.toLowerCase() && elTitle.includes(needle.toLowerCase())){
                if (el.actions && el.actions.byName("AXPress").exists){
                  el.actions.byName("AXPress").perform();
                  delay(0.1);
                  el.actions.byName("AXPress").perform();
                  return true;
                }
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  if (walk(c, depth + 1)) return true;
                }
              }
            } catch(e) {}
            return false;
          }

          for (const w of p.windows()){
            if (walk(w)) return JSON.stringify({ok:true});
          }
          return JSON.stringify({ok:false,error:"Element not found for double-click"});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, role, title_substring))

    def right_click_ui(self, role: str, title_substring: str) -> Dict[str, Any]:
        """Right-click a UI element to open context menu"""
        jxa = r"""
        function run(argv){
          const [appName, role, needle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function walk(el, depth=0){
            if (depth > 10) return false;
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

              if (elRole === role.toLowerCase() && elTitle.includes(needle.toLowerCase())){
                if (el.actions && el.actions.byName("AXShowMenu").exists){
                  el.actions.byName("AXShowMenu").perform();
                  return true;
                }
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  if (walk(c, depth + 1)) return true;
                }
              }
            } catch(e) {}
            return false;
          }

          for (const w of p.windows()){
            if (walk(w)) return JSON.stringify({ok:true});
          }
          return JSON.stringify({ok:false,error:"Element not found for right-click"});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, role, title_substring))

    def hover_ui(self, role: str, title_substring: str) -> Dict[str, Any]:
        """Hover over a UI element"""
        jxa = r"""
        function run(argv){
          const [appName, role, needle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function walk(el, depth=0){
            if (depth > 10) return false;
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

              if (elRole === role.toLowerCase() && elTitle.includes(needle.toLowerCase())){
                const position = el.position();
                const size = el.size();
                const centerX = position[0] + size[0] / 2;
                const centerY = position[1] + size[1] / 2;

                se.mouseMoved([centerX, centerY]);
                return true;
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  if (walk(c, depth + 1)) return true;
                }
              }
            } catch(e) {}
            return false;
          }

          for (const w of p.windows()){
            if (walk(w)) return JSON.stringify({ok:true});
          }
          return JSON.stringify({ok:false,error:"Element not found for hover"});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, role, title_substring))

    def select_text(self, start_pos: int, end_pos: int) -> Dict[str, Any]:
        """Select text in the focused text field"""
        try:
            # Move to start position
            self.keystroke("a", ["command"])  # Select all first
            time.sleep(0.1)

            # Use arrow keys to position cursor
            for _ in range(start_pos):
                self.keystroke("Right arrow", [])

            # Hold shift and move to end position
            for _ in range(end_pos - start_pos):
                self.keystroke("Right arrow", ["shift"])

            return {"ok": True, "start": start_pos, "end": end_pos}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def drag_ui_element(self, from_role: str, from_title: str, to_role: str, to_title: str) -> Dict[str, Any]:
        """Drag one UI element to another"""
        jxa = r"""
        function run(argv){
          const [appName, fromRole, fromTitle, toRole, toTitle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          let fromElement = null;
          let toElement = null;

          function findElement(el, role, title, depth=0){
            if (depth > 10) return null;
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

              if (elRole === role.toLowerCase() && elTitle.includes(title.toLowerCase())){
                return el;
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  const result = findElement(c, role, title, depth + 1);
                  if (result) return result;
                }
              }
            } catch(e) {}
            return null;
          }

          // Find both elements
          for (const w of p.windows()){
            if (!fromElement) fromElement = findElement(w, fromRole, fromTitle);
            if (!toElement) toElement = findElement(w, toRole, toTitle);
          }

          if (!fromElement) return JSON.stringify({ok:false,error:"Source element not found"});
          if (!toElement) return JSON.stringify({ok:false,error:"Target element not found"});

          try {
            const fromPos = fromElement.position();
            const fromSize = fromElement.size();
            const toPos = toElement.position();
            const toSize = toElement.size();

            const fromCenter = [fromPos[0] + fromSize[0]/2, fromPos[1] + fromSize[1]/2];
            const toCenter = [toPos[0] + toSize[0]/2, toPos[1] + toSize[1]/2];

            // Perform drag operation
            se.clickAndDrag(fromCenter, toCenter);

            return JSON.stringify({ok:true, from: fromCenter, to: toCenter});
          } catch(e) {
            return JSON.stringify({ok:false,error:"Drag operation failed: " + e.message});
          }
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, from_role, from_title, to_role, to_title))

    def get_ui_tree(self, max_depth: int = 5) -> Dict[str, Any]:
        """Get complete accessibility tree for debugging"""
        jxa = r"""
        function run(argv){
          const [appName, maxDepth] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function buildTree(el, depth=0){
            if (depth > parseInt(maxDepth)) return null;

            try {
              const node = {
                role: String(el.role()),
                title: String(el.title ? el.title() : el.name()),
                value: el.value ? String(el.value()) : null,
                position: el.position ? el.position() : null,
                size: el.size ? el.size() : null,
                children: []
              };

              if (el.uiElements && el.uiElements.length > 0 && depth < parseInt(maxDepth)){
                for (const child of el.uiElements()){
                  const childNode = buildTree(child, depth + 1);
                  if (childNode) node.children.push(childNode);
                }
              }

              return node;
            } catch(e) {
              return {error: e.message};
            }
          }

          const tree = [];
          for (const w of p.windows()){
            const windowTree = buildTree(w);
            if (windowTree) tree.push(windowTree);
          }

          return JSON.stringify({ok:true, tree: tree});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, str(max_depth)))

    def wait_for_element(self, role: str, title_substring: str, timeout: int = 10) -> Dict[str, Any]:
        """Wait for a UI element to appear with exponential backoff (CPU-efficient)"""
        import time
        start_time = time.time()
        wait_interval = 0.1  # Start with 100ms
        max_interval = 1.0   # Cap at 1 second

        while time.time() - start_time < timeout:
            result = self.click_ui(role, title_substring)
            if result.get("ok"):
                return {"ok": True, "found": True, "wait_time": time.time() - start_time}

            # Exponential backoff to reduce CPU usage
            time.sleep(wait_interval)
            wait_interval = min(wait_interval * 1.2, max_interval)

        return {"ok": False, "error": f"Element not found within {timeout} seconds"}

    def get_element_info(self, role: str, title_substring: str) -> Dict[str, Any]:
        """Get detailed information about a specific UI element"""
        jxa = r"""
        function run(argv){
          const [appName, role, needle] = argv;
          const se = Application("System Events");
          const p = se.processes[appName];
          if (!p.exists()) return JSON.stringify({ok:false,error:"Process not found"});

          function walk(el, depth=0){
            if (depth > 10) return null;
            try {
              const elRole = String(el.role()).toLowerCase();
              const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

              if (elRole === role.toLowerCase() && elTitle.includes(needle.toLowerCase())){
                return {
                  role: String(el.role()),
                  title: String(el.title ? el.title() : el.name()),
                  value: el.value ? String(el.value()) : null,
                  position: el.position ? el.position() : null,
                  size: el.size ? el.size() : null,
                  enabled: el.enabled ? el.enabled() : null,
                  focused: el.focused ? el.focused() : null,
                  actions: el.actions ? el.actions().map(a => String(a.name())) : []
                };
              }

              if (el.uiElements && el.uiElements.length > 0){
                for (const c of el.uiElements()){
                  const result = walk(c, depth + 1);
                  if (result) return result;
                }
              }
            } catch(e) {}
            return null;
          }

          for (const w of p.windows()){
            const info = walk(w);
            if (info) return JSON.stringify({ok:true, element: info});
          }
          return JSON.stringify({ok:false,error:"Element not found"});
        }"""
        return json.loads(_run_jxa(jxa, self.app_name, role, title_substring))

    # ---------- Docker-specific methods ----------

    def docker_start_container(self, container_name: str) -> Dict[str, Any]:
        """Start a Docker container via UI"""
        try:
            self.activate()
            time.sleep(0.5)

            # Find and click the start button for the container
            result = self.click_ui("button", "Start")
            if result.get("ok"):
                return {"ok": True, "container": container_name}
            else:
                # Try clicking on the container row first, then start
                container_result = self.click_ui("row", container_name)
                if container_result.get("ok"):
                    time.sleep(0.2)
                    return self.click_ui("button", "Start")
                return {"ok": False, "error": "Container not found or start button unavailable"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_stop_container(self, container_name: str) -> Dict[str, Any]:
        """Stop a Docker container via UI"""
        try:
            self.activate()
            time.sleep(0.5)

            # Find and click the stop button for the container
            result = self.click_ui("button", "Stop")
            if result.get("ok"):
                return {"ok": True, "container": container_name}
            else:
                # Try clicking on the container row first, then stop
                container_result = self.click_ui("row", container_name)
                if container_result.get("ok"):
                    time.sleep(0.2)
                    return self.click_ui("button", "Stop")
                return {"ok": False, "error": "Container not found or stop button unavailable"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a Docker container via UI"""
        try:
            self.activate()
            time.sleep(0.5)

            # Find and click the restart button for the container
            result = self.click_ui("button", "Restart")
            if result.get("ok"):
                return {"ok": True, "container": container_name}
            else:
                # Try clicking on the container row first, then restart
                container_result = self.click_ui("row", container_name)
                if container_result.get("ok"):
                    time.sleep(0.2)
                    return self.click_ui("button", "Restart")
                return {"ok": False, "error": "Container not found or restart button unavailable"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_open_containers_tab(self) -> Dict[str, Any]:
        """Navigate to Containers tab in Docker Desktop"""
        try:
            self.activate()
            time.sleep(0.3)
            return self.click_ui("tab", "Containers")
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_open_images_tab(self) -> Dict[str, Any]:
        """Navigate to Images tab in Docker Desktop"""
        try:
            self.activate()
            time.sleep(0.3)
            return self.click_ui("tab", "Images")
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_open_volumes_tab(self) -> Dict[str, Any]:
        """Navigate to Volumes tab in Docker Desktop"""
        try:
            self.activate()
            time.sleep(0.3)
            return self.click_ui("tab", "Volumes")
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_search_containers(self, search_term: str) -> Dict[str, Any]:
        """Search for containers in Docker Desktop"""
        try:
            self.activate()
            time.sleep(0.3)

            # Look for search field
            search_result = self.type_in_field("search", search_term)
            if search_result.get("ok"):
                return {"ok": True, "search_term": search_term}
            else:
                # Try clicking search field first
                field_result = self.click_ui("text field", "search")
                if field_result.get("ok"):
                    time.sleep(0.2)
                    return self.type_in_field("search", search_term)
                return {"ok": False, "error": "Search field not found"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_open_container_details(self, container_name: str) -> Dict[str, Any]:
        """Open detailed view for a specific container"""
        try:
            self.activate()
            time.sleep(0.3)

            # Double-click on container to open details
            result = self.double_click_ui("row", container_name)
            if result.get("ok"):
                return {"ok": True, "container": container_name}
            else:
                # Try single click first, then look for details button
                click_result = self.click_ui("row", container_name)
                if click_result.get("ok"):
                    time.sleep(0.2)
                    return self.click_ui("button", "Details")
                return {"ok": False, "error": "Container not found or details unavailable"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_pull_image(self, image_name: str) -> Dict[str, Any]:
        """Pull a Docker image via UI"""
        try:
            self.activate()
            time.sleep(0.3)

            # Navigate to Images tab first
            self.docker_open_images_tab()
            time.sleep(0.5)

            # Look for pull button or field
            pull_result = self.click_ui("button", "Pull")
            if pull_result.get("ok"):
                time.sleep(0.3)
                # Type image name
                type_result = self.type_text(image_name)
                if type_result == "OK":
                    # Press Enter or click Pull button
                    self.keystroke("return", [])
                    return {"ok": True, "image": image_name}

            return {"ok": False, "error": "Pull functionality not accessible"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_remove_container(self, container_name: str) -> Dict[str, Any]:
        """Remove/delete a Docker container via UI"""
        try:
            self.activate()
            time.sleep(0.3)

            # Right-click on container for context menu
            context_result = self.right_click_ui("row", container_name)
            if context_result.get("ok"):
                time.sleep(0.2)
                # Look for Delete/Remove option
                delete_result = self.click_ui("menu item", "Delete")
                if not delete_result.get("ok"):
                    delete_result = self.click_ui("menu item", "Remove")

                if delete_result.get("ok"):
                    # Confirm deletion if dialog appears
                    time.sleep(0.3)
                    confirm_result = self.click_ui("button", "Delete")
                    if not confirm_result.get("ok"):
                        confirm_result = self.click_ui("button", "Yes")

                    return {"ok": True, "container": container_name, "confirmed": confirm_result.get("ok", False)}

            return {"ok": False, "error": "Container not found or delete option unavailable"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def docker_get_container_logs(self, container_name: str) -> Dict[str, Any]:
        """Open logs for a specific container"""
        try:
            self.activate()
            time.sleep(0.3)

            # Click on container
            container_result = self.click_ui("row", container_name)
            if container_result.get("ok"):
                time.sleep(0.2)
                # Look for Logs tab or button
                logs_result = self.click_ui("tab", "Logs")
                if not logs_result.get("ok"):
                    logs_result = self.click_ui("button", "Logs")

                if logs_result.get("ok"):
                    return {"ok": True, "container": container_name}

            return {"ok": False, "error": "Container logs not accessible"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ---------- Calculator-specific methods ----------

    def calculator_type_expression(self, expression: str) -> Dict[str, Any]:
        """Type mathematical expression in Calculator"""
        try:
            self.activate()
            time.sleep(0.3)

            # Clear calculator first
            self.keystroke("c", ["command"])
            time.sleep(0.1)

            # Type the expression
            self.type_text(expression)
            return {"ok": True, "expression": expression}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def calculator_click_buttons(self, button_sequence: List[str]) -> Dict[str, Any]:
        """Click Calculator buttons in sequence"""
        try:
            self.activate()
            time.sleep(0.3)

            for button in button_sequence:
                result = self.click_ui("button", button)
                if not result.get("ok"):
                    return {"ok": False, "error": f"Failed to click button: {button}"}
                time.sleep(0.1)

            return {"ok": True, "sequence": button_sequence}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def calculator_get_display(self) -> Dict[str, Any]:
        """Get current Calculator display value"""
        jxa = r"""
        function run(argv){
          const se = Application("System Events");
          const calc = se.processes["Calculator"];
          if (!calc.exists()) return JSON.stringify({ok:false,error:"Calculator not running"});

          try {
            // Calculator display is usually a text field or static text
            const window = calc.windows[0];

            function findDisplay(el, depth=0){
              if (depth > 5) return null;
              try {
                const role = String(el.role()).toLowerCase();
                if (role === "text field" || role === "static text"){
                  const value = el.value ? String(el.value()) : String(el.title());
                  if (value && !isNaN(parseFloat(value.replace(/[^0-9.-]/g, '')))){
                    return value;
                  }
                }

                if (el.uiElements && el.uiElements.length > 0){
                  for (const child of el.uiElements()){
                    const result = findDisplay(child, depth + 1);
                    if (result) return result;
                  }
                }
              } catch(e) {}
              return null;
            }

            const display = findDisplay(window);
            if (display) {
              return JSON.stringify({ok:true, value: display});
            } else {
              return JSON.stringify({ok:false,error:"Display value not found"});
            }
          } catch(e) {
            return JSON.stringify({ok:false,error:"Error reading display: " + e.message});
          }
        }"""
        return json.loads(_run_jxa(jxa))

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

def brave() -> MacApp:
    return MacApp("Brave Browser")

def calculator() -> MacApp:
    """Get Calculator app instance with enhanced methods"""
    return MacApp("Calculator")

def docker() -> MacApp:
    """Get Docker Desktop app instance with enhanced methods"""
    return MacApp("Docker Desktop")

def launch_any_app(app_name: str, path: str = None) -> dict:
    """Launch any macOS application by name, optionally with a file/folder"""
    try:
        cmd = ['open', '-a', app_name]
        if path:
            cmd.append(path)

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            message = f"Launched {app_name}"
            if path:
                message += f" with {path}"
            return {"ok": True, "message": message, "app": app_name, "path": path}
        else:
            return {"ok": False, "error": f"Failed to launch {app_name}: {result.stderr}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}