"""
Claude Code SDK Controller
Enhanced automation with Claude Code SDK features
"""

import json
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path

class ClaudeSDKController:
    """
    Enhanced automation controller using Claude Code SDK patterns
    Implements context management, tool permissions, and session handling
    """

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.claude_md_path = self.project_path / "CLAUDE.md"
        self.context_cache = {}
        self.session_id = None

    # Context Management
    def save_context(self, namespace: str, content: str, metadata: dict = None) -> bool:
        """Save context to CLAUDE.md file for persistent memory"""
        try:
            # Append to CLAUDE.md in structured format
            context_entry = f"""
## {namespace} - {metadata.get('timestamp', 'Unknown')}
{content}

---
"""
            if not self.claude_md_path.exists():
                self.claude_md_path.write_text("# Claude Code Context\n\n")

            with open(self.claude_md_path, 'a', encoding='utf-8') as f:
                f.write(context_entry)

            return True
        except Exception as e:
            print(f"Error saving context: {e}")
            return False

    def load_context(self, namespace: str = None) -> str:
        """Load context from CLAUDE.md"""
        try:
            if not self.claude_md_path.exists():
                return ""

            content = self.claude_md_path.read_text(encoding='utf-8')

            if namespace:
                # Extract specific namespace content
                lines = content.split('\n')
                namespace_content = []
                in_namespace = False

                for line in lines:
                    if line.startswith(f"## {namespace}"):
                        in_namespace = True
                        continue
                    elif line.startswith("## ") and in_namespace:
                        break
                    elif in_namespace:
                        namespace_content.append(line)

                return '\n'.join(namespace_content)

            return content
        except Exception as e:
            print(f"Error loading context: {e}")
            return ""

    # Tool Permission System
    def check_tool_permission(self, tool_name: str, action: str) -> bool:
        """Check if tool action is permitted"""
        # Read from policy.yaml or implement permission logic
        allowed_tools = {
            'browser': ['navigate', 'click', 'type', 'screenshot'],
            'filesystem': ['read', 'write', 'execute'],
            'app_control': ['activate', 'keystroke', 'menu_click'],
            'system': ['shell_command', 'process_management']
        }

        return action in allowed_tools.get(tool_name, [])

    def execute_with_permission(self, tool_name: str, action: str, params: dict) -> Dict[str, Any]:
        """Execute tool action with permission check"""
        if not self.check_tool_permission(tool_name, action):
            return {
                "ok": False,
                "error": f"Permission denied: {tool_name}.{action}",
                "requires_approval": True
            }

        # Log the action
        self.save_context(
            f"tool_execution",
            f"Tool: {tool_name}, Action: {action}, Params: {json.dumps(params)}",
            {"timestamp": "now", "type": "tool_execution"}
        )

        return {"ok": True, "message": f"Executed {tool_name}.{action}"}

    # Session Management
    def start_session(self, session_type: str = "automation") -> str:
        """Start a new automation session"""
        import time
        self.session_id = f"{session_type}_{int(time.time())}"

        self.save_context(
            "session_start",
            f"Started {session_type} session: {self.session_id}",
            {"timestamp": "now", "type": "session"}
        )

        return self.session_id

    def end_session(self) -> Dict[str, Any]:
        """End current session and save summary"""
        if not self.session_id:
            return {"ok": False, "error": "No active session"}

        summary = self.generate_session_summary()
        self.save_context(
            "session_end",
            f"Session {self.session_id} ended. Summary: {summary}",
            {"timestamp": "now", "type": "session"}
        )

        self.session_id = None
        return {"ok": True, "summary": summary}

    def generate_session_summary(self) -> str:
        """Generate summary of current session"""
        context = self.load_context()
        # Simple summary - count actions
        lines = context.split('\n')
        tool_executions = len([line for line in lines if 'tool_execution' in line])

        return f"Session completed with {tool_executions} tool executions"

    # Enhanced Automation Features
    def create_automation_workflow(self, name: str, steps: List[Dict]) -> bool:
        """Create a reusable automation workflow"""
        workflow = {
            "name": name,
            "steps": steps,
            "created": "now",
            "version": "1.0"
        }

        workflow_path = self.project_path / "workflows" / f"{name}.json"
        workflow_path.parent.mkdir(exist_ok=True)

        try:
            workflow_path.write_text(json.dumps(workflow, indent=2))
            self.save_context(
                "workflow_created",
                f"Created workflow: {name} with {len(steps)} steps",
                {"timestamp": "now", "type": "workflow"}
            )
            return True
        except Exception as e:
            print(f"Error creating workflow: {e}")
            return False

    def execute_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Execute a saved workflow"""
        workflow_path = self.project_path / "workflows" / f"{workflow_name}.json"

        if not workflow_path.exists():
            return {"ok": False, "error": f"Workflow {workflow_name} not found"}

        try:
            workflow = json.loads(workflow_path.read_text())
            results = []

            for step in workflow["steps"]:
                # Execute each step
                result = self.execute_automation_step(step)
                results.append(result)

                if not result.get("ok", False):
                    break

            return {
                "ok": True,
                "workflow": workflow_name,
                "steps_executed": len(results),
                "results": results
            }
        except Exception as e:
            return {"ok": False, "error": f"Error executing workflow: {e}"}

    def execute_automation_step(self, step: Dict) -> Dict[str, Any]:
        """Execute a single automation step"""
        step_type = step.get("type")
        params = step.get("params", {})

        if step_type == "open_website":
            return self.open_website(params.get("url"), params.get("browser", "chrome"))
        elif step_type == "open_app":
            return self.open_app(params.get("app_name"), params.get("path"))
        elif step_type == "wait":
            import time
            time.sleep(params.get("seconds", 1))
            return {"ok": True, "message": f"Waited {params.get('seconds', 1)} seconds"}
        else:
            return {"ok": False, "error": f"Unknown step type: {step_type}"}

    # Integrated Website/App Control
    def open_website(self, url: str, browser: str = "chrome") -> Dict[str, Any]:
        """Open website with permission checking"""
        if not self.check_tool_permission("browser", "navigate"):
            return {"ok": False, "error": "Browser navigation not permitted"}

        browsers = {
            'chrome': 'Google Chrome',
            'brave': 'Brave Browser',
            'safari': 'Safari'
        }

        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'

        browser_name = browsers.get(browser, browser)

        try:
            result = subprocess.run(['open', '-a', browser_name, url],
                                  capture_output=True, text=True)

            if result.returncode == 0:
                self.save_context(
                    "browser_action",
                    f"Opened {url} in {browser_name}",
                    {"timestamp": "now", "type": "browser"}
                )
                return {
                    "ok": True,
                    "message": f"Opened {url} in {browser_name}",
                    "url": url,
                    "browser": browser_name
                }
            else:
                return {"ok": False, "error": f"Failed to open browser: {result.stderr}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def open_app(self, app_name: str, path: str = None) -> Dict[str, Any]:
        """Open application with permission checking"""
        if not self.check_tool_permission("app_control", "activate"):
            return {"ok": False, "error": "App control not permitted"}

        try:
            cmd = ['open', '-a', app_name]
            if path:
                cmd.append(path)

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                msg = f"Launched {app_name}"
                if path:
                    msg += f" with {path}"

                self.save_context(
                    "app_action",
                    msg,
                    {"timestamp": "now", "type": "app_control"}
                )

                return {"ok": True, "message": msg, "app": app_name, "path": path}
            else:
                return {"ok": False, "error": f"Failed to launch {app_name}: {result.stderr}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    # Status and Information
    def get_status(self) -> Dict[str, Any]:
        """Get current controller status"""
        return {
            "session_id": self.session_id,
            "project_path": str(self.project_path),
            "context_file_exists": self.claude_md_path.exists(),
            "context_size": len(self.load_context()) if self.claude_md_path.exists() else 0,
            "active_permissions": ["browser", "app_control", "filesystem"],
            "workflows_available": len(list((self.project_path / "workflows").glob("*.json"))) if (self.project_path / "workflows").exists() else 0
        }

# Factory function for easy instantiation
def create_claude_sdk_controller(project_path: str = None) -> ClaudeSDKController:
    """Create a new Claude SDK Controller instance"""
    return ClaudeSDKController(project_path)