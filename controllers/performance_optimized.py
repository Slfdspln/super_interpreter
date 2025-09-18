"""
Performance optimizations for UI automation controllers.
Prevents CPU busy-loops and enables efficient task queuing.
"""

import asyncio
import threading
import time
import subprocess
from queue import Queue, Empty
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, Future

@dataclass
class UITask:
    """Task for UI automation queue"""
    task_type: str
    payload: Dict[str, Any]
    callback: Optional[Callable] = None
    result_queue: Optional[Queue] = None

class OptimizedUIController:
    """CPU-efficient UI controller with task queuing and smart waiting"""

    def __init__(self):
        self.ui_queue = Queue(maxsize=128)
        self.applescript_queue = Queue(maxsize=64)
        self.is_running = True

        # Start worker threads
        self.ui_worker = threading.Thread(target=self._ui_worker, daemon=True)
        self.applescript_worker = threading.Thread(target=self._applescript_worker, daemon=True)

        self.ui_worker.start()
        self.applescript_worker.start()

        # Thread pool for concurrent operations
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _ui_worker(self):
        """Worker thread for UI tasks - blocks instead of spinning"""
        while self.is_running:
            try:
                task = self.ui_queue.get(timeout=1.0)  # Block, don't spin
                result = self._execute_ui_task(task)

                if task.result_queue:
                    task.result_queue.put(result)
                if task.callback:
                    task.callback(result)

                self.ui_queue.task_done()
            except Empty:
                continue  # Timeout is normal, just continue
            except Exception as e:
                print(f"UI worker error: {e}")

    def _applescript_worker(self):
        """Dedicated AppleScript worker to avoid subprocess spawn thrash"""
        while self.is_running:
            try:
                script = self.applescript_queue.get(timeout=1.0)  # Block
                subprocess.run(["osascript", "-e", script],
                             check=False, capture_output=True)
                self.applescript_queue.task_done()

                # Small delay to prevent rapid-fire AppleScript calls
                time.sleep(0.01)  # 10ms throttle
            except Empty:
                continue
            except Exception as e:
                print(f"AppleScript worker error: {e}")

    def _execute_ui_task(self, task: UITask) -> Dict[str, Any]:
        """Execute a single UI task"""
        try:
            if task.task_type == "click":
                return self._direct_click(task.payload)
            elif task.task_type == "type":
                return self._direct_type(task.payload)
            elif task.task_type == "drag":
                return self._direct_drag(task.payload)
            elif task.task_type == "wait_element":
                return self._smart_wait_element(task.payload)
            else:
                return {"ok": False, "error": f"Unknown task type: {task.task_type}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _direct_click(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Direct click without busy-waiting"""
        x, y = payload["x"], payload["y"]
        script = f"""
        tell application "System Events"
            click at {{{x}, {y}}}
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
            return {"ok": True, "coordinates": [x, y]}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": str(e)}

    def _direct_type(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Direct typing without delays"""
        text = payload["text"]
        script = f'tell application "System Events" to keystroke "{text}"'

        try:
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
            return {"ok": True, "text": text}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": str(e)}

    def _smart_wait_element(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Smart waiting with exponential backoff - no busy-loop"""
        app_name = payload["app_name"]
        role = payload["role"]
        title = payload["title"]
        timeout = payload.get("timeout", 10)

        start_time = time.time()
        wait_interval = 0.1  # Start with 100ms
        max_interval = 1.0   # Cap at 1 second

        while time.time() - start_time < timeout:
            # Try to find element
            found = self._check_element_exists(app_name, role, title)
            if found["ok"]:
                return {"ok": True, "found": True, "wait_time": time.time() - start_time}

            # Exponential backoff to reduce CPU usage
            time.sleep(wait_interval)
            wait_interval = min(wait_interval * 1.2, max_interval)

        return {"ok": False, "error": f"Element not found within {timeout} seconds"}

    def _check_element_exists(self, app_name: str, role: str, title: str) -> Dict[str, Any]:
        """Single element check without looping"""
        jxa_script = f"""
        function run() {{
            const se = Application("System Events");
            const p = se.processes["{app_name}"];
            if (!p.exists()) return JSON.stringify({{ok: false}});

            function walk(el, depth = 0) {{
                if (depth > 8) return false;
                try {{
                    const elRole = String(el.role()).toLowerCase();
                    const elTitle = String(el.title ? el.title() : el.name()).toLowerCase();

                    if (elRole === "{role}".toLowerCase() &&
                        elTitle.includes("{title}".toLowerCase())) {{
                        return true;
                    }}

                    if (el.uiElements && el.uiElements.length > 0) {{
                        for (const c of el.uiElements()) {{
                            if (walk(c, depth + 1)) return true;
                        }}
                    }}
                }} catch(e) {{}}
                return false;
            }}

            for (const w of p.windows()) {{
                if (walk(w)) return JSON.stringify({{ok: true}});
            }}
            return JSON.stringify({{ok: false}});
        }}
        """

        try:
            result = subprocess.run(
                ["osascript", "-l", "JavaScript", "-e", jxa_script],
                capture_output=True, text=True, timeout=2
            )
            import json
            return json.loads(result.stdout.strip())
        except:
            return {"ok": False}

    # Public API methods - these enqueue tasks instead of executing directly

    def click_async(self, x: int, y: int) -> Future:
        """Async click - returns Future"""
        task = UITask("click", {"x": x, "y": y})
        return self.executor.submit(self._execute_ui_task, task)

    def click_sync(self, x: int, y: int, timeout: float = 5.0) -> Dict[str, Any]:
        """Sync click with timeout"""
        result_queue = Queue()
        task = UITask("click", {"x": x, "y": y}, result_queue=result_queue)
        self.ui_queue.put(task)

        try:
            return result_queue.get(timeout=timeout)
        except Empty:
            return {"ok": False, "error": "Click operation timed out"}

    def type_async(self, text: str) -> Future:
        """Async typing"""
        task = UITask("type", {"text": text})
        return self.executor.submit(self._execute_ui_task, task)

    def wait_for_element_efficient(self, app_name: str, role: str, title: str,
                                 timeout: int = 10) -> Dict[str, Any]:
        """Efficient element waiting with exponential backoff"""
        task = UITask("wait_element", {
            "app_name": app_name,
            "role": role,
            "title": title,
            "timeout": timeout
        })
        return self._execute_ui_task(task)

    def enqueue_applescript(self, script: str):
        """Queue AppleScript for batch execution"""
        self.applescript_queue.put(script)

    def calculator_optimized(self, expression: str) -> Dict[str, Any]:
        """Optimized Calculator automation - single AppleScript call"""
        script = f"""
        tell application "Calculator" to activate
        delay 0.3
        tell application "System Events"
            keystroke "c" using command down  -- Clear
            delay 0.1
            keystroke "{expression}"
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", script],
                         check=True, capture_output=True, timeout=5)
            return {"ok": True, "expression": expression}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def shutdown(self):
        """Clean shutdown of workers"""
        self.is_running = False
        self.executor.shutdown(wait=True)

# Drop-in replacements for existing controllers

class EfficientWaitMixin:
    """Mixin to add efficient waiting to existing controllers"""

    def wait_for_element_efficient(self, role: str, title_substring: str,
                                 timeout: int = 10) -> Dict[str, Any]:
        """Replace busy-loop waiting with exponential backoff"""
        start_time = time.time()
        wait_interval = 0.1  # Start with 100ms
        max_interval = 1.0   # Cap at 1 second

        while time.time() - start_time < timeout:
            result = self.click_ui(role, title_substring)
            if result.get("ok"):
                return {"ok": True, "found": True, "wait_time": time.time() - start_time}

            # Exponential backoff
            time.sleep(wait_interval)
            wait_interval = min(wait_interval * 1.2, max_interval)

        return {"ok": False, "error": f"Element not found within {timeout} seconds"}

class EfficientVisionMixin:
    """Mixin for efficient visual change detection"""

    def wait_for_visual_change_efficient(self, reference_image: str = None,
                                       timeout: int = 10,
                                       poll_interval: float = 0.5) -> Dict[str, Any]:
        """Efficient visual change waiting with smart polling"""
        if reference_image is None:
            ref_screenshot = self.screenshot_full()
            if not ref_screenshot["ok"]:
                return {"ok": False, "error": "Failed to capture reference screenshot"}
            reference_image = ref_screenshot["path"]

        start_time = time.time()
        interval = poll_interval
        max_interval = 2.0  # Cap polling at 2 seconds

        while time.time() - start_time < timeout:
            current_screenshot = self.screenshot_full()
            if not current_screenshot["ok"]:
                time.sleep(interval)
                continue

            # Simple file size comparison (fast proxy for content change)
            try:
                import os
                ref_size = os.path.getsize(reference_image)
                current_size = os.path.getsize(current_screenshot["path"])

                # If sizes differ by more than 2%, assume change
                if abs(ref_size - current_size) > ref_size * 0.02:
                    return {
                        "ok": True,
                        "changed": True,
                        "wait_time": time.time() - start_time,
                        "current_screenshot": current_screenshot["path"]
                    }
            except OSError:
                pass

            # Adaptive polling - increase interval if no changes
            time.sleep(interval)
            interval = min(interval * 1.1, max_interval)

        return {"ok": False, "error": f"No visual change detected within {timeout} seconds"}

# Singleton instance for global use
optimized_ui = OptimizedUIController()

def patch_existing_controllers():
    """Patch existing controllers with efficient methods"""
    # This would be imported and applied to existing controller classes
    from controllers.app_controller_macos import MacApp
    from controllers.vision_controller import VisionController

    # Add efficient methods as mixins
    MacApp.wait_for_element_efficient = EfficientWaitMixin.wait_for_element_efficient
    VisionController.wait_for_visual_change_efficient = EfficientVisionMixin.wait_for_visual_change_efficient