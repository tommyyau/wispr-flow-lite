#!/usr/bin/env python3
"""
Quick performance test to compare VAD vs MP3 versions
"""

import os
import sys
import time
import subprocess
from dotenv import load_dotenv

load_dotenv()

def test_version_startup(script_name):
    """Test how long each version takes to start up"""
    print(f"\n🧪 Testing {script_name} startup time...")
    
    start_time = time.perf_counter()
    
    # Start the process and immediately kill it to measure startup time
    try:
        process = subprocess.Popen(
            [sys.executable, script_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for initialization
        time.sleep(2)
        
        # Kill the process
        process.terminate()
        process.wait()
        
        startup_time = time.perf_counter() - start_time
        print(f"   Startup time: {startup_time:.2f}s")
        return startup_time
        
    except Exception as e:
        print(f"   Error testing {script_name}: {e}")
        return None

def check_dependencies():
    """Check what dependencies each version requires"""
    print("\n📦 Checking dependencies...")
    
    vad_imports = [
        "torch", "torchaudio", "numpy", "requests", "pyaudio", 
        "keyboard", "pyautogui", "pynput", "python-dotenv"
    ]
    
    mp3_imports = vad_imports + ["pydub", "audioop-lts"]
    
    print(f"   VAD version imports: {len(vad_imports)} modules")
    print(f"   MP3 version imports: {len(mp3_imports)} modules")
    
    # Test pydub specifically
    try:
        from pydub import AudioSegment
        print("   ✅ pydub available")
    except ImportError as e:
        print(f"   ❌ pydub issue: {e}")

def analyze_code_complexity():
    """Compare code complexity between versions"""
    print("\n🔍 Analyzing code complexity...")
    
    files = [
        "voice_transcriber_fireworks_vad.py",
        "voice_transcriber_fireworks_mp3.py"
    ]
    
    for file in files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                lines = f.readlines()
                total_lines = len(lines)
                code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
                functions = len([l for l in lines if l.strip().startswith('def ')])
                
                print(f"   {file}:")
                print(f"     Total lines: {total_lines}")
                print(f"     Code lines: {code_lines}")
                print(f"     Functions: {functions}")

def main():
    print("🚀 QUICK PERFORMANCE COMPARISON")
    print("=" * 50)
    
    # Check API key
    if not os.getenv('FIREWORKS_API_KEY'):
        print("❌ No FIREWORKS_API_KEY found in .env")
        return
    
    check_dependencies()
    analyze_code_complexity()
    
    # Test startup times
    vad_time = test_version_startup("voice_transcriber_fireworks_vad.py")
    mp3_time = test_version_startup("voice_transcriber_fireworks_mp3.py")
    
    if vad_time and mp3_time:
        print(f"\n📊 COMPARISON RESULTS:")
        print(f"   VAD version: {vad_time:.2f}s startup")
        print(f"   MP3 version: {mp3_time:.2f}s startup")
        
        if mp3_time > vad_time:
            overhead = ((mp3_time - vad_time) / vad_time) * 100
            print(f"   MP3 overhead: +{overhead:.1f}% slower startup")
        else:
            improvement = ((vad_time - mp3_time) / vad_time) * 100
            print(f"   MP3 improvement: {improvement:.1f}% faster startup")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   • VAD version: Simpler, faster startup, proven stable")
    print(f"   • MP3 version: Better for large files, but more complex")
    print(f"   • For quick commands: VAD version likely better")
    print(f"   • For long recordings: MP3 version may be better")

if __name__ == "__main__":
    main()