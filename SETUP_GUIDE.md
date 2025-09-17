# 🚀 Super Interpreter - Complete Setup Guide

**Transform your Mac into a fully automated AI assistant that can control ANY application!**

## 📋 What You'll Get

After setup, your Super Interpreter will have:
- ✅ **62+ macOS applications** under full automation control
- ✅ **Calculator automation** - AI presses all buttons automatically
- ✅ **Document automation** - Creates and saves documents automatically
- ✅ **Browser automation** - AI-powered web browsing
- ✅ **Windsurf terminal control** - Direct code execution
- ✅ **Universal app access** - Control ANY Mac application

## 🎯 One-Time Setup (5 minutes)

### Step 1: Download and Install

```bash
# Clone the repository
git clone https://github.com/Slfdspln/super_interpreter.git
cd super_interpreter

# Create Python environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -U pip
pip install open-interpreter anthropic
```

### Step 2: Set Your API Key

Choose **ONE** of these:

```bash
# Option A: Claude API (Recommended)
export ANTHROPIC_API_KEY=your-anthropic-key-here

# Option B: OpenAI API
export OPENAI_API_KEY=your-openai-key-here
```

### Step 3: Critical macOS Permissions (Most Important!)

**🔑 THIS IS THE KEY STEP - Your AI needs permission to control your Mac**

1. **Open System Settings**
   ```bash
   open "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
   ```

2. **Grant Accessibility Permissions**
   - Click the **🔒 lock icon** (bottom left) and enter your password
   - Click the **➕ plus button** to add applications
   - Navigate to your Python location:

     **Find your Python path:**
     ```bash
     which python3
     ```
     Common locations:
     - `/usr/bin/python3` (System Python)
     - `/opt/homebrew/bin/python3` (Homebrew)
     - `/Users/yourusername/.pyenv/versions/3.x.x/bin/python3` (pyenv)

   - **Add Python to accessibility** - Check the box next to python3
   - **Add Terminal** - Also add Terminal.app for script execution

3. **Verify Permissions**
   ```bash
   python -c "
   from controllers.universal_app_controller import create_universal_app_controller
   controller = create_universal_app_controller()
   status = controller.get_accessibility_status()
   print('✅ Accessibility granted:', status['accessibility_granted'])
   "
   ```

### Step 4: Test Your Setup

```bash
# Make the launcher executable
chmod +x cristal-clean

# Launch Super Interpreter
./cristal-clean
```

You should see:
```
🤖 Super Interpreter Ready - FULL AUTOMATION CAPABILITIES
Enhanced with Claude SDK + Browser Automation + Universal App Control + Document Automation
```

## 🧪 Test the Automation

Once running, try these commands in the Super Interpreter:

```python
# Test 1: Instant calculation
quick_calculate("2819 × 3801")

# Test 2: Full calculator automation (opens calculator, presses buttons)
calculate_with_calculator("123 + 456")

# Test 3: App control
launch_any_app("Calculator")
get_running_apps()

# Test 4: Windsurf control (if you have Windsurf)
execute_in_windsurf_terminal("echo 'Hello from automation!'")
```

## 🔧 Troubleshooting

### "Permission Denied" or "Accessibility Error"

**Problem:** Python doesn't have accessibility permissions

**Solution:**
1. Go to **System Settings > Privacy & Security > Accessibility**
2. Remove python3 if already there
3. Re-add python3 with the exact path from `which python3`
4. Restart Terminal and try again

### "Calculator automation hangs"

**Problem:** GUI automation waiting for permissions

**Solution:**
- Use `quick_calculate()` for instant results
- Ensure Calculator.app is in Applications folder
- Check accessibility permissions are granted

### "Command not found: cristal"

**Problem:** Launcher not in PATH

**Solution:**
```bash
# Option A: Use full path
./cristal-clean

# Option B: Add to PATH
export PATH="$PATH:$(pwd)"
cristal
```

### Python Environment Issues

**Problem:** Wrong Python version or missing packages

**Solution:**
```bash
# Check Python version (needs 3.9+)
python3 --version

# Recreate environment
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip open-interpreter anthropic
```

## 🎮 What Your AI Can Now Do

### 🧮 Calculator Automation
```
> Calculate 2819 x 3801

Your AI will:
1. Open Calculator app automatically
2. Press buttons: 2, 8, 1, 9, ×, 3, 8, 0, 1, =
3. Return result: 10,719,219
```

### 📝 Document Automation
```
> Create a document with my calculations and sign it

Your AI will:
1. Process all calculations in a file
2. Open TextEdit automatically
3. Type all results
4. Add your signature
5. Save the document
```

### 🖥️ Universal App Control
```
> Open Discord and send a message

Your AI will:
1. Launch Discord
2. Navigate to channels
3. Type your message
4. Send automatically
```

### 🌐 Browser Automation
```
> Search Google for Python tutorials

Your AI will:
1. Open browser
2. Navigate to Google
3. Search for tutorials
4. Report findings
```

## 🔐 Security & Privacy

- ✅ **No data collection** - Everything runs locally
- ✅ **Permission-based** - You control what apps can be accessed
- ✅ **API key security** - Keys stored in environment variables
- ✅ **Audit trail** - All actions logged

## 🆘 Need Help?

1. **Check permissions** - Run the verification script
2. **Review logs** - Check Terminal output for errors
3. **Test individual components** - Use the test functions
4. **Create an issue** - Report problems on GitHub

## 🎉 You're Ready!

Your Super Interpreter now has **unprecedented control** over your Mac ecosystem. Your AI can:

- Control 62+ applications automatically
- Perform calculations with real button presses
- Create and edit documents
- Browse the web intelligently
- Execute code in terminals
- Manage your entire workflow

**Welcome to the future of Mac automation!** 🚀

---

*Super Interpreter - Making your entire macOS system AI-controllable*