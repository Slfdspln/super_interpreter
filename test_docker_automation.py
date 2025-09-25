#!/usr/bin/env python3

"""
Test Docker automation capabilities
Tests both native Docker Desktop UI automation and web interface interaction
"""

import sys
import os
import time

# Add controllers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'controllers'))

from app_controller_macos import docker, launch_any_app
from browser_controller import BrowserController

def test_docker_desktop_native():
    """Test Docker Desktop native app automation"""
    print("=== Testing Docker Desktop Native Automation ===")

    # Launch Docker Desktop if not running
    print("1. Launching Docker Desktop...")
    launch_result = launch_any_app("Docker Desktop")
    print(f"Launch result: {launch_result}")

    time.sleep(3)  # Give Docker time to start

    # Create Docker app instance
    docker_app = docker()

    # Test basic app activation
    print("\n2. Testing app activation...")
    try:
        activate_result = docker_app.activate()
        print(f"Activate result: {activate_result}")
    except Exception as e:
        print(f"Activation failed: {e}")
        return False

    # Test window information
    print("\n3. Getting window information...")
    try:
        windows_info = docker_app.get_window_info()
        print(f"Windows info: {windows_info}")
    except Exception as e:
        print(f"Window info failed: {e}")

    # Test UI element discovery
    print("\n4. Finding UI elements...")
    try:
        ui_elements = docker_app.find_ui_elements("button")
        print(f"Found {len(ui_elements.get('elements', []))} buttons")
        if ui_elements.get('elements'):
            print("Sample buttons:")
            for i, element in enumerate(ui_elements['elements'][:5]):
                print(f"  - {element}")
    except Exception as e:
        print(f"UI element discovery failed: {e}")

    # Test Docker-specific functions
    print("\n5. Testing Docker-specific functions...")

    # Test navigation to containers tab
    try:
        containers_result = docker_app.docker_open_containers_tab()
        print(f"Open containers tab: {containers_result}")
        time.sleep(1)
    except Exception as e:
        print(f"Containers tab navigation failed: {e}")

    # Test navigation to images tab
    try:
        images_result = docker_app.docker_open_images_tab()
        print(f"Open images tab: {images_result}")
        time.sleep(1)
    except Exception as e:
        print(f"Images tab navigation failed: {e}")

    print("=== Docker Desktop Native Test Complete ===\n")
    return True

def test_docker_web_interface():
    """Test Docker web interface automation with Playwright"""
    print("=== Testing Docker Web Interface Automation ===")

    # Create browser controller
    try:
        browser = BrowserController(headed=True)
        print("1. Browser controller created")
    except Exception as e:
        print(f"Browser controller creation failed: {e}")
        return False

    # Test Docker web interface connection
    print("\n2. Testing Docker web interface connection...")
    try:
        # Try common Docker web interface ports
        ports_to_try = [9000, 8080, 3000, 5000]

        for port in ports_to_try:
            print(f"   Trying port {port}...")
            try:
                result = browser.docker_web_interface(port)
                if result.get("ok"):
                    print(f"   Successfully connected to localhost:{port}")
                    break
            except Exception as e:
                print(f"   Port {port} failed: {e}")
                continue
        else:
            print("   No Docker web interface found on common ports")
            print("   Testing general localhost connection...")
            try:
                result = browser.goto("http://localhost:8080")
                print(f"   Localhost test result: {result}")
            except Exception as e:
                print(f"   Localhost test failed: {e}")

    except Exception as e:
        print(f"Web interface test failed: {e}")

    # Test Docker-specific Playwright enhancements
    print("\n3. Testing Docker Playwright enhancements...")
    try:
        selectors_result = browser.interact_with_docker_containers()
        print(f"Docker selectors setup: {selectors_result.get('ok', False)}")
        if selectors_result.get('selectors'):
            print("Available Docker selectors:")
            for key, selector in selectors_result['selectors'].items():
                print(f"  {key}: {selector}")
    except Exception as e:
        print(f"Docker selectors test failed: {e}")

    print("=== Docker Web Interface Test Complete ===\n")
    return True

def test_docker_cli_integration():
    """Test Docker CLI integration for verification"""
    print("=== Testing Docker CLI Integration ===")

    import subprocess

    # Test if Docker is installed and running
    try:
        result = subprocess.run(['docker', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Docker CLI available: {result.stdout.strip()}")
        else:
            print("Docker CLI not available")
            return False
    except Exception as e:
        print(f"Docker CLI test failed: {e}")
        return False

    # Test Docker daemon status
    try:
        result = subprocess.run(['docker', 'info'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("Docker daemon is running")

            # Get container count
            result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                containers = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
                print(f"Found {len(containers)} containers total")
                if containers:
                    print("Container names:")
                    for container in containers[:5]:  # Show first 5
                        print(f"  - {container}")

        else:
            print("Docker daemon not running or accessible")
            return False
    except Exception as e:
        print(f"Docker daemon test failed: {e}")
        return False

    print("=== Docker CLI Integration Test Complete ===\n")
    return True

def main():
    """Run all Docker automation tests"""
    print("Starting Docker Automation Tests...\n")

    results = []

    # Test CLI integration first
    cli_result = test_docker_cli_integration()
    results.append(("Docker CLI Integration", cli_result))

    # Test native Docker Desktop automation
    native_result = test_docker_desktop_native()
    results.append(("Docker Desktop Native", native_result))

    # Test web interface automation
    web_result = test_docker_web_interface()
    results.append(("Docker Web Interface", web_result))

    # Print summary
    print("=== TEST SUMMARY ===")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, success in results if success)
    print(f"\nPassed: {total_passed}/{len(results)} tests")

    return total_passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)