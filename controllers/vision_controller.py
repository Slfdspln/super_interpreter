import json
import subprocess
import time
import tempfile
import os
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

class VisionController:
    """Computer vision automation for macOS using screenshots and OCR"""

    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.screenshot_count = 0

    def _get_temp_screenshot_path(self) -> str:
        """Generate unique screenshot filename"""
        self.screenshot_count += 1
        return os.path.join(self.temp_dir, f"vision_screenshot_{self.screenshot_count}.png")

    def _run_applescript(self, script: str) -> str:
        """Execute AppleScript and return output"""
        cmd = ["osascript", "-e", script]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"AppleScript error: {result.stderr.strip()}")
        return result.stdout.strip()

    # ========== SCREENSHOT UTILITIES ==========

    def screenshot_full(self, path: str = None) -> Dict[str, Any]:
        """Take full screen screenshot"""
        try:
            if path is None:
                path = self._get_temp_screenshot_path()

            cmd = ["screencapture", "-x", path]
            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                return {"ok": True, "path": path, "type": "full_screen"}
            else:
                return {"ok": False, "error": "Screenshot failed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def screenshot_region(self, x: int, y: int, width: int, height: int, path: str = None) -> Dict[str, Any]:
        """Take screenshot of specific region"""
        try:
            if path is None:
                path = self._get_temp_screenshot_path()

            # screencapture -R uses format: x,y,width,height
            cmd = ["screencapture", "-x", "-R", f"{x},{y},{width},{height}", path]
            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                return {"ok": True, "path": path, "type": "region", "region": [x, y, width, height]}
            else:
                return {"ok": False, "error": "Region screenshot failed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def screenshot_window(self, window_id: int = None, path: str = None) -> Dict[str, Any]:
        """Take screenshot of specific window"""
        try:
            if path is None:
                path = self._get_temp_screenshot_path()

            if window_id:
                cmd = ["screencapture", "-x", "-l", str(window_id), path]
            else:
                # Interactive window selection
                cmd = ["screencapture", "-x", "-w", path]

            result = subprocess.run(cmd, capture_output=True)

            if result.returncode == 0:
                return {"ok": True, "path": path, "type": "window", "window_id": window_id}
            else:
                return {"ok": False, "error": "Window screenshot failed"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== IMAGE TEMPLATE MATCHING ==========

    def find_image_on_screen(self, template_path: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Find template image on current screen using OpenCV-style matching"""
        try:
            # This would require OpenCV or similar library
            # For now, we'll provide a framework that can be extended

            screenshot = self.screenshot_full()
            if not screenshot["ok"]:
                return {"ok": False, "error": "Failed to capture screenshot"}

            # Note: This is a placeholder - would need cv2 for actual implementation
            # return self._opencv_template_match(screenshot["path"], template_path, confidence)

            return {
                "ok": False,
                "error": "Template matching requires OpenCV installation",
                "todo": "pip install opencv-python to enable this feature"
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def click_image(self, template_path: str, confidence: float = 0.8) -> Dict[str, Any]:
        """Find and click on template image"""
        try:
            match_result = self.find_image_on_screen(template_path, confidence)
            if not match_result["ok"]:
                return match_result

            # Extract center coordinates from match
            x, y = match_result.get("center", [0, 0])

            # Click at the center of found image
            script = f"""
            tell application "System Events"
                click at {{{x}, {y}}}
            end tell
            """
            self._run_applescript(script)

            return {"ok": True, "clicked_at": [x, y], "template": template_path}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== OCR TEXT RECOGNITION ==========

    def read_text_ocr(self, image_path: str = None, region: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
        """Extract text from screenshot using macOS built-in OCR"""
        try:
            if image_path is None:
                if region:
                    x, y, w, h = region
                    screenshot = self.screenshot_region(x, y, w, h)
                else:
                    screenshot = self.screenshot_full()

                if not screenshot["ok"]:
                    return {"ok": False, "error": "Failed to capture screenshot"}
                image_path = screenshot["path"]

            # Use macOS Shortcuts for OCR (requires Monterey+)
            # Alternative approach using Vision framework via Python
            try:
                # First try with shortcuts if available
                cmd = ["shortcuts", "run", "Extract Text from Image", "-i", image_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0 and result.stdout.strip():
                    return {"ok": True, "text": result.stdout.strip(), "method": "shortcuts"}
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            # Fallback: Try using tesseract if installed
            try:
                cmd = ["tesseract", image_path, "stdout"]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

                if result.returncode == 0:
                    return {"ok": True, "text": result.stdout.strip(), "method": "tesseract"}
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

            return {
                "ok": False,
                "error": "No OCR method available",
                "suggestions": [
                    "Install tesseract: brew install tesseract",
                    "Create OCR shortcut in Shortcuts app",
                    "Enable macOS Monterey+ for Vision framework support"
                ]
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def find_text_and_click(self, text: str, region: Tuple[int, int, int, int] = None) -> Dict[str, Any]:
        """Find text on screen using OCR and click on it"""
        try:
            # First, extract text from screen
            ocr_result = self.read_text_ocr(region=region)
            if not ocr_result["ok"]:
                return ocr_result

            extracted_text = ocr_result["text"].lower()
            search_text = text.lower()

            if search_text not in extracted_text:
                return {"ok": False, "error": f"Text '{text}' not found on screen"}

            # For a more sophisticated implementation, we'd need to:
            # 1. Parse OCR results with bounding boxes
            # 2. Find exact coordinates of the text
            # 3. Click at those coordinates

            # Simple fallback: estimate position (center of region or screen)
            if region:
                x, y, w, h = region
                click_x = x + w // 2
                click_y = y + h // 2
            else:
                # Get screen size and click in center as fallback
                screen_info = self._get_screen_size()
                if screen_info["ok"]:
                    click_x = screen_info["width"] // 2
                    click_y = screen_info["height"] // 2
                else:
                    click_x, click_y = 640, 360  # Default fallback

            # Click at estimated position
            script = f"""
            tell application "System Events"
                click at {{{click_x}, {click_y}}}
            end tell
            """
            self._run_applescript(script)

            return {
                "ok": True,
                "text_found": text,
                "clicked_at": [click_x, click_y],
                "note": "Clicked at estimated position - for precise clicking, use coordinate-based methods"
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== COLOR AND PIXEL UTILITIES ==========

    def get_pixel_color(self, x: int, y: int) -> Dict[str, Any]:
        """Get RGB color of pixel at coordinates"""
        try:
            # Take 1x1 screenshot at the specific pixel
            screenshot = self.screenshot_region(x, y, 1, 1)
            if not screenshot["ok"]:
                return {"ok": False, "error": "Failed to capture pixel"}

            # This would require image processing to extract RGB values
            # For now, return a placeholder that can be extended
            return {
                "ok": False,
                "error": "Pixel color reading requires image processing library",
                "todo": "Implement with PIL or opencv-python",
                "coordinates": [x, y]
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def find_color_on_screen(self, target_rgb: Tuple[int, int, int], tolerance: int = 10) -> Dict[str, Any]:
        """Find pixels matching specific RGB color"""
        try:
            screenshot = self.screenshot_full()
            if not screenshot["ok"]:
                return {"ok": False, "error": "Failed to capture screenshot"}

            # This would require image processing to scan for colors
            return {
                "ok": False,
                "error": "Color searching requires image processing library",
                "todo": "Implement with PIL or opencv-python",
                "target_color": target_rgb
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== VISUAL CHANGE DETECTION ==========

    def visual_diff(self, before_image: str, after_image: str = None) -> Dict[str, Any]:
        """Compare two screenshots to detect changes"""
        try:
            if after_image is None:
                # Take current screenshot for comparison
                current_screenshot = self.screenshot_full()
                if not current_screenshot["ok"]:
                    return {"ok": False, "error": "Failed to capture current screenshot"}
                after_image = current_screenshot["path"]

            # This would require image processing for diff analysis
            return {
                "ok": False,
                "error": "Visual diff requires image processing library",
                "todo": "Implement with PIL or opencv-python",
                "images": {"before": before_image, "after": after_image}
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def wait_for_visual_change(self, reference_image: str = None, timeout: int = 10, poll_interval: float = 0.5) -> Dict[str, Any]:
        """Wait for screen to change from reference image with adaptive polling (CPU-efficient)"""
        try:
            if reference_image is None:
                # Take reference screenshot
                ref_screenshot = self.screenshot_full()
                if not ref_screenshot["ok"]:
                    return {"ok": False, "error": "Failed to capture reference screenshot"}
                reference_image = ref_screenshot["path"]

            start_time = time.time()
            interval = poll_interval
            max_interval = 2.0  # Cap polling at 2 seconds

            while time.time() - start_time < timeout:
                # Take current screenshot
                current_screenshot = self.screenshot_full()
                if not current_screenshot["ok"]:
                    time.sleep(interval)
                    continue

                # Compare with reference (simplified check using file size as proxy)
                try:
                    ref_size = os.path.getsize(reference_image)
                    current_size = os.path.getsize(current_screenshot["path"])

                    # If file sizes differ significantly, assume visual change
                    if abs(ref_size - current_size) > ref_size * 0.02:  # 2% difference threshold
                        return {
                            "ok": True,
                            "changed": True,
                            "wait_time": time.time() - start_time,
                            "current_screenshot": current_screenshot["path"]
                        }
                except OSError:
                    pass

                # Adaptive polling - increase interval if no changes detected
                time.sleep(interval)
                interval = min(interval * 1.1, max_interval)

            return {"ok": False, "error": f"No visual change detected within {timeout} seconds"}

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

    def cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary screenshot files"""
        try:
            import glob
            pattern = os.path.join(self.temp_dir, "vision_screenshot_*.png")
            files = glob.glob(pattern)

            removed_count = 0
            for file_path in files:
                try:
                    os.remove(file_path)
                    removed_count += 1
                except OSError:
                    pass

            return {"ok": True, "removed_files": removed_count}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def save_annotated_screenshot(self, annotations: List[Dict[str, Any]], path: str = None) -> Dict[str, Any]:
        """Take screenshot and save with annotations (for debugging)"""
        try:
            screenshot = self.screenshot_full(path)
            if not screenshot["ok"]:
                return screenshot

            # This would require image processing to add annotations
            # For now, just return the plain screenshot
            return {
                "ok": True,
                "path": screenshot["path"],
                "annotations": annotations,
                "note": "Annotation overlay requires image processing library"
            }

        except Exception as e:
            return {"ok": False, "error": str(e)}