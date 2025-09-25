#!/bin/bash

echo "🔧 Shell Function Update for Docker Automation"
echo ""
echo "Your shell has a 'cristal' function that needs to be updated."
echo ""
echo "Please replace the existing cristal function in your shell profile with:"
echo ""
echo "# Updated cristal function with Docker automation support"
echo "cristal() {"
echo "    echo '[Cristal] Starting Cristal Super Interpreter...'"
echo "    echo '🚀 Loading: Docker automation + Calculator + Universal app control + Document creation'"
echo "    cd ~/super_interpreter || return 1"
echo "    source .venv/bin/activate"
echo "    python3 run.py  # Use python3 instead of python"
echo "}"
echo ""
echo "Then run: source ~/.zshrc (or your shell profile file)"
echo ""

# Find the shell profile file
echo "🔍 Checking for shell profile files:"
for file in ~/.zshrc ~/.bash_profile ~/.bashrc ~/.profile; do
    if [ -f "$file" ]; then
        echo "Found: $file"
        if grep -q "cristal ()" "$file" 2>/dev/null || grep -q "cristal() {" "$file" 2>/dev/null; then
            echo "  ✅ Contains cristal function - update this file"
        fi
    fi
done

echo ""
echo "Or simply run: unset -f cristal"
echo "Then use: ./cristal (to use the local script)"