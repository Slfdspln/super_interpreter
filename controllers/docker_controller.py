#!/usr/bin/env python3

"""
Comprehensive Docker Controller
Combines native Docker Desktop automation with web interface control
Ensures Playwright can interact with all Docker UI elements without fail
"""

import time
import subprocess
from typing import Dict, Any, List, Optional, Union

try:
    from .app_controller_macos import docker as docker_app, launch_any_app
    from .browser_controller import BrowserController
except ImportError:
    # Handle direct execution
    from app_controller_macos import docker as docker_app, launch_any_app
    from browser_controller import BrowserController

class DockerController:
    """
    Comprehensive Docker automation controller
    Supports both native Docker Desktop UI and web interface automation
    """

    def __init__(self, prefer_web: bool = False, web_port: int = 9000):
        self.prefer_web = prefer_web
        self.web_port = web_port
        self.docker_app = None
        self.browser = None
        self._ensure_docker_running()

    def _ensure_docker_running(self):
        """Ensure Docker Desktop is running"""
        try:
            result = subprocess.run(['docker', 'info'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print("Starting Docker Desktop...")
                launch_any_app("Docker Desktop")
                time.sleep(5)  # Give Docker time to start
        except Exception:
            print("Docker not found, attempting to launch Docker Desktop...")
            launch_any_app("Docker Desktop")
            time.sleep(5)

    def _get_native_app(self):
        """Get native Docker Desktop app controller"""
        if not self.docker_app:
            self.docker_app = docker_app()
        return self.docker_app

    def _get_browser(self):
        """Get browser controller for web interface"""
        if not self.browser:
            self.browser = BrowserController(headed=True)
        return self.browser

    def _try_native_then_web(self, native_method: str, web_method: str, *args, **kwargs) -> Dict[str, Any]:
        """Try native method first, fallback to web interface"""
        if not self.prefer_web:
            # Try native first
            try:
                app = self._get_native_app()
                method = getattr(app, native_method)
                result = method(*args, **kwargs)
                if result.get("ok"):
                    return result
            except Exception as e:
                print(f"Native method {native_method} failed: {e}")

        # Try web interface
        try:
            browser = self._get_browser()
            method = getattr(browser, web_method)
            return method(*args, **kwargs)
        except Exception as e:
            print(f"Web method {web_method} failed: {e}")
            return {"ok": False, "error": f"Both native and web methods failed"}

    # ========== Container Management ==========

    def list_containers(self, all_containers: bool = True) -> Dict[str, Any]:
        """List all Docker containers"""
        try:
            cmd = ['docker', 'ps', '-a' if all_containers else '', '--format',
                  'table {{.Names}}\\t{{.Status}}\\t{{.Image}}\\t{{.Ports}}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                containers = []
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 3:
                            containers.append({
                                'name': parts[0].strip(),
                                'status': parts[1].strip(),
                                'image': parts[2].strip(),
                                'ports': parts[3].strip() if len(parts) > 3 else ''
                            })

                return {"ok": True, "containers": containers, "count": len(containers)}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def start_container(self, container_name: str) -> Dict[str, Any]:
        """Start a Docker container (native UI first, then CLI)"""
        # Try native UI first
        try:
            app = self._get_native_app()
            result = app.docker_start_container(container_name)
            if result.get("ok"):
                return result
        except Exception:
            pass

        # Fallback to CLI
        try:
            result = subprocess.run(['docker', 'start', container_name],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"ok": True, "container": container_name, "method": "cli"}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def stop_container(self, container_name: str) -> Dict[str, Any]:
        """Stop a Docker container (native UI first, then CLI)"""
        # Try native UI first
        try:
            app = self._get_native_app()
            result = app.docker_stop_container(container_name)
            if result.get("ok"):
                return result
        except Exception:
            pass

        # Fallback to CLI
        try:
            result = subprocess.run(['docker', 'stop', container_name],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"ok": True, "container": container_name, "method": "cli"}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a Docker container (native UI first, then CLI)"""
        # Try native UI first
        try:
            app = self._get_native_app()
            result = app.docker_restart_container(container_name)
            if result.get("ok"):
                return result
        except Exception:
            pass

        # Fallback to CLI
        try:
            result = subprocess.run(['docker', 'restart', container_name],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"ok": True, "container": container_name, "method": "cli"}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def remove_container(self, container_name: str, force: bool = False) -> Dict[str, Any]:
        """Remove a Docker container"""
        # Try native UI first
        try:
            app = self._get_native_app()
            result = app.docker_remove_container(container_name)
            if result.get("ok"):
                return result
        except Exception:
            pass

        # Fallback to CLI
        try:
            cmd = ['docker', 'rm']
            if force:
                cmd.append('-f')
            cmd.append(container_name)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"ok": True, "container": container_name, "method": "cli"}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def get_container_logs(self, container_name: str, lines: int = 100) -> Dict[str, Any]:
        """Get container logs (UI first, then CLI)"""
        # Try native UI first
        try:
            app = self._get_native_app()
            result = app.docker_get_container_logs(container_name)
            if result.get("ok"):
                return result
        except Exception:
            pass

        # Fallback to CLI
        try:
            result = subprocess.run(['docker', 'logs', '--tail', str(lines), container_name],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return {"ok": True, "logs": result.stdout, "container": container_name, "method": "cli"}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== Image Management ==========

    def list_images(self) -> Dict[str, Any]:
        """List Docker images"""
        try:
            result = subprocess.run(['docker', 'images', '--format',
                                  'table {{.Repository}}\\t{{.Tag}}\\t{{.ID}}\\t{{.Size}}'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                images = []
                for line in lines:
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 4:
                            images.append({
                                'repository': parts[0].strip(),
                                'tag': parts[1].strip(),
                                'id': parts[2].strip(),
                                'size': parts[3].strip()
                            })

                return {"ok": True, "images": images, "count": len(images)}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def pull_image(self, image_name: str) -> Dict[str, Any]:
        """Pull a Docker image (UI first, then CLI)"""
        # Try native UI first
        try:
            app = self._get_native_app()
            result = app.docker_pull_image(image_name)
            if result.get("ok"):
                return result
        except Exception:
            pass

        # Fallback to CLI
        try:
            result = subprocess.run(['docker', 'pull', image_name],
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                return {"ok": True, "image": image_name, "method": "cli"}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def remove_image(self, image_name: str, force: bool = False) -> Dict[str, Any]:
        """Remove a Docker image"""
        try:
            cmd = ['docker', 'rmi']
            if force:
                cmd.append('-f')
            cmd.append(image_name)

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return {"ok": True, "image": image_name}
            else:
                return {"ok": False, "error": result.stderr}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== Docker Desktop UI Navigation ==========

    def open_containers_tab(self) -> Dict[str, Any]:
        """Open Containers tab in Docker Desktop"""
        try:
            app = self._get_native_app()
            return app.docker_open_containers_tab()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_images_tab(self) -> Dict[str, Any]:
        """Open Images tab in Docker Desktop"""
        try:
            app = self._get_native_app()
            return app.docker_open_images_tab()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_volumes_tab(self) -> Dict[str, Any]:
        """Open Volumes tab in Docker Desktop"""
        try:
            app = self._get_native_app()
            return app.docker_open_volumes_tab()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def search_containers(self, search_term: str) -> Dict[str, Any]:
        """Search containers in Docker Desktop"""
        try:
            app = self._get_native_app()
            return app.docker_search_containers(search_term)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== Web Interface Methods ==========

    def open_web_interface(self, port: int = None) -> Dict[str, Any]:
        """Open Docker web interface"""
        port = port or self.web_port
        try:
            browser = self._get_browser()
            return browser.docker_web_interface(port)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def web_click_with_retry(self, selector: str, max_retries: int = 3) -> Dict[str, Any]:
        """Click element in web interface with retry"""
        try:
            browser = self._get_browser()
            return browser.docker_click_with_retry(selector, max_retries)
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def web_get_container_list(self) -> Dict[str, Any]:
        """Get container list from web interface"""
        try:
            browser = self._get_browser()
            return browser.docker_get_container_list()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # ========== Utility Methods ==========

    def get_docker_info(self) -> Dict[str, Any]:
        """Get comprehensive Docker system information"""
        try:
            # Get CLI info
            cli_info = subprocess.run(['docker', 'info', '--format', 'json'],
                                    capture_output=True, text=True, timeout=10)

            # Get version info
            version_info = subprocess.run(['docker', '--version'],
                                        capture_output=True, text=True, timeout=5)

            # Get container counts
            containers = self.list_containers(True)

            # Get image counts
            images = self.list_images()

            info = {
                "ok": True,
                "docker_version": version_info.stdout.strip() if version_info.returncode == 0 else "Unknown",
                "containers": containers.get("count", 0),
                "images": images.get("count", 0),
                "daemon_running": cli_info.returncode == 0
            }

            if cli_info.returncode == 0:
                import json
                try:
                    docker_info = json.loads(cli_info.stdout)
                    info["server_version"] = docker_info.get("ServerVersion", "Unknown")
                    info["architecture"] = docker_info.get("Architecture", "Unknown")
                    info["os"] = docker_info.get("OSType", "Unknown")
                except:
                    pass

            return info
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Comprehensive Docker system health check"""
        try:
            # Check Docker daemon
            daemon_check = subprocess.run(['docker', 'info'],
                                        capture_output=True, text=True, timeout=10)

            # Check Docker Desktop app
            try:
                app = self._get_native_app()
                app_info = app.get_window_info()
                app_running = app_info.get("ok", False)
            except:
                app_running = False

            # Check web interface (if applicable)
            web_accessible = False
            try:
                browser = self._get_browser()
                web_result = browser.docker_web_interface(self.web_port)
                web_accessible = web_result.get("ok", False)
            except:
                pass

            return {
                "ok": True,
                "daemon_healthy": daemon_check.returncode == 0,
                "desktop_app_running": app_running,
                "web_interface_accessible": web_accessible,
                "overall_status": "healthy" if daemon_check.returncode == 0 else "unhealthy"
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

# Convenience functions for quick access
def get_docker_controller(prefer_web: bool = False, web_port: int = 9000) -> DockerController:
    """Get a Docker controller instance"""
    return DockerController(prefer_web=prefer_web, web_port=web_port)

def quick_container_start(container_name: str) -> Dict[str, Any]:
    """Quick container start with automatic fallback"""
    controller = get_docker_controller()
    return controller.start_container(container_name)

def quick_container_stop(container_name: str) -> Dict[str, Any]:
    """Quick container stop with automatic fallback"""
    controller = get_docker_controller()
    return controller.stop_container(container_name)

def quick_container_list() -> Dict[str, Any]:
    """Quick container list"""
    controller = get_docker_controller()
    return controller.list_containers()