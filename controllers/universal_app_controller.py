#!/usr/bin/env python3
"""
Universal macOS App Controller
Full access to all macOS applications with enhanced permissions
"""

import subprocess
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

# Import existing app controller
from .app_controller_macos import MacApp, launch_any_app

class UniversalAppController:
    """
    Universal controller for all macOS applications
    Provides comprehensive app automation capabilities
    """

    def __init__(self):
        self.active_apps = {}  # Cache of active app controllers
        self.app_list = self._get_all_apps()

    def _get_all_apps(self) -> List[Dict[str, str]]:
        """Get list of all installed applications"""
        apps = []

        # Search common app directories
        app_dirs = [
            '/Applications',
            '/System/Applications',
            '/Applications/Utilities',
            '~/Applications'
        ]

        for app_dir in app_dirs:
            try:
                expanded_dir = Path(app_dir).expanduser()
                if expanded_dir.exists():
                    for app_path in expanded_dir.glob('*.app'):
                        app_name = app_path.stem
                        apps.append({
                            'name': app_name,
                            'path': str(app_path),
                            'directory': str(app_dir)
                        })
            except Exception:
                continue

        return sorted(apps, key=lambda x: x['name'])

    def get_app_list(self) -> List[Dict[str, str]]:
        """Get list of all available applications"""
        return self.app_list

    def find_app(self, app_name: str) -> Optional[Dict[str, str]]:
        """Find an app by name (fuzzy matching)"""
        app_name_lower = app_name.lower()

        # Exact match first
        for app in self.app_list:
            if app['name'].lower() == app_name_lower:
                return app

        # Partial match
        for app in self.app_list:
            if app_name_lower in app['name'].lower():
                return app

        return None

    def get_app_controller(self, app_name: str) -> MacApp:
        """Get or create app controller for specific app"""
        if app_name not in self.active_apps:
            self.active_apps[app_name] = MacApp(app_name)
        return self.active_apps[app_name]

    # Universal App Operations
    def launch_app(self, app_name: str, path: str = None) -> Dict[str, Any]:
        """Launch any application by name"""
        app_info = self.find_app(app_name)
        if not app_info:
            return {"ok": False, "error": f"App '{app_name}' not found"}

        try:
            result = launch_any_app(app_info['name'], path)
            return result
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def activate_app(self, app_name: str) -> Dict[str, Any]:
        """Activate and bring app to front"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.activate()
            return {"ok": True, "message": f"Activated {app_name}", "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def quit_app(self, app_name: str) -> Dict[str, Any]:
        """Quit an application"""
        try:
            controller = self.get_app_controller(app_name)
            controller.keystroke("q", ["command"])
            return {"ok": True, "message": f"Quit command sent to {app_name}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Universal UI Operations
    def click_menu(self, app_name: str, menu_path: List[str]) -> Dict[str, Any]:
        """Click menu items in any app"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.menu_click(menu_path)
            return {"ok": True, "message": f"Clicked menu {menu_path} in {app_name}", "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def type_text(self, app_name: str, text: str) -> Dict[str, Any]:
        """Type text in any app"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.type_text(text)
            return {"ok": True, "message": f"Typed text in {app_name}", "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def send_keystroke(self, app_name: str, key: str, modifiers: List[str] = None) -> Dict[str, Any]:
        """Send keystroke to any app"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.keystroke(key, modifiers or [])
            return {"ok": True, "message": f"Sent keystroke {key} to {app_name}", "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def click_ui_element(self, app_name: str, role: str, title: str) -> Dict[str, Any]:
        """Click UI element in any app"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.click_ui(role, title)
            return {"ok": True, "message": f"Clicked {role} '{title}' in {app_name}", "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_app_info(self, app_name: str) -> Dict[str, Any]:
        """Get comprehensive information about an app"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.get_window_info()
            return {"ok": True, "app_info": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def find_ui_elements(self, app_name: str, role: str = None) -> Dict[str, Any]:
        """Find UI elements in any app"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.find_ui_elements(role)
            return {"ok": True, "elements": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Terminal and Code Editor Specific Operations
    def execute_in_terminal_app(self, app_name: str, command: str) -> Dict[str, Any]:
        """Execute command in terminal application"""
        terminal_apps = ['Terminal', 'iTerm', 'Windsurf', 'Visual Studio Code', 'Cursor']

        if app_name not in terminal_apps:
            return {"ok": False, "error": f"{app_name} is not a supported terminal app"}

        try:
            controller = self.get_app_controller(app_name)
            controller.activate()

            if app_name == 'Windsurf':
                # Use Windsurf terminal
                controller.windsurf_terminal()
                time.sleep(1)
            elif app_name in ['Visual Studio Code', 'Cursor']:
                # Toggle integrated terminal
                controller.keystroke("`", ["control"])
                time.sleep(1)

            # Type command and execute
            controller.type_text(command)
            controller.keystroke("return", [])

            return {"ok": True, "message": f"Executed '{command}' in {app_name}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_file_in_editor(self, app_name: str, file_path: str) -> Dict[str, Any]:
        """Open file in code editor"""
        editor_apps = ['Windsurf', 'Visual Studio Code', 'Cursor', 'Sublime Text', 'Atom', 'TextEdit']

        try:
            if app_name in editor_apps:
                controller = self.get_app_controller(app_name)
                result = controller.open_path(file_path)
                return {"ok": True, "message": f"Opened {file_path} in {app_name}", "result": result}
            else:
                # Try generic file opening
                return self.launch_app(app_name, file_path)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Batch Operations
    def batch_app_operation(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple app operations in sequence"""
        results = []

        for op in operations:
            try:
                op_type = op.get('type')
                app_name = op.get('app_name')

                if op_type == 'launch':
                    result = self.launch_app(app_name, op.get('path'))
                elif op_type == 'activate':
                    result = self.activate_app(app_name)
                elif op_type == 'type':
                    result = self.type_text(app_name, op.get('text'))
                elif op_type == 'keystroke':
                    result = self.send_keystroke(app_name, op.get('key'), op.get('modifiers'))
                elif op_type == 'menu':
                    result = self.click_menu(app_name, op.get('menu_path'))
                elif op_type == 'execute':
                    result = self.execute_in_terminal_app(app_name, op.get('command'))
                else:
                    result = {"ok": False, "error": f"Unknown operation type: {op_type}"}

                results.append({"operation": op, "result": result})

                # Wait between operations
                if op.get('wait', 0) > 0:
                    time.sleep(op['wait'])

            except Exception as e:
                results.append({"operation": op, "result": {"ok": False, "error": str(e)}})

        return results

    # App Discovery and Management
    def search_apps(self, query: str) -> List[Dict[str, str]]:
        """Search for apps by name"""
        query_lower = query.lower()
        matches = []

        for app in self.app_list:
            if query_lower in app['name'].lower():
                matches.append(app)

        return sorted(matches, key=lambda x: x['name'])

    def get_running_apps(self) -> List[str]:
        """Get list of currently running applications"""
        try:
            result = subprocess.run([
                'osascript', '-e',
                'tell application "System Events" to get name of every process whose background only is false'
            ], capture_output=True, text=True)

            if result.returncode == 0:
                apps = [app.strip() for app in result.stdout.split(',')]
                return sorted([app for app in apps if app])
            return []
        except Exception:
            return []

    def get_app_windows(self, app_name: str) -> Dict[str, Any]:
        """Get information about app windows"""
        try:
            controller = self.get_app_controller(app_name)
            result = controller.windows()
            return {"ok": True, "windows": result}
        except Exception as e:
            return {"ok": False, "error": str(e)}

# Factory function
def create_universal_app_controller() -> UniversalAppController:
    """Create a new Universal App Controller"""
    return UniversalAppController()