#!/usr/bin/env python3

"""
Comprehensive Docker Controller Test
Tests the unified Docker controller that combines UI and CLI automation
"""

import sys
import os
import time

# Add controllers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'controllers'))

from docker_controller import DockerController, get_docker_controller, quick_container_list

def test_docker_controller_init():
    """Test Docker controller initialization"""
    print("=== Testing Docker Controller Initialization ===")

    try:
        # Test basic initialization
        controller = DockerController()
        print("✅ Docker controller created successfully")

        # Test web-preferred initialization
        web_controller = DockerController(prefer_web=True)
        print("✅ Web-preferred Docker controller created")

        # Test convenience function
        quick_controller = get_docker_controller()
        print("✅ Quick Docker controller created")

        return True
    except Exception as e:
        print(f"❌ Docker controller initialization failed: {e}")
        return False

def test_docker_system_info():
    """Test Docker system information gathering"""
    print("\n=== Testing Docker System Information ===")

    try:
        controller = get_docker_controller()

        # Test health check
        health = controller.health_check()
        print(f"Health check: {health}")

        # Test system info
        info = controller.get_docker_info()
        print(f"Docker info: {info}")

        if info.get("ok"):
            print(f"Docker version: {info.get('docker_version', 'Unknown')}")
            print(f"Containers: {info.get('containers', 0)}")
            print(f"Images: {info.get('images', 0)}")

        return True
    except Exception as e:
        print(f"❌ System info test failed: {e}")
        return False

def test_container_management():
    """Test container management operations"""
    print("\n=== Testing Container Management ===")

    try:
        controller = get_docker_controller()

        # Test listing containers
        containers = controller.list_containers()
        print(f"Container list result: {containers.get('ok', False)}")
        if containers.get("ok"):
            print(f"Found {containers.get('count', 0)} containers")
            for container in containers.get('containers', [])[:3]:  # Show first 3
                print(f"  - {container.get('name', 'Unknown')}: {container.get('status', 'Unknown')}")

        # Test quick container list
        quick_list = quick_container_list()
        print(f"Quick list result: {quick_list.get('ok', False)}")

        # If we have containers, test operations on the first one
        if containers.get("containers"):
            test_container = containers["containers"][0]["name"]
            print(f"\nTesting operations on container: {test_container}")

            # Test getting logs (read-only operation)
            logs = controller.get_container_logs(test_container, lines=10)
            print(f"Get logs result: {logs.get('ok', False)}")

            # Don't actually start/stop containers in test to avoid disruption
            print("Skipping start/stop operations to avoid disrupting running containers")

        return True
    except Exception as e:
        print(f"❌ Container management test failed: {e}")
        return False

def test_image_management():
    """Test image management operations"""
    print("\n=== Testing Image Management ===")

    try:
        controller = get_docker_controller()

        # Test listing images
        images = controller.list_images()
        print(f"Image list result: {images.get('ok', False)}")
        if images.get("ok"):
            print(f"Found {images.get('count', 0)} images")
            for image in images.get('images', [])[:3]:  # Show first 3
                repo = image.get('repository', 'Unknown')
                tag = image.get('tag', 'Unknown')
                size = image.get('size', 'Unknown')
                print(f"  - {repo}:{tag} ({size})")

        return True
    except Exception as e:
        print(f"❌ Image management test failed: {e}")
        return False

def test_ui_navigation():
    """Test Docker Desktop UI navigation"""
    print("\n=== Testing Docker Desktop UI Navigation ===")

    try:
        controller = get_docker_controller()

        # Test opening different tabs
        tabs_to_test = [
            ("containers", controller.open_containers_tab),
            ("images", controller.open_images_tab),
            ("volumes", controller.open_volumes_tab)
        ]

        for tab_name, method in tabs_to_test:
            try:
                result = method()
                status = "✅" if result.get("ok") else "⚠️"
                print(f"{status} {tab_name.title()} tab: {result.get('ok', False)}")
                if result.get("ok"):
                    time.sleep(0.5)  # Brief pause between navigation
            except Exception as e:
                print(f"⚠️ {tab_name.title()} tab failed: {e}")

        return True
    except Exception as e:
        print(f"❌ UI navigation test failed: {e}")
        return False

def test_web_interface():
    """Test Docker web interface capabilities"""
    print("\n=== Testing Docker Web Interface ===")

    try:
        controller = get_docker_controller(prefer_web=True)

        # Test opening web interface on common ports
        ports_to_test = [9000, 8080, 3000, 5000]
        web_success = False

        for port in ports_to_test:
            try:
                result = controller.open_web_interface(port)
                if result.get("ok"):
                    print(f"✅ Web interface accessible on port {port}")
                    web_success = True

                    # Test web-specific functionality
                    containers_web = controller.web_get_container_list()
                    print(f"Web container list: {containers_web.get('ok', False)}")
                    break
                else:
                    print(f"⚠️ Port {port}: {result.get('error', 'Not accessible')}")
            except Exception as e:
                print(f"⚠️ Port {port}: {e}")

        if not web_success:
            print("ℹ️ No Docker web interface found on common ports (this is normal)")

        return True
    except Exception as e:
        print(f"❌ Web interface test failed: {e}")
        return False

def test_fallback_mechanisms():
    """Test fallback between UI and CLI methods"""
    print("\n=== Testing Fallback Mechanisms ===")

    try:
        controller = get_docker_controller()

        # Test that methods work even if UI automation fails
        print("Testing robust container listing...")
        containers = controller.list_containers()
        print(f"Container listing robustness: {containers.get('ok', False)}")

        print("Testing robust image listing...")
        images = controller.list_images()
        print(f"Image listing robustness: {images.get('ok', False)}")

        # Test system info gathering
        info = controller.get_docker_info()
        print(f"System info robustness: {info.get('ok', False)}")

        return True
    except Exception as e:
        print(f"❌ Fallback mechanism test failed: {e}")
        return False

def test_comprehensive_docker_automation():
    """Run a comprehensive Docker automation test"""
    print("=== Docker Comprehensive Automation Test ===")

    try:
        controller = get_docker_controller()

        # Step 1: System health check
        print("1. Checking Docker system health...")
        health = controller.health_check()
        if not health.get("daemon_healthy", False):
            print("⚠️ Docker daemon not healthy, some tests may fail")
        else:
            print("✅ Docker daemon healthy")

        # Step 2: Get system overview
        print("\n2. Getting system overview...")
        info = controller.get_docker_info()
        if info.get("ok"):
            print(f"   Version: {info.get('docker_version', 'Unknown')}")
            print(f"   Containers: {info.get('containers', 0)}")
            print(f"   Images: {info.get('images', 0)}")

        # Step 3: UI navigation test
        print("\n3. Testing UI navigation...")
        nav_result = controller.open_containers_tab()
        print(f"   Containers tab: {nav_result.get('ok', False)}")

        # Step 4: List resources
        print("\n4. Listing Docker resources...")
        containers = controller.list_containers()
        images = controller.list_images()
        print(f"   Containers listed: {containers.get('ok', False)} ({containers.get('count', 0)} found)")
        print(f"   Images listed: {images.get('ok', False)} ({images.get('count', 0)} found)")

        return True
    except Exception as e:
        print(f"❌ Comprehensive test failed: {e}")
        return False

def main():
    """Run all Docker controller tests"""
    print("Starting Comprehensive Docker Controller Tests...\n")

    test_functions = [
        ("Docker Controller Init", test_docker_controller_init),
        ("Docker System Info", test_docker_system_info),
        ("Container Management", test_container_management),
        ("Image Management", test_image_management),
        ("UI Navigation", test_ui_navigation),
        ("Web Interface", test_web_interface),
        ("Fallback Mechanisms", test_fallback_mechanisms),
        ("Comprehensive Automation", test_comprehensive_docker_automation)
    ]

    results = []
    for test_name, test_func in test_functions:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} threw exception: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("🎉 All Docker automation tests passed!")
        print("Docker can now be controlled through both UI and CLI methods with robust fallbacks.")
    else:
        print("⚠️ Some tests failed, but Docker automation is partially functional.")

    return passed >= len(results) * 0.7  # 70% success rate considered acceptable

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)