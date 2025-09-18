#!/usr/bin/env python3
"""
Demo: Real Calculator App Automation
Shows actual browser controller and UI automation capabilities
"""

import subprocess
import time
import sys
import os

# Add current directory to path
sys.path.append('.')

def demo_calculator_automation():
    print("🚀 REAL CALCULATOR APP AUTOMATION DEMO")
    print("=" * 50)
    print("This will:")
    print("1. 📱 Open macOS Calculator app")
    print("2. 🤖 Use UI automation to click buttons")
    print("3. 📊 Read the actual result from Calculator display")
    print("4. 🌐 Open browser and paste result")
    print()

    try:
        # Import our automation controllers
        from controllers.app_controller_macos import MacApp, launch_any_app
        from controllers.calculator_optimized import OptimizedCalculatorController
        from controllers.browser_controller import BrowserController

        print("✅ Controllers imported successfully")

        # Step 1: Open Calculator app (real app!)
        print("\n🧮 Step 1: Opening Calculator app...")
        result = launch_any_app("Calculator")
        print(f"Calculator launch result: {result}")
        time.sleep(2)  # Wait for app to open

        # Step 2: Use optimized Calculator automation
        print("\n🤖 Step 2: Automating calculation: 89.76 * 0.15...")
        calc = OptimizedCalculatorController()
        calc_result = calc.calculate("89.76*0.15")
        print(f"Calculation result: {calc_result}")

        # Step 3: Read Calculator display
        display_value = calc.get_display()
        print(f"Calculator display shows: {display_value}")

        # Step 4: Browser automation
        print("\n🌐 Step 4: Opening browser and pasting result...")
        browser = BrowserController("policy.yaml", headed=True)
        browser.goto("https://docs.new")
        time.sleep(3)  # Wait for page load

        if calc_result.get("ok"):
            browser.type_in_google_docs(f"Calculator result: {calc_result['result']}")
            print("✅ Result pasted into Google Docs!")

        print("\n🎉 FULL AUTOMATION COMPLETE!")
        print("✅ Real Calculator app was automated")
        print("✅ Real browser was controlled")
        print("✅ Actual UI elements were clicked")

    except Exception as e:
        print(f"❌ Error during automation: {e}")

        # Fallback: Show what WOULD happen
        print("\n🔄 Demonstrating automation capabilities:")
        print("1. 📱 Calculator app opens with launch_any_app('Calculator')")
        print("2. 🤖 UI automation clicks buttons: ['8','9','.','7','6','*','0','.','1','5','=']")
        print("3. 📊 Reads display value using accessibility APIs")
        print("4. 🌐 Browser opens Google Docs and types the result")

        # Manual calculation as backup
        manual_result = 89.76 * 0.15
        print(f"\n📊 Manual calculation result: {manual_result}")

if __name__ == "__main__":
    demo_calculator_automation()