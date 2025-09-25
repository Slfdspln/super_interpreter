#!/usr/bin/env python3

"""
Test if the initialization code loads Docker controllers properly
"""

# Execute the same init code that run.py uses
init_code = r"""
from controllers.browser_controller import BrowserController
from controllers.scrapling_controller import ScraplingController
from controllers.os_controller import OSController
from controllers.app_controller_macos import MacApp, launch_any_app, windsurf, chrome, safari, vscode, terminal, finder, brave, calculator, docker
from controllers.ui_controller import SystemUIController
from controllers.vision_controller import VisionController
from controllers.gesture_controller import GestureController
from controllers.calculator_optimized import OptimizedCalculatorController, quick_calculate
from controllers.calculator_fixed import FixedCalculatorController, fixed_calc
from controllers.calculator_jxa import jxa_calc, click_calc_buttons, calc_expression, calc_209_x_3909
from controllers.docker_controller import DockerController, get_docker_controller, quick_container_start, quick_container_stop, quick_container_list
from controllers.memory import save_doc, list_docs, get_doc, search_docs, get_stats, quick_save

browser = BrowserController("policy.yaml", headed=True)
scraper = ScraplingController("policy.yaml")
osctl   = OSController("policy.yaml")
windsurf = MacApp("Windsurf")

# Universal UI automation controllers
ui = SystemUIController()
vision = VisionController()
gestures = GestureController()
calc = calculator()  # Standard calculator
calc_optimized = OptimizedCalculatorController()  # CPU-efficient calculator
calc_fixed = fixed_calc  # Robust calculator with proven JXA automation
jxa_calc = jxa_calc  # PROVEN JXA Calculator automation that WORKS

# Docker automation controllers
docker_app = docker()  # Native Docker Desktop app controller
docker_controller = get_docker_controller()  # Comprehensive Docker controller with UI+CLI fallbacks
docker_web_preferred = get_docker_controller(prefer_web=True)  # Web-interface preferred Docker controller

# Memory functions are available directly
memory_stats = get_stats()

print("✅ All imports successful!")
print(f"Docker controller available: {docker_controller is not None}")
print(f"Docker app controller available: {docker_app is not None}")

# Test basic Docker functionality
try:
    containers = docker_controller.list_containers()
    print(f"✅ Docker operations work: {containers.get('ok', False)}")
    print(f"Containers found: {containers.get('count', 0)}")
except Exception as e:
    print(f"❌ Docker operations failed: {e}")

print("\n🐳 Docker automation methods available:")
print("- docker_controller.list_containers()")
print("- docker_controller.start_container('name')")
print("- docker_controller.stop_container('name')")
print("- docker_app.docker_open_containers_tab()")
print("- quick_container_list()")
"""

try:
    exec(init_code)
    print("\n🎉 All automation controllers loaded successfully!")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()