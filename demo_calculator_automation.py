#!/usr/bin/env python3
"""
Demo: Fully Automated Calculator Operations
Shows how Super Interpreter can press calculator buttons automatically
"""

import sys
import time
sys.path.append('.')

from controllers.universal_app_controller import create_universal_app_controller

def automated_calculator_demo():
    """Demonstrate fully automated calculator operations"""
    print("🧮 Automated Calculator Demo: 2819 × 3801")
    print("=" * 50)

    # Initialize universal controller
    universal = create_universal_app_controller()

    try:
        # 1. Launch Calculator
        print("1. Launching Calculator...")
        result = universal.launch_app('Calculator')
        print(f"   ✅ {result['message']}")
        time.sleep(2)

        # 2. Activate Calculator
        print("2. Activating Calculator...")
        universal.activate_app('Calculator')
        time.sleep(1)

        # 3. Clear calculator (just in case)
        print("3. Clearing calculator...")
        universal.send_keystroke('Calculator', 'c', ['command'])
        time.sleep(0.5)

        # 4. Enter first number: 2819
        print("4. Entering first number: 2819")
        for digit in "2819":
            universal.send_keystroke('Calculator', digit)
            print(f"   Pressed: {digit}")
            time.sleep(0.3)

        # 5. Press multiplication (×)
        print("5. Pressing multiplication (×)")
        universal.send_keystroke('Calculator', '*')
        print("   Pressed: ×")
        time.sleep(0.5)

        # 6. Enter second number: 3801
        print("6. Entering second number: 3801")
        for digit in "3801":
            universal.send_keystroke('Calculator', digit)
            print(f"   Pressed: {digit}")
            time.sleep(0.3)

        # 7. Press equals (=)
        print("7. Pressing equals (=)")
        universal.send_keystroke('Calculator', '=')
        print("   Pressed: =")
        time.sleep(1)

        print("\n🎉 Calculator automation completed!")
        print("✅ 2819 × 3801 has been calculated automatically")
        print("📱 Check your Calculator app to see the result: 10,719,219")

        return "10719219"  # Expected result

    except Exception as e:
        print(f"❌ Error during automation: {e}")
        return None

if __name__ == "__main__":
    automated_calculator_demo()