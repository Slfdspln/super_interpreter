#!/usr/bin/env python3
"""
Universal launcher for websites and applications
Supports Chrome, Brave, Safari and any macOS application
"""

import subprocess
import sys
import urllib.parse
from pathlib import Path
from controllers.app_controller_macos import MacApp, chrome

class UniversalLauncher:
    def __init__(self):
        self.browsers = {
            'chrome': 'Google Chrome',
            'brave': 'Brave Browser',
            'safari': 'Safari',
            'firefox': 'Firefox'
        }

    def open_website(self, url: str, browser: str = 'chrome') -> dict:
        """Open a website in the specified browser"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'

            # Validate URL
            parsed = urllib.parse.urlparse(url)
            if not parsed.netloc:
                return {"ok": False, "error": "Invalid URL format"}

            browser_name = self.browsers.get(browser.lower(), browser)

            # Open URL in browser
            result = subprocess.run([
                'open', '-a', browser_name, url
            ], capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    "ok": True,
                    "message": f"Opened {url} in {browser_name}",
                    "url": url,
                    "browser": browser_name
                }
            else:
                return {
                    "ok": False,
                    "error": f"Failed to open {browser_name}: {result.stderr}"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_app(self, app_name: str, path: str = None) -> dict:
        """Launch any macOS application, optionally with a file/folder"""
        try:
            cmd = ['open', '-a', app_name]
            if path:
                cmd.append(path)

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                message = f"Launched {app_name}"
                if path:
                    message += f" with {path}"
                return {
                    "ok": True,
                    "message": message,
                    "app": app_name,
                    "path": path
                }
            else:
                return {
                    "ok": False,
                    "error": f"Failed to launch {app_name}: {result.stderr}"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_installed_browsers(self) -> list:
        """Get list of installed browsers"""
        installed = []
        for browser_key, browser_name in self.browsers.items():
            try:
                # Quick check if app exists by trying to get its path
                result = subprocess.run([
                    'osascript', '-e', f'tell application "Finder" to get POSIX path of (path to application "{browser_name}")'
                ], capture_output=True, text=True, timeout=5)

                if result.returncode == 0 and result.stdout.strip():
                    installed.append(browser_key)
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                # If the app doesn't exist or times out, skip it
                pass
        return installed

    def list_applications(self, pattern: str = None) -> list:
        """List installed applications, optionally filtered by pattern"""
        try:
            # Use ls command to list Applications folder - much faster
            apps = []

            # Check /Applications
            for app_dir in ['/Applications', '/System/Applications']:
                try:
                    result = subprocess.run(['ls', app_dir],
                                          capture_output=True, text=True, timeout=10)

                    for line in result.stdout.strip().split('\n'):
                        if line.endswith('.app'):
                            app_name = line[:-4]  # Remove .app extension
                            if pattern is None or pattern.lower() in app_name.lower():
                                apps.append({
                                    'name': app_name,
                                    'path': f"{app_dir}/{line}"
                                })
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    continue

            return sorted(apps, key=lambda x: x['name'])
        except Exception as e:
            return []

def main():
    launcher = UniversalLauncher()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python universal_launcher.py website <url> [browser]")
        print("  python universal_launcher.py app <app_name> [file_path]")
        print("  python universal_launcher.py list-browsers")
        print("  python universal_launcher.py list-apps [pattern]")
        print()
        print("Examples:")
        print("  python universal_launcher.py website github.com chrome")
        print("  python universal_launcher.py website https://google.com brave")
        print("  python universal_launcher.py app Windsurf")
        print("  python universal_launcher.py app 'Visual Studio Code' /path/to/project")
        return

    command = sys.argv[1].lower()

    if command == 'website':
        if len(sys.argv) < 3:
            print("Error: URL required")
            return

        url = sys.argv[2]
        browser = sys.argv[3] if len(sys.argv) > 3 else 'chrome'

        result = launcher.open_website(url, browser)
        if result["ok"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['error']}")

    elif command == 'app':
        if len(sys.argv) < 3:
            print("Error: App name required")
            return

        app_name = sys.argv[2]
        file_path = sys.argv[3] if len(sys.argv) > 3 else None

        result = launcher.open_app(app_name, file_path)
        if result["ok"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result['error']}")

    elif command == 'list-browsers':
        browsers = launcher.get_installed_browsers()
        print("Installed browsers:")
        for browser in browsers:
            print(f"  - {browser}")

    elif command == 'list-apps':
        pattern = sys.argv[2] if len(sys.argv) > 2 else None
        apps = launcher.list_applications(pattern)

        if pattern:
            print(f"Applications matching '{pattern}':")
        else:
            print("All applications (showing first 20):")

        for app in apps[:20]:
            print(f"  - {app['name']}")

        if len(apps) > 20:
            print(f"  ... and {len(apps) - 20} more")

    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()