#!/usr/bin/env python3
"""
Super Interpreter - Automated macOS Permissions Setup
Streamlines the process of granting Accessibility permissions.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_python_path():
    """Get the current Python executable path."""
    return sys.executable

def test_accessibility_permissions():
    """Test if we have accessibility permissions."""
    try:
        # Try to use System Events via osascript
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to return "OK"'
        ], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def open_accessibility_settings():
    """Open System Settings to Accessibility page."""
    subprocess.run([
        'open',
        'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
    ])

def copy_to_clipboard(text):
    """Copy text to clipboard."""
    try:
        subprocess.run(['pbcopy'], input=text.encode(), check=True)
        return True
    except:
        return False

def main():
    print("🤖 Super Interpreter - macOS Permissions Setup")
    print("=" * 50)

    python_path = get_python_path()
    python_dir = str(Path(python_path).parent)

    print(f"📍 Your Python binary location:")
    print(f"   {python_path}")
    print()

    # Test current permissions
    print("🔍 Testing current permissions...")
    if test_accessibility_permissions():
        print("✅ Accessibility permissions are already granted!")
        print("🎉 You're all set! Run 'cristal' to start automating.")
        return

    print("❌ Accessibility permissions needed.")
    print()

    # Auto-open settings
    print("🔧 Opening System Settings for you...")
    open_accessibility_settings()
    print("✅ System Settings → Privacy & Security → Accessibility should be open.")
    print()

    # Copy path to clipboard
    if copy_to_clipboard(python_dir):
        print("📋 Python directory path copied to clipboard!")
        print()

    print("📝 Please follow these steps:")
    print("1. Click the 🔒 lock icon and enter your password")
    print("2. Click the ➕ plus button to add an app")
    print("3. In the file picker, press ⌘+Shift+G (Go to Folder)")
    print("4. Paste the path (already in clipboard):")
    print(f"   {python_dir}")
    print("5. Select the 'python' file (no extension)")
    print("6. Toggle it ON")
    print()

    input("Press Enter after granting permissions to test...")

    # Test again
    print("🔍 Testing permissions again...")
    if test_accessibility_permissions():
        print("✅ Success! Accessibility permissions granted.")
        print("🎉 You're ready! Run 'cristal' to start the Super Interpreter.")
    else:
        print("❌ Still no permissions. Please check the steps above.")
        print("💡 Tip: Make sure you selected the 'python' file, not the folder.")

if __name__ == "__main__":
    main()