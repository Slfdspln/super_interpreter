"""
CPU-efficient Calculator automation that batches operations and prevents busy-loops.
Replaces multiple AppleScript calls with single optimized commands.
"""

import subprocess
import time
import threading
from queue import Queue, Empty
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class CalculatorCommand:
    """Single Calculator command"""
    action: str  # "type", "click", "clear", "read"
    payload: Any
    result_queue: Queue = None

class OptimizedCalculatorController:
    """CPU-efficient Calculator controller with command batching"""

    def __init__(self):
        self.command_queue = Queue(maxsize=32)
        self.is_running = True
        self.worker = threading.Thread(target=self._calculator_worker, daemon=True)
        self.worker.start()

    def _calculator_worker(self):
        """Worker thread for Calculator operations - prevents subprocess thrash"""
        calculator_active = False

        while self.is_running:
            try:
                command = self.command_queue.get(timeout=1.0)  # Block, don't spin

                # Ensure Calculator is active
                if not calculator_active:
                    self._activate_calculator()
                    calculator_active = True

                result = self._execute_command(command)

                if command.result_queue:
                    command.result_queue.put(result)

                self.command_queue.task_done()

                # Small delay to prevent rapid-fire operations
                time.sleep(0.05)  # 50ms throttle

            except Empty:
                calculator_active = False  # Reset if idle
                continue
            except Exception as e:
                print(f"Calculator worker error: {e}")

    def _activate_calculator(self):
        """Activate Calculator once per batch"""
        script = """
        tell application "Calculator" to activate
        delay 0.3
        """
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)

    def _execute_command(self, command: CalculatorCommand) -> Dict[str, Any]:
        """Execute single Calculator command"""
        try:
            if command.action == "type_expression":
                return self._type_expression_direct(command.payload)
            elif command.action == "click_buttons":
                return self._click_buttons_batch(command.payload)
            elif command.action == "clear":
                return self._clear_calculator()
            elif command.action == "read_display":
                return self._read_display()
            else:
                return {"ok": False, "error": f"Unknown command: {command.action}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _type_expression_direct(self, expression: str) -> Dict[str, Any]:
        """Type entire expression in one AppleScript call"""
        # Escape quotes and special characters
        escaped_expr = expression.replace('"', '\\"').replace('\\', '\\\\')

        script = f"""
        tell application "System Events"
            keystroke "c" using command down
            delay 0.1
            keystroke "{escaped_expr}"
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", script],
                         check=True, capture_output=True, timeout=5)
            return {"ok": True, "expression": expression}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Failed to type expression: {e}"}

    def _click_buttons_batch(self, buttons: List[str]) -> Dict[str, Any]:
        """Click multiple buttons in single AppleScript call"""
        # Build button click sequence
        click_commands = []
        for button in buttons:
            if button in ["=", "+", "-", "*", "/", "×", "÷"]:
                # Operators need special handling
                if button == "*":
                    button = "×"
                elif button == "/":
                    button = "÷"

            click_commands.append(f'click button "{button}" of window 1')

        script = f"""
        tell application "System Events" to tell process "Calculator"
            {chr(10).join(click_commands)}
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", script],
                         check=True, capture_output=True, timeout=5)
            return {"ok": True, "buttons": buttons}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Failed to click buttons: {e}"}

    def _clear_calculator(self) -> Dict[str, Any]:
        """Clear Calculator display"""
        script = """
        tell application "System Events"
            keystroke "c" using command down
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", script],
                         check=True, capture_output=True, timeout=3)
            return {"ok": True, "action": "cleared"}
        except subprocess.CalledProcessError as e:
            return {"ok": False, "error": f"Failed to clear: {e}"}

    def _read_display(self) -> Dict[str, Any]:
        """Read Calculator display value efficiently"""
        jxa_script = """
        function run() {
            const se = Application("System Events");
            const calc = se.processes["Calculator"];
            if (!calc.exists()) {
                return JSON.stringify({ok: false, error: "Calculator not running"});
            }

            try {
                const window = calc.windows[0];

                function findDisplay(el, depth = 0) {
                    if (depth > 4) return null;
                    try {
                        const role = String(el.role()).toLowerCase();
                        if (role === "text field" || role === "static text") {
                            const value = el.value ? String(el.value()) : String(el.title());
                            // Check if it looks like a number
                            if (value && /[0-9]/.test(value)) {
                                return value;
                            }
                        }

                        if (el.uiElements && el.uiElements.length > 0) {
                            for (const child of el.uiElements()) {
                                const result = findDisplay(child, depth + 1);
                                if (result) return result;
                            }
                        }
                    } catch(e) {}
                    return null;
                }

                const display = findDisplay(window);
                if (display) {
                    return JSON.stringify({ok: true, value: display});
                } else {
                    return JSON.stringify({ok: false, error: "Display value not found"});
                }
            } catch(e) {
                return JSON.stringify({ok: false, error: "Error reading display: " + e.message});
            }
        }
        """

        try:
            result = subprocess.run(
                ["osascript", "-l", "JavaScript", "-e", jxa_script],
                capture_output=True, text=True, timeout=3
            )
            import json
            return json.loads(result.stdout.strip())
        except Exception as e:
            return {"ok": False, "error": f"Failed to read display: {e}"}

    # Public API methods

    def calculate(self, expression: str, timeout: float = 10.0) -> Dict[str, Any]:
        """Complete calculation in one optimized operation"""
        result_queue = Queue()
        command = CalculatorCommand("type_expression", expression, result_queue)
        self.command_queue.put(command)

        try:
            result = result_queue.get(timeout=timeout)
            if result["ok"]:
                # Read the result
                read_command = CalculatorCommand("read_display", None, result_queue)
                self.command_queue.put(read_command)
                display_result = result_queue.get(timeout=timeout)

                if display_result["ok"]:
                    return {
                        "ok": True,
                        "expression": expression,
                        "result": display_result["value"]
                    }
                else:
                    return display_result
            else:
                return result
        except Empty:
            return {"ok": False, "error": "Calculator operation timed out"}

    def click_buttons_sequence(self, buttons: List[str], timeout: float = 10.0) -> Dict[str, Any]:
        """Click button sequence efficiently"""
        result_queue = Queue()
        command = CalculatorCommand("click_buttons", buttons, result_queue)
        self.command_queue.put(command)

        try:
            return result_queue.get(timeout=timeout)
        except Empty:
            return {"ok": False, "error": "Button sequence timed out"}

    def clear(self, timeout: float = 5.0) -> Dict[str, Any]:
        """Clear Calculator"""
        result_queue = Queue()
        command = CalculatorCommand("clear", None, result_queue)
        self.command_queue.put(command)

        try:
            return result_queue.get(timeout=timeout)
        except Empty:
            return {"ok": False, "error": "Clear operation timed out"}

    def get_display(self, timeout: float = 5.0) -> Dict[str, Any]:
        """Read display value"""
        result_queue = Queue()
        command = CalculatorCommand("read_display", None, result_queue)
        self.command_queue.put(command)

        try:
            return result_queue.get(timeout=timeout)
        except Empty:
            return {"ok": False, "error": "Display read timed out"}

    def shutdown(self):
        """Clean shutdown"""
        self.is_running = False

# Convenience functions for quick calculations

def quick_calculate(expression: str) -> str:
    """Quick calculation with automatic result extraction"""
    calc = OptimizedCalculatorController()
    try:
        result = calc.calculate(expression)
        if result["ok"]:
            return result["result"]
        else:
            return f"Error: {result['error']}"
    finally:
        calc.shutdown()

def quick_button_sequence(buttons: List[str]) -> Dict[str, Any]:
    """Quick button sequence"""
    calc = OptimizedCalculatorController()
    try:
        return calc.click_buttons_sequence(buttons)
    finally:
        calc.shutdown()

# Singleton for global use
optimized_calculator = OptimizedCalculatorController()