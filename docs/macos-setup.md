# macOS Setup Guide

This guide will help you set up all necessary permissions for WisprFlow Lite on macOS.

## System Requirements

- macOS 10.15 or later
- Python 3.7 or later
- Homebrew (recommended)

## Permission Setup

This is CRITICAL for the app to work! The app needs several permissions to function properly.

### A. Open System Settings
1. Click the Apple menu () > System Settings
2. Go to Privacy & Security > Privacy
3. Click the lock icon 🔒 in the bottom left to make changes (you'll need to enter your password)

### B. Microphone Permissions
1. Scroll to find "Microphone"
2. Enable permissions for:
   - Terminal.app
   - Python (`/opt/homebrew/Cellar/python@3.13/3.13.3_1/bin/python3.13`)
   - Cursor.app (if running from Cursor IDE)

### C. Accessibility Permissions
1. Scroll to find "Accessibility"
2. Click the '+' button
3. Press Command+Shift+G
4. Add and enable ALL of these:
   - `/Applications/Utilities/Terminal.app`
   - `/opt/homebrew/Cellar/python@3.13/3.13.3_1/bin/python3.13`
   - `/Applications/Cursor.app` (if running from Cursor IDE)

### D. Input Monitoring
1. Scroll to find "Input Monitoring"
2. Click the '+' button
3. Press Command+Shift+G
4. Add and enable ALL of these:
   - `/Applications/Utilities/Terminal.app`
   - `/opt/homebrew/Cellar/python@3.13/3.13.3_1/bin/python3.13`
   - `/Applications/Cursor.app` (if running from Cursor IDE)

### E. After Adding Permissions
1. If running from Terminal:
   - Quit Terminal completely (Command+Q)
   - Reopen Terminal
2. If running from Cursor:
   - Quit Cursor completely (Command+Q)
   - Reopen Cursor
3. Try running the app again

### F. Finding Python Path
If you can't find the Python path, try these steps:
1. Open Terminal
2. Run: `brew list python3`
3. Look for the path ending in `/bin/python3.13`
4. Use that path when adding permissions

## Troubleshooting

### Common Issues

**"Process is not trusted!"**
1. Check all permissions are enabled:
   - Microphone
   - Accessibility
   - Input Monitoring
2. Verify Terminal/Cursor AND Python are added to each section
3. Try removing and re-adding permissions:
   - Uncheck the boxes
   - Remove the entries
   - Restart Terminal/Cursor
   - Add them back
4. Make sure to use the exact Python path from `brew list python3`

**"Input event monitoring not possible"**
1. Double-check Input Monitoring permissions:
   - Both Terminal/Cursor and Python should be checked
   - Try unchecking and rechecking
2. Verify Python path:
   - Use Command+Shift+G to enter the path exactly
   - Make sure to add to ALL required sections
3. If still not working:
   - Remove all permissions
   - Restart your Mac
   - Add permissions again
   - Start with a fresh Terminal/Cursor window

**"No audio device found"**
1. Check System Settings:
   - Privacy & Security > Privacy > Microphone
   - Enable for Terminal/Cursor and Python
2. Test your microphone:
   - System Settings > Sound
   - Check input device is detected
   - Speak and verify input level moves
3. Hardware checks:
   - Unplug and replug external microphones
   - Try built-in microphone if available
   - Check mute switch if applicable

### General Tips
- Always quit Terminal completely after permission changes
- Use Command+Shift+G to enter paths exactly
- Double-check all checkboxes in each permission section
- When in doubt, remove and re-add permissions
- Restart Terminal (or your Mac) if problems persist 