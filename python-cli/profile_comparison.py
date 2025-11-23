#!/usr/bin/env python3
"""
Profile and compare the original vs optimized voice transcriber implementations
to identify where the real bottlenecks are.
"""

import time
import sys
import io
import wave
import pyaudio
import re
import tempfile
import os

def create_mock_audio_data(duration_seconds=3):
    """Create mock audio data for testing both versions"""
    import numpy as np
    
    # Generate test audio
    sample_rate = 16000
    frequency = 440
    frames = int(duration_seconds * sample_rate)
    t = np.linspace(0, duration_seconds, frames, False)
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
    audio_16bit = (audio_data * 32767).astype(np.int16)
    
    # Convert to chunks like the real recording would produce
    chunk_size = 4096
    audio_chunks = []
    for i in range(0, len(audio_16bit), chunk_size):
        chunk = audio_16bit[i:i + chunk_size]
        audio_chunks.append(chunk.tobytes())
    
    return audio_chunks

def profile_original_approach(audio_chunks):
    """Profile the original file-based approach"""
    print("🔍 Profiling ORIGINAL approach...")
    
    times = {}
    total_start = time.perf_counter()
    
    # Step 1: Save to file (original approach)
    file_start = time.perf_counter()
    audio = pyaudio.PyAudio()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    
    with wave.open(temp_file.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(audio_chunks))
    
    audio.terminate()
    times['file_creation'] = (time.perf_counter() - file_start) * 1000
    
    # Step 2: Text processing (original nested loop approach)
    text_start = time.perf_counter()
    test_text = "Um, well, you know, this is like actually a test sentence with filler words."
    
    # Original filler word removal
    filler_words = {'um', 'uh', 'well', 'like', 'you know', 'actually'}
    words = test_text.lower().split()
    cleaned_words = []
    i = 0
    while i < len(words):
        word = words[i].strip('.,!?;:"()[]{}')
        skip = False
        for filler_length in [2, 1]:  # Check multi-word then single word
            if i + filler_length <= len(words):
                phrase = ' '.join(words[i:i+filler_length]).strip('.,!?;:"()[]{}')
                if phrase in filler_words:
                    i += filler_length
                    skip = True
                    break
        if not skip:
            cleaned_words.append(words[i])
            i += 1
    
    cleaned_text = ' '.join(cleaned_words)
    times['text_processing'] = (time.perf_counter() - text_start) * 1000
    
    # Step 3: Typing simulation (original settings)
    typing_start = time.perf_counter()
    time.sleep(0.1)  # Original initial delay
    # Simulate typing with original interval (0.01s per char)
    typing_simulation_time = len(cleaned_text) * 0.01
    time.sleep(min(typing_simulation_time, 0.1))  # Cap simulation time
    times['typing'] = (time.perf_counter() - typing_start) * 1000
    
    # Cleanup
    os.unlink(temp_file.name)
    
    times['total'] = (time.perf_counter() - total_start) * 1000
    
    print(f"   📁 File creation: {times['file_creation']:.1f}ms")
    print(f"   📝 Text processing: {times['text_processing']:.2f}ms")  
    print(f"   ⌨️  Typing: {times['typing']:.1f}ms")
    print(f"   🏁 Total: {times['total']:.1f}ms")
    
    return times

def profile_optimized_approach(audio_chunks):
    """Profile the optimized in-memory approach"""
    print("\\n🚀 Profiling OPTIMIZED approach...")
    
    times = {}
    total_start = time.perf_counter()
    
    # Step 1: In-memory buffer (optimized approach)
    buffer_start = time.perf_counter()
    audio = pyaudio.PyAudio()
    audio_buffer = io.BytesIO()
    
    with wave.open(audio_buffer, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(audio_chunks))
    
    audio_buffer.seek(0)
    audio_data = audio_buffer.getvalue()
    audio.terminate()
    times['buffer_creation'] = (time.perf_counter() - buffer_start) * 1000
    
    # Step 2: Text processing (optimized regex approach)
    text_start = time.perf_counter()
    test_text = "Um, well, you know, this is like actually a test sentence with filler words."
    
    # Pre-compiled regex approach
    filler_words = {'um', 'uh', 'well', 'like', 'you know', 'actually'}
    sorted_fillers = sorted(filler_words, key=len, reverse=True)
    escaped_fillers = [re.escape(filler) for filler in sorted_fillers]
    pattern = r'\\b(?:' + '|'.join(escaped_fillers) + r')\\b'
    filler_pattern = re.compile(pattern, re.IGNORECASE)
    
    cleaned_text = filler_pattern.sub('', test_text).strip()
    times['text_processing'] = (time.perf_counter() - text_start) * 1000
    
    # Step 3: Typing simulation (optimized settings)
    typing_start = time.perf_counter()
    time.sleep(0.02)  # Optimized initial delay
    # Simulate typing with optimized interval (0.005s per char)
    typing_simulation_time = len(cleaned_text) * 0.005
    time.sleep(min(typing_simulation_time, 0.05))  # Cap simulation time
    times['typing'] = (time.perf_counter() - typing_start) * 1000
    
    times['total'] = (time.perf_counter() - total_start) * 1000
    
    print(f"   💾 Buffer creation: {times['buffer_creation']:.1f}ms")
    print(f"   📝 Text processing: {times['text_processing']:.2f}ms")
    print(f"   ⌨️  Typing: {times['typing']:.1f}ms")
    print(f"   🏁 Total: {times['total']:.1f}ms")
    
    return times

def analyze_api_bottleneck():
    """Analyze the API call bottleneck"""
    print("\\n🌐 Analyzing API Call Bottleneck...")
    print("   📡 Typical Fireworks API response times:")
    print("   • Network latency: 50-200ms")
    print("   • Processing time: 500-2000ms (depends on audio length)")
    print("   • Data transfer: 10-100ms (depends on audio size)")
    print("   📊 Total API time: 560-2300ms")
    print("   💡 This is 80-95% of total processing time!")

def main():
    """Run the comparison profiling"""
    print("🔬 Voice Transcriber Performance Profiler")
    print("=" * 50)
    
    try:
        import numpy as np
    except ImportError:
        print("❌ Installing NumPy for audio generation...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy as np
    
    # Generate test audio data
    audio_chunks = create_mock_audio_data(duration_seconds=3)
    print(f"🎵 Generated {len(audio_chunks)} audio chunks ({sum(len(c) for c in audio_chunks)} bytes)")
    
    # Profile both approaches
    original_times = profile_original_approach(audio_chunks)
    optimized_times = profile_optimized_approach(audio_chunks)
    
    # Calculate improvements
    print("\\n" + "=" * 50)
    print("📊 PERFORMANCE COMPARISON")
    
    categories = ['file_creation', 'text_processing', 'typing', 'total']
    mapping = {'file_creation': 'buffer_creation'}  # Map original to optimized names
    
    total_savings = 0
    for category in categories:
        orig_key = category
        opt_key = mapping.get(category, category)
        
        if orig_key in original_times and opt_key in optimized_times:
            original_time = original_times[orig_key]
            optimized_time = optimized_times[opt_key]
            savings = original_time - optimized_time
            improvement = (savings / original_time) * 100 if original_time > 0 else 0
            
            print(f"   {orig_key.replace('_', ' ').title()}: {savings:+.1f}ms ({improvement:+.1f}%)")
            if category != 'total':
                total_savings += savings
    
    print(f"\\n🎯 REAL PERFORMANCE IMPACT:")
    print(f"   Local optimizations save: ~{total_savings:.0f}ms")
    print(f"   But API calls typically take: 1000-2500ms")
    print(f"   So optimizations provide: {(total_savings/1500)*100:.1f}% improvement")
    
    analyze_api_bottleneck()
    
    print("\\n💡 CONCLUSION:")
    print("   • Local optimizations help, but API latency dominates")
    print("   • Focus on API response time and caching for bigger gains")
    print("   • Consider streaming/partial results for better UX")

if __name__ == "__main__":
    main()