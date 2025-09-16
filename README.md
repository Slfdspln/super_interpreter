# 🤖 Super Interpreter

A powerful automation framework that combines browser automation, OS control, and native macOS app automation in one unified system.

## ✨ Features

- 🌐 **Browser Automation** - Control web browsers with Playwright
- 💻 **OS Control** - Execute shell commands and manage files securely
- 🖥️ **macOS App Automation** - Control native Mac applications using Accessibility API
- 🎯 **Policy-Based Security** - Configurable permissions and confirmations
- 🤖 **LLM Integration** - Works with OpenAI GPT and Anthropic Claude models

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- macOS (for app automation features)
- OpenAI API key or Anthropic API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd super_interpreter
   ```

2. **Set up Python environment**
   ```bash
   pyenv local 3.12.6  # or your Python 3.12+ version
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -U pip setuptools wheel
   pip install open-interpreter==0.4.3 playwright==1.55.0 typer==0.12.5
   python -m playwright install
   ```

4. **Set your API key**
   ```bash
   export OPENAI_API_KEY=your-openai-key-here
   # OR
   export ANTHROPIC_API_KEY=your-anthropic-key-here
   ```

5. **Setup macOS permissions** (for app automation)
   ```bash
   python setup_permissions.py
   ```
   This will:
   - Auto-open System Settings to the right page
   - Copy the Python path to your clipboard
   - Guide you through granting Accessibility permissions
   - Test that everything works

6. **Run the super interpreter**
   ```bash
   cristal
   ```

## 🎮 Usage Examples

### Browser Automation
```python
# Navigate to a website
browser.goto("https://example.com")

# Click elements and scrape text
browser.click("button")
browser.scrape_text("h1")

# Take screenshots
browser.screenshot("page.png")
```

### OS Control
```python
# Run shell commands
osctl.run_shell("ls -la", cwd="/Users/username")

# Write files securely
osctl.write_file("notes.txt", "Hello World!")

# Open in code editor
osctl.open_in_editor("myfile.py", editor="code")
```

### macOS App Automation
```python
# Control any Mac application
windsurf.activate()
windsurf.open_path("/path/to/project")
windsurf.menu_click(["File", "New File"])
windsurf.keystroke("s", ["command"])  # Cmd+S
windsurf.type_text("Hello from automation!")
```

### CLI Tools

Control apps directly from terminal:
```bash
# Activate applications
python app_cli.py activate --app-name "Windsurf"

# Open projects
python app_cli.py open "/path/to/project" --app-name "Windsurf"

# Automate interactions
python app_cli.py menu --app-name "Windsurf" --items File "New File"
python app_cli.py keystroke "s" --app-name "Windsurf" --command
```

## 📁 Project Structure

```
super_interpreter/
├── controllers/
│   ├── browser_controller.py    # Playwright web automation
│   ├── os_controller.py         # OS operations & file management
│   └── app_controller_macos.py  # Native macOS app control
├── policy.yaml                  # Security policies & permissions
├── run.py                       # Main LLM integration script
├── app_cli.py                   # CLI tool for direct automation
├── snake_game.html             # Demo: Single-file HTML5 game
└── README.md                   # This file
```

## ⚙️ Configuration

Edit `policy.yaml` to customize:

- **Browser domains** - Whitelist allowed websites
- **File system access** - Restrict write/read locations
- **Confirmation prompts** - Enable/disable user confirmations
- **Allowed editors** - Specify which code editors can be opened

## 🎯 Demo Projects

- **Snake Game** (`snake_game.html`) - A complete HTML5 game in a single file
- **Browser automation examples** - Web scraping and interaction
- **App control workflows** - Multi-application automation chains

## 🛡️ Security

- Policy-based permissions system
- User confirmation prompts for sensitive operations
- No hardcoded secrets or API keys
- Restricted file system access

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is open source and available under the MIT License.

---

*Built with ❤️ for automation enthusiasts*