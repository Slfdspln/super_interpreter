# 🚀 Quick Start Guide

## Fastest Ways to Run Super Interpreter

### Option 1: Use `cristal` command (Recommended)
Since `/Users/cristalrivera/super_interpreter` is in your PATH:

```bash
cristal
```

This works from any directory and handles virtual environment activation automatically.

### Option 2: Add Shell Alias
Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
alias super='cd /Users/cristalrivera/super_interpreter && source .venv/bin/activate && python run.py'
```

Then reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

Now you can run from anywhere:
```bash
super
```

### Option 3: Direct Execution
From the project directory:
```bash
./run.py
```

Or with full path from anywhere:
```bash
/Users/cristalrivera/super_interpreter/run.py
```

## What Each Option Does

- **`cristal`**: Custom launcher script that changes to project directory, activates venv, and runs interpreter
- **Shell alias**: One-liner that does the same via shell alias
- **Direct execution**: Uses shebang to run Python script directly

All methods are faster than the original 3-step process!