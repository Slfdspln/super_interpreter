#!/usr/bin/env python3
"""
Test Windsurf terminal automation
"""

import sys
import time
sys.path.append('.')

from controllers.app_controller_macos import windsurf

def test_windsurf_terminal():
    """Test Windsurf terminal automation"""
    print("🧪 Testing Windsurf Terminal Automation")
    print("=" * 40)

    # Initialize Windsurf controller
    w = windsurf()

    try:
        # 1. Activate Windsurf
        print("1. Activating Windsurf...")
        result = w.activate()
        print(f"   ✅ Result: {result}")
        time.sleep(1)

        # 2. Open terminal
        print("2. Opening terminal...")
        result = w.windsurf_terminal()
        print(f"   ✅ Result: {result}")
        time.sleep(2)

        # 3. Execute a simple command
        print("3. Executing 'echo Hello from Super Interpreter!'...")
        w.type_text("echo 'Hello from Super Interpreter!'")
        time.sleep(0.5)
        w.keystroke("return", [])
        print("   ✅ Command sent")
        time.sleep(2)

        # 4. Execute Python command
        print("4. Executing Python command...")
        w.type_text("python3 -c \"print('Python works in Windsurf!')\"")
        time.sleep(0.5)
        w.keystroke("return", [])
        print("   ✅ Python command sent")
        time.sleep(2)

        # 5. List files
        print("5. Listing files...")
        w.type_text("ls -la")
        time.sleep(0.5)
        w.keystroke("return", [])
        print("   ✅ ls command sent")

        print("\n🎉 Windsurf terminal automation test completed!")
        print("Check your Windsurf terminal to see the results.")

        return True

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    test_windsurf_terminal()