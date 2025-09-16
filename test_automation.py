#!/usr/bin/env python3

# Quick test script to verify automation permissions
from controllers.app_controller_macos import MacApp

def test_automation():
    try:
        # Test opening TextEdit and typing
        textedit = MacApp("TextEdit")

        print("Testing automation permissions...")
        print("1. Activating TextEdit...")
        result = textedit.activate()
        print(f"   Result: {result}")

        print("2. Typing test text...")
        result = textedit.type_text("Hello World! Automation is working! 🎉")
        print(f"   Result: {result}")

        print("\n✅ If you see 'Hello World!' in TextEdit, automation is working!")
        print("❌ If you got permission errors, Python needs accessibility access.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("This usually means Python doesn't have accessibility permissions yet.")

if __name__ == "__main__":
    test_automation()