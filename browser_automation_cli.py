#!/usr/bin/env python3
"""
Browser Automation CLI - Browser-Use Integration
Advanced browser control for Super Interpreter
"""

import asyncio
import sys
import json
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from controllers.browser_use_controller import create_browser_use_controller, quick_browser_task

class BrowserAutomationCLI:
    """Command-line interface for browser automation"""

    def __init__(self):
        self.controller = create_browser_use_controller()

    def print_help(self):
        """Print help information"""
        print("🤖 Browser Automation CLI - Advanced Browser Control")
        print("=" * 55)
        print()
        print("Commands:")
        print("  task '<description>'     - Execute browser automation task")
        print("  workflow <name> [tasks]  - Create workflow from tasks")
        print("  actions                  - List available actions")
        print("  help                     - Show this help")
        print("  exit                     - Exit the CLI")
        print()
        print("Examples:")
        print("  task 'search Google for Python tutorials'")
        print("  task 'go to github.com and find trending repos'")
        print("  task 'navigate to news.ycombinator.com'")
        print("  workflow daily_check 'go to github.com' 'check notifications'")
        print()
        print("Available Actions:")
        for action in self.controller.get_available_actions():
            print(f"  • {action}")

    async def execute_task(self, task_description: str):
        """Execute a browser automation task"""
        print(f"\n🚀 Executing task: {task_description}")
        print("-" * 50)

        try:
            result = await self.controller.execute_task(task_description)

            print("\n📊 Task Results:")
            print(f"  ✅ Actions performed: {result['actions_performed']}")
            print(f"  ✅ Successful: {result['successful_actions']}")
            print(f"  🌐 Final URL: {result['current_url']}")

            if result.get('screenshot'):
                print(f"  📸 Screenshot: {result['screenshot']}")

            print(f"\n📝 Summary:")
            print(result['summary'])

            return result

        except Exception as e:
            print(f"❌ Error executing task: {e}")
            return {"error": str(e)}

    def create_workflow(self, name: str, tasks: list):
        """Create a workflow from multiple tasks"""
        print(f"\n🔧 Creating workflow: {name}")
        print(f"📋 Tasks: {len(tasks)}")

        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task}")

        success = self.controller.create_complex_workflow(name, tasks)

        if success:
            print(f"✅ Workflow '{name}' created successfully!")
        else:
            print(f"❌ Failed to create workflow '{name}'")

        return success

    async def interactive_mode(self):
        """Run in interactive mode"""
        print("🤖 Browser Automation Interactive Mode")
        print("Type 'help' for commands or 'exit' to quit")
        print()

        while True:
            try:
                user_input = input("browser> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("👋 Goodbye!")
                    break

                elif user_input.lower() == 'help':
                    self.print_help()

                elif user_input.lower() == 'actions':
                    print("\nAvailable Actions:")
                    for action in self.controller.get_available_actions():
                        print(f"  • {action}")

                elif user_input.startswith('task '):
                    task = user_input[5:].strip().strip("'\"")
                    await self.execute_task(task)

                elif user_input.startswith('workflow '):
                    parts = user_input[9:].strip().split()
                    if len(parts) >= 2:
                        name = parts[0]
                        tasks = [t.strip("'\"") for t in parts[1:]]
                        self.create_workflow(name, tasks)
                    else:
                        print("Usage: workflow <name> '<task1>' '<task2>' ...")

                else:
                    # Treat as task if not a command
                    await self.execute_task(user_input)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def main():
    """Main entry point"""
    cli = BrowserAutomationCLI()

    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()

        if command == 'task' and len(sys.argv) > 2:
            task = ' '.join(sys.argv[2:])
            await cli.execute_task(task)

        elif command == 'workflow' and len(sys.argv) > 3:
            name = sys.argv[2]
            tasks = sys.argv[3:]
            cli.create_workflow(name, tasks)

        elif command == 'actions':
            print("Available Actions:")
            for action in cli.controller.get_available_actions():
                print(f"  • {action}")

        elif command == 'help':
            cli.print_help()

        else:
            print("Unknown command. Use 'help' for usage information.")

    else:
        # Interactive mode
        await cli.interactive_mode()

if __name__ == "__main__":
    asyncio.run(main())