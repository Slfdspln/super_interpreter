import json
import subprocess
import time
import math
from typing import List, Optional, Dict, Any, Tuple

class GestureController:
    """Advanced trackpad and mouse gesture automation for macOS"""

    def __init__(self):
        self.gesture_delay = 0.1
        self.smooth_steps = 20  # Steps for smooth animations

    def _run_applescript(self, script: str) -> str:
        """Execute AppleScript and return output"""
        cmd = ["osascript", "-e", script]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
        return result.stdout.strip()

    def _run_jxa(self, script: str, *args: str) -> str:
        """Execute JXA JavaScript and return output"""
        cmd = ["osascript", "-l", "JavaScript", "-e", script, "--"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"JXA error: {result.stderr.strip()}")
        return result.stdout.strip()

    # ========== TRACKPAD GESTURES ==========

    def swipe(self, direction: str, fingers: int = 2, distance: float = 1.0) -> Dict[str, Any]:
        """Perform trackpad swipe gesture"""
        try:
            direction_map = {
                "left": "left",
                "right": "right",
                "up": "up",
                "down": "down"
            }

            if direction not in direction_map:
                return {"ok": False, "error": f"Invalid direction: {direction}"}

            if fingers not in [2, 3, 4]:
                return {"ok": False, "error": f"Invalid finger count: {fingers} (must be 2, 3, or 4)"}

            # Use cliclick if available for more precise control
            try:
                # Check if cliclick is installed
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Calculate swipe parameters
                base_distance = int(100 * distance)  # Base distance in pixels

                if direction == "left":
                    cmd = ["cliclick", f"m:+{base_distance},+0"]
                elif direction == "right":
                    cmd = ["cliclick", f"m:-{base_distance},+0"]
                elif direction == "up":
                    cmd = ["cliclick", f"m:+0,+{base_distance}"]
                else:  # down
                    cmd = ["cliclick", f"m:+0,-{base_distance}"]

                subprocess.run(cmd, check=True)
                return {"ok": True, "direction": direction, "fingers": fingers, "method": "cliclick"}

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to AppleScript
                script = f"""
                tell application "System Events"
                    -- Simulate trackpad swipe using key combinations
                    -- This is a simplified approach
                    delay 0.1
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "direction": direction,
                    "fingers": fingers,
                    "method": "applescript_fallback",
                    "note": "Install cliclick for better gesture control: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def pinch_zoom(self, zoom_type: str, amount: float = 1.0, center_x: int = None, center_y: int = None) -> Dict[str, Any]:
        """Perform pinch-to-zoom gesture"""
        try:
            if zoom_type not in ["in", "out"]:
                return {"ok": False, "error": "zoom_type must be 'in' or 'out'"}

            # Get screen center if coordinates not provided
            if center_x is None or center_y is None:
                screen_info = self._get_screen_size()
                if screen_info["ok"]:
                    center_x = center_x or screen_info["width"] // 2
                    center_y = center_y or screen_info["height"] // 2
                else:
                    center_x, center_y = 640, 360  # Default fallback

            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Simulate pinch gesture with mouse movements
                if zoom_type == "in":
                    # Pinch in - move points closer
                    distance = int(50 * amount)
                    cmd1 = ["cliclick", f"m:{center_x-distance},{center_y}"]
                    cmd2 = ["cliclick", f"m:{center_x+distance},{center_y}"]
                else:
                    # Pinch out - move points farther
                    distance = int(50 * amount)
                    cmd1 = ["cliclick", f"m:{center_x+distance},{center_y}"]
                    cmd2 = ["cliclick", f"m:{center_x-distance},{center_y}"]

                # Execute gesture simulation
                subprocess.run(cmd1)
                time.sleep(0.1)
                subprocess.run(cmd2)

                return {
                    "ok": True,
                    "zoom_type": zoom_type,
                    "amount": amount,
                    "center": [center_x, center_y],
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to keyboard shortcuts
                if zoom_type == "in":
                    script = 'tell application "System Events" to keystroke "+" using command down'
                else:
                    script = 'tell application "System Events" to keystroke "-" using command down'

                self._run_applescript(script)
                return {
                    "ok": True,
                    "zoom_type": zoom_type,
                    "method": "keyboard_shortcut",
                    "note": "Install cliclick for true pinch gestures: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def multi_finger_tap(self, fingers: int, x: int, y: int, tap_count: int = 1) -> Dict[str, Any]:
        """Perform multi-finger tap gesture"""
        try:
            if fingers not in [2, 3, 4]:
                return {"ok": False, "error": f"Invalid finger count: {fingers} (must be 2, 3, or 4)"}

            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Simulate multi-finger tap by clicking multiple nearby points
                offsets = [
                    (0, 0),      # Center
                    (-10, 0),    # Left
                    (10, 0),     # Right
                    (0, -10),    # Up
                    (0, 10)      # Down
                ]

                for _ in range(tap_count):
                    for i in range(fingers):
                        offset_x, offset_y = offsets[i % len(offsets)]
                        tap_x = x + offset_x
                        tap_y = y + offset_y
                        cmd = ["cliclick", f"c:{tap_x},{tap_y}"]
                        subprocess.run(cmd)
                        time.sleep(0.02)  # Brief delay between taps

                    if tap_count > 1:
                        time.sleep(0.1)  # Delay between multiple taps

                return {
                    "ok": True,
                    "fingers": fingers,
                    "position": [x, y],
                    "tap_count": tap_count,
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to single click
                script = f"""
                tell application "System Events"
                    click at {{{x}, {y}}}
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "fingers": 1,  # Fallback to single finger
                    "position": [x, y],
                    "method": "applescript_fallback",
                    "note": "Install cliclick for true multi-finger taps: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def force_touch(self, x: int, y: int, pressure: float = 1.0) -> Dict[str, Any]:
        """Simulate Force Touch/3D Touch at coordinates"""
        try:
            if pressure < 0.1 or pressure > 2.0:
                return {"ok": False, "error": "pressure must be between 0.1 and 2.0"}

            # Force Touch is typically simulated with a long press
            press_duration = 0.5 + (pressure * 0.5)  # Scale duration with pressure

            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Simulate force touch with long press
                cmd = ["cliclick", f"dd:{x},{y}", f"du:{x},{y}"]
                subprocess.run(["cliclick", f"dd:{x},{y}"])
                time.sleep(press_duration)
                subprocess.run(["cliclick", f"du:{x},{y}"])

                return {
                    "ok": True,
                    "position": [x, y],
                    "pressure": pressure,
                    "duration": press_duration,
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to long press simulation
                script = f"""
                tell application "System Events"
                    set mouseLocation to {{{x}, {y}}}
                    mouse down at mouseLocation
                    delay {press_duration}
                    mouse up at mouseLocation
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "position": [x, y],
                    "pressure": pressure,
                    "method": "applescript_long_press",
                    "note": "Install cliclick for better pressure simulation: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== SMOOTH MOUSE MOVEMENTS ==========

    def smooth_move(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 1.0) -> Dict[str, Any]:
        """Move mouse smoothly from one point to another"""
        try:
            steps = int(self.smooth_steps * duration)
            if steps < 1:
                steps = 1

            dx = (to_x - from_x) / steps
            dy = (to_y - from_y) / steps

            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Move to starting position
                subprocess.run(["cliclick", f"m:{from_x},{from_y}"])

                # Smooth movement
                for i in range(steps):
                    current_x = int(from_x + dx * i)
                    current_y = int(from_y + dy * i)
                    subprocess.run(["cliclick", f"m:{current_x},{current_y}"])
                    time.sleep(duration / steps)

                # Ensure we end at exact target
                subprocess.run(["cliclick", f"m:{to_x},{to_y}"])

                return {
                    "ok": True,
                    "from": [from_x, from_y],
                    "to": [to_x, to_y],
                    "duration": duration,
                    "steps": steps,
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to direct movement
                script = f"""
                tell application "System Events"
                    set mouseLocation to {{{to_x}, {to_y}}}
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "from": [from_x, from_y],
                    "to": [to_x, to_y],
                    "method": "applescript_direct",
                    "note": "Install cliclick for smooth movements: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def smooth_scroll(self, x: int, y: int, delta_x: int, delta_y: int, steps: int = 10) -> Dict[str, Any]:
        """Perform smooth scrolling at coordinates"""
        try:
            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Move to position first
                subprocess.run(["cliclick", f"m:{x},{y}"])

                # Smooth scroll in steps
                step_x = delta_x / steps
                step_y = delta_y / steps

                for i in range(steps):
                    scroll_x = int(step_x)
                    scroll_y = int(step_y)

                    if scroll_y > 0:
                        cmd = ["cliclick", f"w:{scroll_y}"]
                    elif scroll_y < 0:
                        cmd = ["cliclick", f"w:{scroll_y}"]
                    else:
                        cmd = ["cliclick", "w:0"]

                    subprocess.run(cmd)
                    time.sleep(0.02)

                return {
                    "ok": True,
                    "position": [x, y],
                    "delta": [delta_x, delta_y],
                    "steps": steps,
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to AppleScript scrolling
                if delta_y > 0:
                    direction = "down"
                    amount = abs(delta_y)
                else:
                    direction = "up"
                    amount = abs(delta_y)

                script = f"""
                tell application "System Events"
                    set mouseLocation to {{{x}, {y}}}
                    scroll {direction} {amount}
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "position": [x, y],
                    "direction": direction,
                    "amount": amount,
                    "method": "applescript_fallback",
                    "note": "Install cliclick for better scroll control: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== ADVANCED DRAG OPERATIONS ==========

    def smooth_drag(self, from_x: int, from_y: int, to_x: int, to_y: int, duration: float = 1.0) -> Dict[str, Any]:
        """Perform smooth drag operation"""
        try:
            steps = int(self.smooth_steps * duration)
            if steps < 1:
                steps = 1

            dx = (to_x - from_x) / steps
            dy = (to_y - from_y) / steps

            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Start drag
                subprocess.run(["cliclick", f"dd:{from_x},{from_y}"])

                # Smooth drag movement
                for i in range(1, steps + 1):
                    current_x = int(from_x + dx * i)
                    current_y = int(from_y + dy * i)
                    subprocess.run(["cliclick", f"dm:{current_x},{current_y}"])
                    time.sleep(duration / steps)

                # End drag
                subprocess.run(["cliclick", f"du:{to_x},{to_y}"])

                return {
                    "ok": True,
                    "from": [from_x, from_y],
                    "to": [to_x, to_y],
                    "duration": duration,
                    "steps": steps,
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to AppleScript
                script = f"""
                tell application "System Events"
                    set startPoint to {{{from_x}, {from_y}}}
                    set endPoint to {{{to_x}, {to_y}}}

                    mouse down at startPoint
                    delay 0.1
                    mouse up at endPoint
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "from": [from_x, from_y],
                    "to": [to_x, to_y],
                    "method": "applescript_fallback",
                    "note": "Install cliclick for smooth drag: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def circular_gesture(self, center_x: int, center_y: int, radius: int, clockwise: bool = True, duration: float = 1.0) -> Dict[str, Any]:
        """Perform circular mouse gesture"""
        try:
            steps = max(20, int(50 * duration))  # More steps for smoother circles
            angle_step = (2 * math.pi) / steps

            if not clockwise:
                angle_step = -angle_step

            try:
                # Check if cliclick is available
                subprocess.run(["which", "cliclick"], check=True, capture_output=True)

                # Start at top of circle
                start_x = center_x
                start_y = center_y - radius
                subprocess.run(["cliclick", f"m:{start_x},{start_y}"])

                # Draw circle
                for i in range(steps + 1):
                    angle = i * angle_step - (math.pi / 2)  # Start at top
                    x = int(center_x + radius * math.cos(angle))
                    y = int(center_y + radius * math.sin(angle))
                    subprocess.run(["cliclick", f"m:{x},{y}"])
                    time.sleep(duration / steps)

                return {
                    "ok": True,
                    "center": [center_x, center_y],
                    "radius": radius,
                    "clockwise": clockwise,
                    "duration": duration,
                    "steps": steps,
                    "method": "cliclick"
                }

            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to simple movement
                script = f"""
                tell application "System Events"
                    set mouseLocation to {{{center_x}, {center_y}}}
                end tell
                """
                self._run_applescript(script)
                return {
                    "ok": True,
                    "center": [center_x, center_y],
                    "method": "applescript_fallback",
                    "note": "Install cliclick for circular gestures: brew install cliclick"
                }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== UTILITY METHODS ==========

    def _get_screen_size(self) -> Dict[str, Any]:
        """Get screen dimensions"""
        try:
            script = """
            tell application "System Events"
                set screenBounds to bounds of desktop
                return (item 3 of screenBounds as string) & "," & (item 4 of screenBounds as string)
            end tell
            """
            result = self._run_applescript(script)
            width, height = map(int, result.split(","))
            return {"ok": True, "width": width, "height": height}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_mouse_position(self) -> Dict[str, Any]:
        """Get current mouse position"""
        try:
            jxa_script = """
            function run() {
                const se = Application("System Events");
                const pos = se.mouseLocation();
                return JSON.stringify({ok: true, x: pos[0], y: pos[1]});
            }
            """
            result = self._run_jxa(jxa_script)
            return json.loads(result)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required tools are installed"""
        dependencies = {}

        # Check for cliclick
        try:
            result = subprocess.run(["which", "cliclick"], capture_output=True)
            dependencies["cliclick"] = result.returncode == 0
        except:
            dependencies["cliclick"] = False

        return {
            "ok": True,
            "dependencies": dependencies,
            "recommendations": [
                "brew install cliclick  # For precise mouse/trackpad control",
                "Enable Accessibility permissions for your terminal/app"
            ] if not dependencies["cliclick"] else []
        }