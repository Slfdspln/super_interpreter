#!/usr/bin/python3
"""
Simple Cristal launcher - bypasses environment issues
"""

import subprocess
import sys

def open_website(url, browser='chrome'):
    """Open website in browser"""
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
        print(f"✅ Opened {url} in {browser_name}")
    except Exception as e:
        print(f"❌ Error: {e}")

def open_app(app_name, path=None):
    """Launch app"""
    try:
        cmd = ['open', '-a', app_name]
        if path:
            cmd.append(path)
        subprocess.run(cmd)

        msg = f"✅ Launched {app_name}"
        if path:
            msg += f" with {path}"
        print(msg)
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🤖 Simple Cristal Launcher")
    print("=" * 30)
    print()
    print("Available commands:")
    print("1. open_website(url, browser)")
    print("2. open_app(app_name)")
    print("3. Python code execution")
    print()
    print("Examples:")
    print(">>> open_website('github.com', 'chrome')")
    print(">>> open_app('Calculator')")
    print(">>> import os; os.listdir('.')")
    print()

    # Make functions available globally
    globals()['open_website'] = open_website
    globals()['open_app'] = open_app

    try:
        import code
        console = code.InteractiveConsole(globals())
        console.interact()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()