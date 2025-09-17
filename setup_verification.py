#!/usr/bin/env python3
"""
Super Interpreter Setup Verification Script
Automatically checks all requirements and permissions
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_status(check, status, details=""):
    """Print a status line with emoji"""
    emoji = "✅" if status else "❌"
    print(f"{emoji} {check}: {'PASS' if status else 'FAIL'}")
    if details:
        print(f"   {details}")

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    is_valid = version.major == 3 and version.minor >= 9
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    return is_valid, version_str

def check_python_path():
    """Get the current Python executable path"""
    return sys.executable

def check_venv():
    """Check if running in virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def check_packages():
    """Check if required packages are installed"""
    required_packages = {
        'interpreter': 'open-interpreter',
        'anthropic': 'anthropic',
    }

    results = {}
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            results[pip_name] = True
        except ImportError:
            results[pip_name] = False

    return results

def check_accessibility_permissions():
    """Check if accessibility permissions are granted"""
    try:
        # Try to access system events - this will fail if no accessibility permission
        result = subprocess.run([
            'osascript', '-e',
            'tell application "System Events" to get name of every process'
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

def check_controllers():
    """Check if controller modules are available"""
    controllers = {
        'Universal App Controller': 'controllers.universal_app_controller',
        'Document Automation': 'controllers.document_automation_controller',
        'Browser Use Controller': 'controllers.browser_use_controller',
    }

    results = {}
    for name, module_path in controllers.items():
        try:
            __import__(module_path)
            results[name] = True
        except ImportError as e:
            results[name] = False

    return results

def check_api_keys():
    """Check if API keys are configured"""
    api_keys = {
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    }

    configured = any(key for key in api_keys.values() if key)
    return configured, api_keys

def test_automation_functions():
    """Test basic automation functionality"""
    try:
        from controllers.universal_app_controller import create_universal_app_controller
        controller = create_universal_app_controller()

        # Test basic functions
        apps = controller.get_app_list()
        running = controller.get_running_apps()

        return len(apps) > 0 and len(running) > 0, f"Found {len(apps)} apps, {len(running)} running"
    except Exception as e:
        return False, str(e)

def test_calculation_functions():
    """Test calculation automation"""
    try:
        from controllers.document_automation_controller import create_document_automation_controller
        doc_automation = create_document_automation_controller("Test User")

        # Test calculation
        result = doc_automation.evaluate_expression("2 + 2")
        return result == 4.0, f"Calculation test: 2 + 2 = {result}"
    except Exception as e:
        return False, str(e)

def provide_setup_instructions():
    """Provide setup instructions based on failed checks"""
    print("\n" + "="*60)
    print("🛠️ SETUP INSTRUCTIONS")
    print("="*60)

    print("\n📋 If you see failures above, follow these steps:")

    print("\n1. 🐍 Python Environment:")
    print("   python3 -m venv .venv")
    print("   source .venv/bin/activate")
    print("   pip install -U pip open-interpreter anthropic")

    print("\n2. 🔑 API Keys (choose one):")
    print("   export ANTHROPIC_API_KEY=your-anthropic-key")
    print("   # OR")
    print("   export OPENAI_API_KEY=your-openai-key")

    print("\n3. 🔒 Accessibility Permissions:")
    print("   - Open System Settings > Privacy & Security > Accessibility")
    print(f"   - Add this Python path: {check_python_path()}")
    print("   - Also add Terminal.app")
    print("   - Check the boxes to enable permissions")

    print("\n4. 🧪 Test Again:")
    print("   python setup_verification.py")

def main():
    """Main verification routine"""
    print("🚀 Super Interpreter Setup Verification")
    print("Checking all requirements and permissions...")

    # Track overall status
    all_passed = True

    # Check Python version
    print_header("Python Environment")
    python_ok, version = check_python_version()
    print_status("Python Version (≥3.9)", python_ok, f"Current: {version}")
    all_passed &= python_ok

    # Check virtual environment
    venv_ok = check_venv()
    print_status("Virtual Environment", venv_ok, "Running in .venv" if venv_ok else "Not in virtual environment")

    # Check Python path
    python_path = check_python_path()
    print_status("Python Path", True, python_path)

    # Check packages
    print_header("Required Packages")
    packages = check_packages()
    for package, installed in packages.items():
        print_status(f"Package: {package}", installed)
        all_passed &= installed

    # Check API keys
    print_header("API Configuration")
    api_configured, api_keys = check_api_keys()
    print_status("API Key Configured", api_configured)
    if api_configured:
        for key, value in api_keys.items():
            if value:
                print_status(f"{key}", True, "Configured")
    all_passed &= api_configured

    # Check controllers
    print_header("Controller Modules")
    controllers = check_controllers()
    for name, available in controllers.items():
        print_status(name, available)
        all_passed &= available

    # Check accessibility permissions
    print_header("macOS Permissions")
    accessibility_ok = check_accessibility_permissions()
    print_status("Accessibility Permissions", accessibility_ok,
                "Python can control other apps" if accessibility_ok else "Python needs accessibility permission")
    all_passed &= accessibility_ok

    # Test automation functions
    print_header("Automation Tests")
    automation_ok, automation_details = test_automation_functions()
    print_status("App Control Functions", automation_ok, automation_details)

    calc_ok, calc_details = test_calculation_functions()
    print_status("Calculation Functions", calc_ok, calc_details)

    # Final status
    print_header("Overall Status")
    if all_passed and accessibility_ok and automation_ok and calc_ok:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your Super Interpreter is ready to use!")
        print("\nTo start: ./cristal-clean")
    else:
        print("⚠️ SOME CHECKS FAILED")
        print("❌ Setup is incomplete")
        provide_setup_instructions()

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)