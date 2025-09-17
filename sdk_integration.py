#!/usr/bin/env python3
"""
Claude Code SDK Integration for Super Interpreter
Enhanced automation with SDK features
"""

import json
from controllers.claude_sdk_controller import ClaudeSDKController
from controllers.browser_controller import BrowserController
from controllers.app_controller_macos import MacApp
from pathlib import Path

class SuperInterpreterSDK:
    """
    Enhanced Super Interpreter with Claude Code SDK integration
    """

    def __init__(self, project_path: str = None):
        self.sdk = ClaudeSDKController(project_path)
        self.browser = BrowserController("policy.yaml", headed=True)
        self.project_path = Path(project_path) if project_path else Path.cwd()

        # Start a session
        self.session_id = self.sdk.start_session("super_interpreter")
        print(f"🚀 Super Interpreter SDK started - Session: {self.session_id}")

    def create_workflow_from_commands(self, name: str, commands: list) -> bool:
        """Create a workflow from a list of natural language commands"""
        steps = []

        for command in commands:
            # Parse commands into structured steps
            if "open website" in command.lower() or "navigate to" in command.lower():
                # Extract URL and browser
                parts = command.split()
                url = None
                browser = "chrome"

                for part in parts:
                    if "http" in part or ".com" in part or ".org" in part:
                        url = part
                    elif part.lower() in ["chrome", "brave", "safari"]:
                        browser = part.lower()

                if url:
                    steps.append({
                        "type": "open_website",
                        "params": {"url": url, "browser": browser},
                        "description": command
                    })

            elif "open app" in command.lower() or "launch" in command.lower():
                # Extract app name
                parts = command.split()
                app_name = None

                for i, part in enumerate(parts):
                    if part.lower() in ["app", "application", "launch", "open"]:
                        if i + 1 < len(parts):
                            app_name = parts[i + 1]
                            break

                if app_name:
                    steps.append({
                        "type": "open_app",
                        "params": {"app_name": app_name},
                        "description": command
                    })

            elif "wait" in command.lower():
                # Extract wait time
                import re
                match = re.search(r'(\d+)', command)
                seconds = int(match.group(1)) if match else 1

                steps.append({
                    "type": "wait",
                    "params": {"seconds": seconds},
                    "description": command
                })

        return self.sdk.create_automation_workflow(name, steps)

    def quick_automation(self, commands: list) -> dict:
        """Execute a quick automation sequence"""
        results = []

        for command in commands:
            print(f"Executing: {command}")

            if "website" in command.lower():
                # Extract URL
                parts = command.split()
                for part in parts:
                    if "http" in part or ".com" in part:
                        result = self.sdk.open_website(part)
                        results.append({"command": command, "result": result})
                        break

            elif "app" in command.lower():
                # Extract app name
                parts = command.split()
                for i, part in enumerate(parts):
                    if part.lower() in ["app", "open", "launch"]:
                        if i + 1 < len(parts):
                            app_name = parts[i + 1]
                            result = self.sdk.open_app(app_name)
                            results.append({"command": command, "result": result})
                            break

        return {"executed_commands": len(results), "results": results}

    def save_automation_session(self, description: str = None) -> dict:
        """Save current automation session"""
        status = self.sdk.get_status()
        session_data = {
            "session_id": self.session_id,
            "description": description or "Automation session",
            "status": status,
            "timestamp": "now"
        }

        # Save to project
        session_file = self.project_path / "sessions" / f"{self.session_id}.json"
        session_file.parent.mkdir(exist_ok=True)

        try:
            session_file.write_text(json.dumps(session_data, indent=2))
            return {"ok": True, "session_file": str(session_file)}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def list_available_apps(self) -> list:
        """List available applications"""
        try:
            import subprocess
            apps = []

            # Check /Applications
            result = subprocess.run(['ls', '/Applications'],
                                  capture_output=True, text=True)

            for line in result.stdout.strip().split('\n'):
                if line.endswith('.app'):
                    apps.append(line[:-4])  # Remove .app extension

            return sorted(apps)
        except Exception as e:
            print(f"Error listing apps: {e}")
            return []

    def generate_automation_report(self) -> str:
        """Generate a report of automation activities"""
        context = self.sdk.load_context()
        status = self.sdk.get_status()

        report = f"""
# Super Interpreter Automation Report

## Session Information
- Session ID: {self.session_id}
- Project Path: {status['project_path']}
- Context Size: {status['context_size']} characters
- Workflows Available: {status['workflows_available']}

## Recent Activities
{context[-1000:] if len(context) > 1000 else context}

## Available Applications
{chr(10).join([f"- {app}" for app in self.list_available_apps()[:10]])}

---
Generated by Super Interpreter SDK
        """

        return report.strip()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sdk.end_session()
        print("🏁 Super Interpreter SDK session ended")

def main():
    """Demo of SDK integration"""
    print("🤖 Super Interpreter with Claude Code SDK")
    print("=" * 50)

    with SuperInterpreterSDK() as sdk:
        # Demo: Create a workflow
        commands = [
            "open website github.com in chrome",
            "wait 2 seconds",
            "open app Calculator"
        ]

        print("Creating workflow from commands:")
        for cmd in commands:
            print(f"  - {cmd}")

        sdk.create_workflow_from_commands("demo_workflow", commands)
        print("✅ Workflow created")

        # Demo: Quick automation
        print("\nExecuting quick automation...")
        result = sdk.quick_automation([
            "open website google.com",
            "open app Calculator"
        ])

        print(f"✅ Executed {result['executed_commands']} commands")

        # Demo: Generate report
        print("\n📊 Automation Report:")
        print(sdk.generate_automation_report())

if __name__ == "__main__":
    main()