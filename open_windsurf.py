#!/usr/bin/env python3
"""
Script to open Windsurf using the browser controller
"""

from controllers.browser_controller import BrowserController

def main():
    # Initialize the browser controller
    browser = BrowserController("policy.yaml", headed=True)

    print("Opening Windsurf...")

    # Try to open Windsurf website
    result = browser.goto("https://windsurf.codeium.com")

    if result["ok"]:
        print(f"✅ Successfully opened Windsurf!")
        print(f"   Title: {result['title']}")
        print(f"   URL: {result['url']}")

        # Take a screenshot for verification
        screenshot_result = browser.screenshot("windsurf_screenshot.png")
        if screenshot_result["ok"]:
            print(f"📸 Screenshot saved: {screenshot_result['path']}")
    else:
        print(f"❌ Failed to open Windsurf: {result['error']}")

if __name__ == "__main__":
    main()