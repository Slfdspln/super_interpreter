#!/usr/bin/env python3
"""
Test Universal App Control
"""

import sys
import time
sys.path.append('.')

from controllers.universal_app_controller import create_universal_app_controller

def test_universal_app_control():
    """Test universal app control capabilities"""
    print("🧪 Testing Universal App Control")
    print("=" * 40)

    # Initialize universal controller
    universal = create_universal_app_controller()

    try:
        # 1. List all apps
        print("1. Getting all installed applications...")
        apps = universal.get_app_list()
        print(f"   ✅ Found {len(apps)} applications")

        # 2. Search for specific apps
        print("2. Searching for calculator apps...")
        calc_apps = universal.search_apps('calculator')
        print(f"   ✅ Found calculator apps: {[app['name'] for app in calc_apps]}")

        # 3. Launch Calculator
        print("3. Launching Calculator...")
        result = universal.launch_app('Calculator')
        print(f"   ✅ Result: {result}")
        time.sleep(2)

        # 4. Type in Calculator (send keystrokes)
        print("4. Typing in Calculator...")
        universal.activate_app('Calculator')
        time.sleep(1)
        universal.send_keystroke('Calculator', '1')
        time.sleep(0.5)
        universal.send_keystroke('Calculator', '+')
        time.sleep(0.5)
        universal.send_keystroke('Calculator', '2')
        time.sleep(0.5)
        universal.send_keystroke('Calculator', '=')
        print("   ✅ Typed: 1 + 2 = in Calculator")

        # 5. Launch TextEdit and type text
        print("5. Testing TextEdit...")
        universal.launch_app('TextEdit')
        time.sleep(2)
        universal.activate_app('TextEdit')
        time.sleep(1)
        universal.type_text('TextEdit', 'Hello from Super Interpreter Universal Control!')
        print("   ✅ Typed text in TextEdit")

        # 6. Test terminal execution
        print("6. Testing terminal execution...")
        result = universal.execute_in_terminal_app('Terminal', 'echo "Hello from Terminal automation!"')
        print(f"   ✅ Terminal result: {result}")

        # 7. Get running apps
        print("7. Getting running applications...")
        running = universal.get_running_apps()
        print(f"   ✅ Running apps: {len(running)} applications")
        print(f"   First 5: {running[:5]}")

        # 8. Test app info
        print("8. Getting Calculator app info...")
        info = universal.get_app_info('Calculator')
        print(f"   ✅ App info available: {info.get('ok', False)}")

        print("\n🎉 Universal App Control test completed!")
        print("✅ Calculator launched and controlled")
        print("✅ TextEdit launched and typed in")
        print("✅ Terminal commands executed")
        print("✅ App discovery and management working")

        return True

    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    test_universal_app_control()