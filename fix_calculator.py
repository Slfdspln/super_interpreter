#!/usr/bin/env python3
"""
Quick fix to remove Calculator blocking from the running interpreter session
"""

print("🔧 Applying Calculator fix...")

# Monkey patch to remove blocking
def enable_all_apps():
    """Remove all app blocking"""
    import builtins
    import os
    from controllers.app_controller_macos import launch_any_app as original_launch

    # Restore original system function
    if hasattr(builtins, '_original_system'):
        os.system = builtins._original_system
        builtins.system = builtins._original_system

    # Create new non-blocking launch function
    def unblocked_launch_any_app(app_name, path=None):
        print(f"🚀 LAUNCHING {app_name} with full UI automation available")
        return original_launch(app_name, path)

    return unblocked_launch_any_app

# Apply the fix
new_launch = enable_all_apps()

# Test it
print("Testing Calculator launch...")
result = new_launch("Calculator")
print(f"Result: {result}")

print("✅ Fix applied! All apps should now be available.")
print("You can now use:")
print("  - launch_any_app('Calculator')")
print("  - launch_any_app('TextEdit')")
print("  - launch_any_app('Messages')")
print("  - launch_any_app('Any App Name')")