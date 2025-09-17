#!/usr/bin/env python3
"""
Demo script showing website and app launching capabilities
"""

from controllers.browser_controller import BrowserController
from controllers.app_controller_macos import launch_any_app, MacApp, chrome, brave

def demo_website_opening():
    print("🌐 Website Opening Demo")
    print("="*40)

    # Using browser controller with native browser opening
    browser = BrowserController("policy.yaml", headed=False)

    # Open websites in different browsers
    sites = [
        ("https://github.com", "chrome"),
        ("https://google.com", "brave"),
        ("https://anthropic.com", "safari")
    ]

    for url, browser_name in sites:
        print(f"\n📱 Opening {url} in {browser_name}...")
        result = browser.open_in_native_browser(url, browser_name)
        if result["ok"]:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ {result['error']}")

def demo_app_launching():
    print("\n📱 Application Launching Demo")
    print("="*40)

    # Common apps to test
    apps = [
        "Calculator",
        "TextEdit",
        "System Preferences",
        "Activity Monitor"
    ]

    for app in apps:
        print(f"\n🚀 Launching {app}...")
        result = launch_any_app(app)
        if result["ok"]:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ {result['error']}")

def demo_browser_control():
    print("\n🎮 Browser Control Demo")
    print("="*40)

    # Control Chrome directly
    chrome_app = chrome()
    print("\n📱 Activating Chrome...")
    try:
        chrome_app.activate()
        print("   ✅ Chrome activated")

        # Open a new tab with Cmd+T
        print("📱 Opening new tab...")
        chrome_app.keystroke("t", ["command"])
        print("   ✅ New tab opened")

    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 Super Interpreter - Universal Launcher Demo")
    print("=" * 50)

    try:
        demo_website_opening()
        demo_app_launching()
        demo_browser_control()

        print("\n🎉 Demo complete! Your project can now:")
        print("   • Open any website in Chrome, Brave, or Safari")
        print("   • Launch any macOS application")
        print("   • Control browser tabs and interactions")
        print("   • Automate complex workflows")

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")