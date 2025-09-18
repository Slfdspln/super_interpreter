import json
import subprocess
import time
from typing import List, Optional, Dict, Any, Tuple

class SystemUIController:
    """Universal macOS UI automation for laptop-wide control via Accessibility APIs"""

    def __init__(self):
        self.default_delay = 0.1

    def _run_applescript(self, script: str) -> str:
        """Execute AppleScript and return output"""
        cmd = ["osascript", "-e", script]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
        return result.stdout.strip()

    def _run_jxa(self, script: str, *args: str) -> str:
        """Execute JXA JavaScript and return output"""
        cmd = ["osascript", "-l", "JavaScript", "-e", script, "--"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"JXA error: {result.stderr.strip()}")
        return result.stdout.strip()

    # ========== COORDINATE-BASED CLICKING ==========

    def click_anywhere(self, x: int, y: int) -> Dict[str, Any]:
        """Click at absolute screen coordinates"""
        try:
            script = f"""
            tell application "System Events"
                set mouseLocation to {{{x}, {y}}}
                click at mouseLocation
            end tell
            """
            self._run_applescript(script)
            return {"ok": True, "action": "click", "coordinates": [x, y]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def double_click_anywhere(self, x: int, y: int) -> Dict[str, Any]:
        """Double-click at absolute screen coordinates"""
        try:
            script = f"""
            tell application "System Events"
                set mouseLocation to {{{x}, {y}}}
                click at mouseLocation
                delay 0.1
                click at mouseLocation
            end tell
            """
            self._run_applescript(script)
            return {"ok": True, "action": "double_click", "coordinates": [x, y]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def right_click_anywhere(self, x: int, y: int) -> Dict[str, Any]:
        """Right-click at absolute screen coordinates"""
        try:
            script = f"""
            tell application "System Events"
                set mouseLocation to {{{x}, {y}}}
                right click at mouseLocation
            end tell
            """
            self._run_applescript(script)
            return {"ok": True, "action": "right_click", "coordinates": [x, y]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def drag(self, from_x: int, from_y: int, to_x: int, to_y: int) -> Dict[str, Any]:
        """Drag from one coordinate to another"""
        try:
            script = f"""
            tell application "System Events"
                set startPoint to {{{from_x}, {from_y}}}
                set endPoint to {{{to_x}, {to_y}}}

                -- Click and hold at start point
                click at startPoint
                delay 0.1

                -- Drag to end point
                key down option
                click at endPoint
                key up option
            end tell
            """
            self._run_applescript(script)
            return {"ok": True, "action": "drag", "from": [from_x, from_y], "to": [to_x, to_y]}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== SCROLLING ==========

    def scroll(self, direction: str, amount: int = 3, x: int = None, y: int = None) -> Dict[str, Any]:
        """Scroll in specified direction at coordinates or current mouse position"""
        try:
            direction_map = {
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right"
            }

            if direction not in direction_map:
                return {"ok": False, "error": f"Invalid direction: {direction}"}

            if x is not None and y is not None:
                move_script = f'set mouseLocation to {{{x}, {y}}}\nmove to mouseLocation\n'
            else:
                move_script = ""

            script = f"""
            tell application "System Events"
                {move_script}
                scroll {direction_map[direction]} {amount}
            end tell
            """
            self._run_applescript(script)
            return {"ok": True, "action": "scroll", "direction": direction, "amount": amount}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== DOCK INTERACTION ==========

    def dock_click(self, app_name: str) -> Dict[str, Any]:
        """Click an app in the Dock"""
        try:
            jxa_script = f"""
            function run(argv) {{
                const appName = argv[0];
                const se = Application("System Events");
                const dock = se.processes["Dock"];

                if (!dock.exists()) {{
                    return JSON.stringify({{ok: false, error: "Dock not found"}});
                }}

                try {{
                    const dockItems = dock.windows[0].groups[0].groups;
                    for (const group of dockItems()) {{
                        if (group.buttons && group.buttons.length > 0) {{
                            for (const button of group.buttons()) {{
                                const title = String(button.title());
                                if (title.toLowerCase().includes(appName.toLowerCase())) {{
                                    button.click();
                                    return JSON.stringify({{ok: true, app: title}});
                                }}
                            }}
                        }}
                    }}
                    return JSON.stringify({{ok: false, error: "App not found in Dock"}});
                }} catch(e) {{
                    return JSON.stringify({{ok: false, error: e.message}});
                }}
            }}
            """
            result = self._run_jxa(jxa_script, app_name)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== MENU BAR INTERACTION ==========

    def menu_bar_click(self, item_name: str) -> Dict[str, Any]:
        """Click an item in the menu bar (top right area)"""
        try:
            jxa_script = f"""
            function run(argv) {{
                const itemName = argv[0];
                const se = Application("System Events");

                try {{
                    const menuBarItems = se.processes["SystemUIServer"].menuBars[0].menuBarItems;
                    for (const item of menuBarItems()) {{
                        const title = String(item.title ? item.title() : item.name());
                        if (title.toLowerCase().includes(itemName.toLowerCase())) {{
                            item.click();
                            return JSON.stringify({{ok: true, item: title}});
                        }}
                    }}
                    return JSON.stringify({{ok: false, error: "Menu bar item not found"}});
                }} catch(e) {{
                    return JSON.stringify({{ok: false, error: e.message}});
                }}
            }}
            """
            result = self._run_jxa(jxa_script, item_name)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== SPOTLIGHT SEARCH ==========

    def global_search(self, query: str, open_first: bool = True) -> Dict[str, Any]:
        """Use Spotlight to search and optionally open first result"""
        try:
            # Open Spotlight
            script = """
            tell application "System Events"
                key code 49 using command down  -- Cmd+Space
                delay 0.5
            end tell
            """
            self._run_applescript(script)

            # Type search query
            self.type_text(query)
            time.sleep(0.5)

            if open_first:
                # Press Enter to open first result
                self.keystroke("return")

            return {"ok": True, "query": query, "opened": open_first}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== KEYBOARD AUTOMATION ==========

    def keystroke(self, key: str, modifiers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send keystroke with optional modifiers"""
        try:
            mods = modifiers or []
            mod_string = ""

            if "command" in mods or "cmd" in mods:
                mod_string += "command down, "
            if "shift" in mods:
                mod_string += "shift down, "
            if "option" in mods or "alt" in mods:
                mod_string += "option down, "
            if "control" in mods or "ctrl" in mods:
                mod_string += "control down, "

            mod_string = mod_string.rstrip(", ")

            if mod_string:
                script = f'tell application "System Events" to keystroke "{key}" using {{{mod_string}}}'
            else:
                script = f'tell application "System Events" to keystroke "{key}"'

            self._run_applescript(script)
            return {"ok": True, "key": key, "modifiers": mods}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def type_text(self, text: str) -> Dict[str, Any]:
        """Type text using System Events"""
        try:
            # Escape quotes and special characters
            escaped_text = text.replace('"', '\\"').replace('\\', '\\\\')
            script = f'tell application "System Events" to keystroke "{escaped_text}"'
            self._run_applescript(script)
            return {"ok": True, "text": text}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== SYSTEM UTILITIES ==========

    def screenshot(self, path: str = "/tmp/ui_screenshot.png") -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            cmd = ["screencapture", "-x", path]
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                return {"ok": True, "path": path}
            else:
                return {"ok": False, "error": "Screenshot failed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse cursor position"""
        try:
            jxa_script = """
            function run() {
                const se = Application("System Events");
                const pos = se.mouseLocation();
                return JSON.stringify({ok: true, x: pos[0], y: pos[1]});
            }
            """
            result = self._run_jxa(jxa_script)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_screen_size(self) -> Dict[str, Any]:
        """Get screen dimensions"""
        try:
            jxa_script = """
            function run() {
                const se = Application("System Events");
                const desktops = se.desktops();
                if (desktops.length > 0) {
                    const bounds = desktops[0].bounds();
                    return JSON.stringify({
                        ok: true,
                        width: bounds[2],
                        height: bounds[3]
                    });
                }
                return JSON.stringify({ok: false, error: "No desktop found"});
            }
            """
            result = self._run_jxa(jxa_script)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== NOTIFICATION INTERACTION ==========

    def notification_interact(self, action: str = "click") -> Dict[str, Any]:
        """Interact with the most recent notification"""
        try:
            jxa_script = f"""
            function run(argv) {{
                const action = argv[0];
                const se = Application("System Events");

                try {{
                    const notifications = se.processes["NotificationCenter"];
                    if (!notifications.exists()) {{
                        return JSON.stringify({{ok: false, error: "No notifications found"}});
                    }}

                    const windows = notifications.windows();
                    if (windows.length > 0) {{
                        const latestNotification = windows[0];
                        if (action === "click") {{
                            latestNotification.click();
                        }} else if (action === "dismiss") {{
                            // Try to find close button
                            const buttons = latestNotification.buttons();
                            for (const btn of buttons) {{
                                if (btn.title() === "Close") {{
                                    btn.click();
                                    break;
                                }}
                            }}
                        }}
                        return JSON.stringify({{ok: true, action: action}});
                    }}
                    return JSON.stringify({{ok: false, error: "No notification windows"}});
                }} catch(e) {{
                    return JSON.stringify({{ok: false, error: e.message}});
                }}
            }}
            """
            result = self._run_jxa(jxa_script, action)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== FINDER UTILITIES ==========

    def find_and_click_text(self, text: str, app_name: str = None) -> Dict[str, Any]:
        """Find UI element containing specific text and click it"""
        try:
            target = f'processes["{app_name}"]' if app_name else 'processes'

            jxa_script = f"""
            function run(argv) {{
                const searchText = argv[0];
                const se = Application("System Events");

                function searchInElement(element, depth = 0) {{
                    if (depth > 8) return false;

                    try {{
                        const title = String(element.title ? element.title() : element.name()).toLowerCase();
                        const value = element.value ? String(element.value()).toLowerCase() : "";

                        if (title.includes(searchText.toLowerCase()) || value.includes(searchText.toLowerCase())) {{
                            if (element.actions && element.actions.byName("AXPress").exists) {{
                                element.actions.byName("AXPress").perform();
                                return true;
                            }}
                        }}

                        if (element.uiElements && element.uiElements.length > 0) {{
                            for (const child of element.uiElements()) {{
                                if (searchInElement(child, depth + 1)) return true;
                            }}
                        }}
                    }} catch(e) {{
                        // Ignore errors and continue
                    }}
                    return false;
                }}

                const processes = se.{target};
                for (const process of processes()) {{
                    for (const window of process.windows()) {{
                        if (searchInElement(window)) {{
                            return JSON.stringify({{ok: true, text: searchText}});
                        }}
                    }}
                }}

                return JSON.stringify({{ok: false, error: "Text not found"}});
            }}
            """
            result = self._run_jxa(jxa_script, text)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}