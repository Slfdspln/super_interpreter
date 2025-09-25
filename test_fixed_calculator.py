#!/usr/bin/env python3
"""
Test the fixed Calculator automation with 76 × 2
"""

import sys
sys.path.append('.')

from controllers.calculator_fixed import fixed_calc

def test_calculator_automation():
    print("🧮 TESTING FIXED CALCULATOR AUTOMATION")
    print("=" * 50)
    print("Testing: 76 × 2")
    print()

    # Test the robust calculation method
    result = fixed_calc.calculate_robust("76*2")

    print("📊 RESULT:")
    print(f"   Success: {result['ok']}")
    print(f"   Method: {result.get('method', 'unknown')}")
    print(f"   Expression: {result.get('expression', 'unknown')}")
    print(f"   Result: {result.get('result', 'unknown')}")

    if not result['ok']:
        print(f"   Error: {result.get('error', 'unknown')}")

    print()
    if result['ok']:
        print("✅ CALCULATOR AUTOMATION WORKING!")
        print(f"✅ 76 × 2 = {result['result']}")
    else:
        print("❌ Calculator automation failed")
        print("🔧 This might need accessibility permissions")

    print()
    print("📋 PERMISSIONS NEEDED:")
    print("1. System Settings → Privacy & Security → Accessibility")
    print("   → Enable for Terminal/iTerm")
    print("2. System Settings → Privacy & Security → Automation")
    print("   → Enable System Events and Calculator for Terminal/iTerm")

if __name__ == "__main__":
    test_calculator_automation()