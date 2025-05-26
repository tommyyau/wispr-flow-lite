#!/usr/bin/env python3
"""
Voice Transcriber Installer
Automatically sets up the voice transcription app on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, shell=False):
    """Run a command and return success status"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), capture_output=True, text=True)
        
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} found")
        return True
    else:
        print(f"❌ Python 3.7+ required, found {version.major}.{version.minor}.{version.micro}")
        return False

def install_system_dependencies():
    """Install system-specific dependencies"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 Installing macOS dependencies...")
        success, _ = run_command("brew --version")
        if not success:
            print("⚠️  Homebrew not found. Installing portaudio may fail.")
            print("💡 Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        else:
            success, output = run_command("brew install portaudio")
            if success:
                print("✅ portaudio installed")
    
    elif system == "linux":
        print("🐧 Installing Linux dependencies...")
        # Try apt-get first (Ubuntu/Debian)
        success, output = run_command("sudo apt-get update && sudo apt-get install -y portaudio19-dev python3-dev", shell=True)
        if success:
            print("✅ System dependencies installed")
        else:
            print("⚠️  Could not install dependencies automatically.")
            print("💡 Manual install: sudo apt-get install portaudio19-dev python3-dev")
    
    elif system == "windows":
        print("🪟 Windows detected - dependencies will be installed via pip")
    
    return True

def create_virtual_environment():
    """Create virtual environment"""
    print("📦 Creating virtual environment...")
    
    success, output = run_command("python -m venv venv")
    if not success:
        # Try python3 command
        success, output = run_command("python3 -m venv venv")
    
    if success:
        print("✅ Virtual environment created")
        return True
    else:
        print(f"❌ Failed to create virtual environment: {output}")
        return False

def install_packages():
    """Install Python packages"""
    print("📥 Installing Python packages...")
    
    system = platform.system().lower()
    if system == "windows":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Install requirements
    success, output = run_command(f"{pip_cmd} install -r requirements.txt")
    if success:
        print("✅ All packages installed successfully!")
        return True
    else:
        print(f"❌ Package installation failed: {output}")
        print("💡 Try installing packages manually:")
        print(f"   {pip_cmd} install openai pyaudio keyboard pyautogui pynput python-dotenv tenacity")
        return False

def create_launcher_scripts():
    """Create launcher scripts"""
    print("🚀 Creating launcher scripts...")
    
    system = platform.system().lower()
    
    if system == "windows":
        # Windows batch file
        batch_content = """@echo off
echo Starting Voice Transcriber...
cd /d "%~dp0"
venv\\Scripts\\python.exe voice_transcriber.py
pause
"""
        with open("start_transcriber.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created start_transcriber.bat")
    
    else:
        # Unix shell script
        shell_content = """#!/bin/bash
echo "Starting Voice Transcriber..."
cd "$(dirname "$0")"
./venv/bin/python voice_transcriber.py
"""
        with open("start_transcriber.sh", "w") as f:
            f.write(shell_content)
        
        # Make executable
        os.chmod("start_transcriber.sh", 0o755)
        print("✅ Created start_transcriber.sh")
    
    return True

def print_instructions():
    """Print setup instructions"""
    system = platform.system().lower()
    
    print("\n" + "="*60)
    print("🎉 Installation Complete!")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Get your OpenAI API key:")
    print("   https://platform.openai.com/account/api-keys")
    
    print("\n2. Edit the .env file and replace 'your-api-key-here' with your actual API key")
    
    if system == "darwin":
        print("\n3. Grant permissions on macOS:")
        print("   System Preferences > Security & Privacy > Privacy")
        print("   • Enable 'Microphone' access")
        print("   • Enable 'Accessibility' access") 
        print("   • Enable 'Input Monitoring' access")
    
    elif system == "linux":
        print("\n3. Add your user to audio group:")
        print("   sudo usermod -a -G audio $USER")
        print("   (logout and login again)")
    
    print("\n4. Start the application:")
    if system == "windows":
        print("   Double-click: start_transcriber.bat")
    else:
        print("   Run: ./start_transcriber.sh")
    
    print("\n💡 Usage:")
    print("   • Press F9 to start/stop recording")
    print("   • Position cursor where you want text")
    print("   • Speak clearly into microphone") 
    print("   • Press Ctrl+C to quit")
    
    print("\n" + "="*60)

def main():
    """Main installer"""
    print("🎙️ Voice Transcriber Installer")
    print("="*40)
    
    if not check_python():
        return 1
    
    if not install_system_dependencies():
        print("⚠️  Continuing despite system dependency issues...")
    
    if not create_virtual_environment():
        return 1
    
    if not install_packages():
        return 1
    
    if not create_launcher_scripts():
        return 1
    
    print_instructions()
    return 0

if __name__ == "__main__":
    sys.exit(main())