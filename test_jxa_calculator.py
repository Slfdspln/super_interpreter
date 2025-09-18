#!/usr/bin/env python3
"""
Test the JXA Calculator automation
"""

import sys
sys.path.append('.')

def test_jxa_calculator():
    print("🧮 TESTING JXA CALCULATOR AUTOMATION")
    print("=" * 50)

    from controllers.calculator_jxa import jxa_calc, click_calc_buttons, calc_expression

    print("📋 Available methods:")
    print("1. click_calc_buttons(['2','0','9','*','3','9','0','9','='])")
    print("2. calc_expression('209*3909')")
    print("3. jxa_calc.dump_buttons() - see available buttons")
    print()

    # Test button dumping first
    print("🔍 Checking available buttons...")
    dump_result = jxa_calc.dump_buttons()
    print(f"Dump result: {dump_result}")
    print()

    # Test specific calculation
    print("🧮 Testing 209 × 3909 button clicking...")
    button_result = click_calc_buttons(["2","0","9","*","3","9","0","9","="])
    print(f"Button click result: {button_result}")
    print()

    print("🧮 Testing 209 × 3909 expression mode...")
    expr_result = calc_expression("209*3909")
    print(f"Expression result: {expr_result}")
    print()

    if button_result.get("ok") or expr_result.get("ok"):
        print("✅ JXA Calculator automation is working!")
        print("✅ The AI can now click actual Calculator buttons!")
        print("✅ Result should be: 209 × 3909 = 817,981")
    else:
        print("❌ JXA automation needs accessibility permissions")
        print("🔧 Enable: System Settings → Privacy & Security → Accessibility")
        print("🔧 Add: Terminal/iTerm to allowed apps")

    print()
    print("🎯 The AI should now use:")
    print("   - click_calc_buttons() for button sequences")
    print("   - calc_expression() for typing expressions")
    print("   - Both methods click the REAL Calculator app!")

if __name__ == "__main__":
    test_jxa_calculator()