#!/usr/bin/env python3
"""
Quick launcher for websites and apps - simplified version
"""

import subprocess
import sys

def open_website(url, browser='chrome'):
    """Open website in specified browser"""
    browsers = {
        'chrome': 'Google Chrome',
        'brave': 'Brave Browser',
        'safari': 'Safari'
    }

    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    browser_name = browsers.get(browser.lower(), browser)

    try:
        subprocess.run(['open', '-a', browser_name, url], check=True)
        print(f"✅ Opened {url} in {browser_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to open {browser_name}: {e}")
        return False

def open_app(app_name, path=None):
    """Launch any macOS application"""
    try:
        cmd = ['open', '-a', app_name]
        if path:
            cmd.append(path)

        subprocess.run(cmd, check=True)
        msg = f"✅ Launched {app_name}"
        if path:
            msg += f" with {path}"
        print(msg)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch {app_name}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python quick_launcher.py website <url> [browser]")
        print("  python quick_launcher.py app <app_name> [path]")
        print()
        print("Examples:")
        print("  python quick_launcher.py website github.com chrome")
        print("  python quick_launcher.py website google.com brave")
        print("  python quick_launcher.py app Calculator")
        print("  python quick_launcher.py app Windsurf")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'website':
        url = sys.argv[2]
        browser = sys.argv[3] if len(sys.argv) > 3 else 'chrome'
        open_website(url, browser)

    elif command == 'app':
        app_name = sys.argv[2]
        path = sys.argv[3] if len(sys.argv) > 3 else None
        open_app(app_name, path)

    else:
        print(f"Unknown command: {command}")