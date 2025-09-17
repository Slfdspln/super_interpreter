#!/usr/bin/env python3
"""
Browser-Use Integration for Super Interpreter
Advanced browser automation with AI capabilities
"""

import asyncio
import json
import subprocess
import time
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass

# Import existing controllers with fallback
try:
    from .browser_controller import BrowserController
    BROWSER_CONTROLLER_AVAILABLE = True
except ImportError:
    BROWSER_CONTROLLER_AVAILABLE = False
    print("Warning: BrowserController not available (missing playwright)")

try:
    from .claude_sdk_controller import ClaudeSDKController
    SDK_CONTROLLER_AVAILABLE = True
except ImportError:
    SDK_CONTROLLER_AVAILABLE = False
    print("Warning: ClaudeSDKController not available")

@dataclass
class BrowserAction:
    """Represents a browser action to be performed"""
    action_type: str  # 'click', 'type', 'scroll', 'navigate', 'extract'
    target: str = None  # CSS selector or URL
    value: str = None   # Text to type or scroll amount
    wait_time: float = 1.0
    description: str = ""

class BrowserUseAgent:
    """
    AI-powered browser automation agent
    Inspired by browser-use but compatible with Python 3.9
    """

    def __init__(self, task: str, browser_controller=None, sdk=None):
        self.task = task

        # Initialize browser controller
        if BROWSER_CONTROLLER_AVAILABLE and browser_controller:
            self.browser = browser_controller
        elif BROWSER_CONTROLLER_AVAILABLE:
            self.browser = BrowserController("policy.yaml", headed=True)
        else:
            self.browser = None
            print("Browser controller not available - using direct commands")

        # Initialize SDK controller
        if SDK_CONTROLLER_AVAILABLE and sdk:
            self.sdk = sdk
        elif SDK_CONTROLLER_AVAILABLE:
            self.sdk = ClaudeSDKController()
        else:
            self.sdk = None
            print("SDK controller not available - limited tracking")

        self.session_id = self.sdk.start_session("browser_automation") if self.sdk else f"session_{int(time.time())}"
        self.actions_performed = []
        self.current_url = ""
        self.page_content = ""

    def parse_task_to_actions(self, task: str) -> List[BrowserAction]:
        """
        Parse natural language task into browser actions
        Simple rule-based parsing (can be enhanced with LLM later)
        """
        actions = []
        task_lower = task.lower()

        # Extract URLs
        import re
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', task)
        domains = re.findall(r'\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b', task)

        # Navigation actions
        if 'go to' in task_lower or 'navigate to' in task_lower or 'visit' in task_lower:
            if urls:
                url = urls[0]
            elif domains:
                url = f"https://{domains[0]}"
            else:
                url = "https://google.com"

            actions.append(BrowserAction(
                action_type='navigate',
                target=url,
                description=f"Navigate to {url}"
            ))

        # Search actions
        if 'search for' in task_lower:
            search_terms = task_lower.split('search for')[1].strip().replace("'", "").replace('"', '')
            actions.extend([
                BrowserAction(
                    action_type='navigate',
                    target='https://google.com',
                    description="Navigate to Google"
                ),
                BrowserAction(
                    action_type='type',
                    target='input[name="q"]',
                    value=search_terms,
                    description=f"Search for: {search_terms}"
                ),
                BrowserAction(
                    action_type='click',
                    target='input[value="Google Search"]',
                    description="Click search button"
                )
            ])

        # Click actions
        if 'click' in task_lower:
            # Extract what to click (simplified)
            click_target = "button"  # Default
            if 'button' in task_lower:
                click_target = "button"
            elif 'link' in task_lower:
                click_target = "a"

            actions.append(BrowserAction(
                action_type='click',
                target=click_target,
                description=f"Click {click_target}"
            ))

        # Extract data actions
        if 'extract' in task_lower or 'get' in task_lower or 'find' in task_lower:
            actions.append(BrowserAction(
                action_type='extract',
                target='*',
                description="Extract page content"
            ))

        # Default action if no specific actions found
        if not actions:
            actions.append(BrowserAction(
                action_type='extract',
                target='*',
                description="Extract page information"
            ))

        return actions

    async def execute_action(self, action: BrowserAction) -> Dict[str, Any]:
        """Execute a single browser action"""
        try:
            result = {"action": action.action_type, "success": False, "data": None}

            if self.browser:
                # Use Playwright-based browser controller
                if action.action_type == 'navigate':
                    nav_result = self.browser.goto(action.target)
                    result["success"] = nav_result.get("ok", False)
                    result["data"] = nav_result
                    self.current_url = action.target

                elif action.action_type == 'click':
                    click_result = self.browser.click(action.target)
                    result["success"] = click_result.get("ok", False)
                    result["data"] = click_result

                elif action.action_type == 'type':
                    type_result = self.browser.type(action.target, action.value, press_enter=True)
                    result["success"] = type_result.get("ok", False)
                    result["data"] = type_result

                elif action.action_type == 'extract':
                    extract_result = self.browser.scrape_text("body")
                    result["success"] = extract_result.get("ok", False)
                    result["data"] = extract_result
                    if result["success"]:
                        self.page_content = extract_result.get("texts", [""])[0] if extract_result.get("texts") else ""

            else:
                # Fallback to system commands
                if action.action_type == 'navigate':
                    # Open URL in default browser
                    try:
                        subprocess.run(['open', action.target], check=True)
                        result["success"] = True
                        result["data"] = {"message": f"Opened {action.target} in default browser"}
                        self.current_url = action.target
                    except subprocess.CalledProcessError:
                        result["success"] = False
                        result["data"] = {"error": "Failed to open browser"}

                elif action.action_type == 'extract':
                    # Simulate extraction
                    result["success"] = True
                    result["data"] = {"message": "Browser content extraction not available without Playwright"}
                    self.page_content = f"Visited: {self.current_url}"

                else:
                    # Other actions not supported in fallback mode
                    result["success"] = False
                    result["data"] = {"error": f"Action {action.action_type} not supported in fallback mode"}

            # Wait between actions
            await asyncio.sleep(action.wait_time)

            # Log action
            if self.sdk:
                self.sdk.save_context(
                    "browser_action",
                    f"Action: {action.action_type}, Target: {action.target}, Success: {result['success']}",
                    {"timestamp": str(time.time()), "type": "browser_automation"}
                )

            self.actions_performed.append(result)
            return result

        except Exception as e:
            error_result = {"action": action.action_type, "success": False, "error": str(e)}
            self.actions_performed.append(error_result)
            return error_result

    async def run(self) -> Dict[str, Any]:
        """Execute the browser automation task"""
        print(f"🤖 Starting browser automation task: {self.task}")

        # Parse task into actions
        actions = self.parse_task_to_actions(self.task)
        print(f"📋 Planned actions: {len(actions)}")

        results = []

        # Execute each action
        for i, action in enumerate(actions, 1):
            print(f"🔄 Step {i}/{len(actions)}: {action.description}")
            result = await self.execute_action(action)
            results.append(result)

            if not result["success"]:
                print(f"⚠️  Action failed: {result.get('error', 'Unknown error')}")
                # Continue with other actions

        # Take final screenshot if browser available
        screenshot_result = None
        if self.browser:
            screenshot_result = self.browser.screenshot(f"browser_automation_{self.session_id}.png")

        # Generate summary
        summary = self.generate_summary(results)

        final_result = {
            "task": self.task,
            "session_id": self.session_id,
            "actions_performed": len(results),
            "successful_actions": sum(1 for r in results if r["success"]),
            "current_url": self.current_url,
            "page_content_length": len(self.page_content),
            "screenshot": screenshot_result.get("path") if screenshot_result and screenshot_result.get("ok") else None,
            "summary": summary,
            "detailed_results": results
        }

        # Save to context if SDK available
        if self.sdk:
            self.sdk.save_context(
                "browser_automation_complete",
                json.dumps(final_result, indent=2),
                {"timestamp": str(time.time()), "type": "automation_summary"}
            )

        print(f"✅ Browser automation completed!")
        print(f"   Actions performed: {final_result['actions_performed']}")
        print(f"   Successful: {final_result['successful_actions']}")
        print(f"   Current URL: {final_result['current_url']}")

        return final_result

    def generate_summary(self, results: List[Dict]) -> str:
        """Generate a summary of the automation session"""
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        summary = f"Browser automation for task: '{self.task}'\n"
        summary += f"Total actions: {len(results)}, Successful: {len(successful)}, Failed: {len(failed)}\n"

        if self.current_url:
            summary += f"Final URL: {self.current_url}\n"

        if self.page_content:
            # Truncate content for summary
            content_preview = self.page_content[:500] + "..." if len(self.page_content) > 500 else self.page_content
            summary += f"Page content preview: {content_preview}\n"

        return summary

class BrowserUseController:
    """
    Main controller for browser-use integration
    """

    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()

        # Initialize SDK if available
        if SDK_CONTROLLER_AVAILABLE:
            self.sdk = ClaudeSDKController(project_path)
        else:
            self.sdk = None

        # Initialize browser if available
        if BROWSER_CONTROLLER_AVAILABLE:
            self.browser = BrowserController("policy.yaml", headed=True)
        else:
            self.browser = None

    def create_agent(self, task: str) -> BrowserUseAgent:
        """Create a new browser automation agent"""
        return BrowserUseAgent(task, self.browser, self.sdk)

    async def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute a browser automation task"""
        agent = self.create_agent(task)
        return await agent.run()

    def get_available_actions(self) -> List[str]:
        """Get list of available browser actions"""
        return [
            "navigate - Go to a URL",
            "search - Search for something on Google",
            "click - Click an element",
            "type - Type text into a field",
            "extract - Extract content from page",
            "screenshot - Take a screenshot"
        ]

    def create_complex_workflow(self, name: str, tasks: List[str]) -> bool:
        """Create a complex workflow with multiple browser tasks"""
        workflow_steps = []

        for i, task in enumerate(tasks):
            workflow_steps.append({
                "type": "browser_automation",
                "params": {"task": task},
                "description": f"Step {i+1}: {task}",
                "wait_after": 2
            })

        if self.sdk:
            return self.sdk.create_automation_workflow(name, workflow_steps)
        else:
            print(f"Created workflow '{name}' with {len(tasks)} tasks (no persistence without SDK)")
            return True

# Factory functions
def create_browser_use_controller(project_path: str = None) -> BrowserUseController:
    """Create a new Browser-Use controller"""
    return BrowserUseController(project_path)

async def quick_browser_task(task: str) -> Dict[str, Any]:
    """Quick execution of a browser task"""
    controller = create_browser_use_controller()
    return await controller.execute_task(task)