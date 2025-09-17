# 🚀 Quick Start Guide

## Fastest Ways to Run Super Interpreter

### Option 1: Use `cristal-clean` command (Recommended)
From your project directory:

```bash
./cristal-clean
```

This automatically activates the virtual environment and starts with full automation features.

### Option 2: Add Shell Alias (Optional)
Add this to your `~/.zshrc` or `~/.bashrc` for global access:

```bash
alias super='cd /path/to/your/super_interpreter && ./cristal-clean'
```

Replace `/path/to/your/super_interpreter` with your actual project location:
```bash
# Example setup:
cd ~/Downloads/super_interpreter  # or wherever you cloned it
pwd  # Copy this path
```

Then add to your shell config:
```bash
alias super='cd /Users/yourname/Downloads/super_interpreter && ./cristal-clean'
```

Reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Now you can run from anywhere:
```bash
super
```

### Option 3: Add to PATH (Advanced)
To use `cristal` from anywhere, add the project directory to your PATH:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$PATH:/path/to/your/super_interpreter"
```

Then use:
```bash
cristal-clean
```

## What Each Option Does

- **`./cristal-clean`**: Enhanced launcher with full automation features (recommended)
- **Shell alias**: Global shortcut to run from any directory
- **PATH export**: Makes `cristal-clean` available system-wide

## 🎯 First Time Setup

1. **Clone and enter project:**
   ```bash
   git clone https://github.com/Slfdspln/super_interpreter.git
   cd super_interpreter
   ```

2. **Quick setup:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install open-interpreter anthropic
   export ANTHROPIC_API_KEY=your-key
   ```

3. **Launch:**
   ```bash
   ./cristal-clean
   ```

**That's it! No hardcoded paths, works for every user!** 🚀