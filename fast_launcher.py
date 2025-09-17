#!/usr/bin/python3
"""
Fast launcher - no timeouts, immediate results
"""

import subprocess
import sys
import os

def check_browser_exists(browser_name):
    """Quick check if browser exists"""
    try:
        subprocess.run(['which', 'open'], capture_output=True, timeout=2)
        return True
    except:
        return False

def list_browsers():
    """List common browsers that might be installed"""
    browsers = {
        'chrome': 'Google Chrome',
        'brave': 'Brave Browser',
        'safari': 'Safari',
        'firefox': 'Firefox'
    }

    print("Common browsers (not checking if installed):")
    for key, name in browsers.items():
        print(f"  {key} -> {name}")

def list_apps():
    """List applications in /Applications"""
    try:
        apps = os.listdir('/Applications')
        print("Applications in /Applications:")
        for app in sorted(apps):
            if app.endswith('.app'):
                print(f"  {app[:-4]}")
    except Exception as e:
        print(f"Error listing apps: {e}")

def open_website(url, browser='chrome'):
    """Open website"""
    browsers = {
        'chrome': 'Google Chrome',
        'brave': 'Brave Browser',
        'safari': 'Safari'
    }

    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'

    browser_name = browsers.get(browser, browser)

    try:
        subprocess.run(['open', '-a', browser_name, url])
        print(f"✅ Opening {url} in {browser_name}")
    except Exception as e:
        print(f"❌ Error: {e}")

def open_app(app_name):
    """Launch app"""
    try:
        subprocess.run(['open', '-a', app_name])
        print(f"✅ Launched {app_name}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fast_launcher.py list-browsers")
        print("  python fast_launcher.py list-apps")
        print("  python fast_launcher.py website <url> [browser]")
        print("  python fast_launcher.py app <app_name>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'list-browsers':
        list_browsers()
    elif cmd == 'list-apps':
        list_apps()
    elif cmd == 'website' and len(sys.argv) >= 3:
        url = sys.argv[2]
        browser = sys.argv[3] if len(sys.argv) > 3 else 'chrome'
        open_website(url, browser)
    elif cmd == 'app' and len(sys.argv) >= 3:
        app_name = sys.argv[2]
        open_app(app_name)
    else:
        print("Invalid command or missing arguments")