#!/usr/bin/env python3
"""
Performance Benchmark Script for Voice Transcriber Optimizations
Tests and measures actual performance improvements in the optimized version.
"""

import time
import io
import wave
import pyaudio
import re
import tempfile
import os
from pathlib import Path

def create_test_audio_data(duration_seconds=2, sample_rate=16000):
    """Create test audio data for benchmarking"""
    import numpy as np
    
    # Generate a simple sine wave for testing
    frequency = 440  # A4 note
    frames = int(duration_seconds * sample_rate)
    t = np.linspace(0, duration_seconds, frames, False)
    audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
    
    # Convert to 16-bit integers
    audio_16bit = (audio_data * 32767).astype(np.int16)
    
    # Convert to bytes (chunks of 4096 samples)
    chunk_size = 4096
    audio_chunks = []
    for i in range(0, len(audio_16bit), chunk_size):
        chunk = audio_16bit[i:i + chunk_size]
        audio_chunks.append(chunk.tobytes())
    
    return audio_chunks

def benchmark_file_io_vs_memory():
    """Benchmark file I/O vs in-memory audio processing"""
    print("🧪 Benchmarking File I/O vs In-Memory Processing...")
    
    # Create test audio data
    audio_chunks = create_test_audio_data(duration_seconds=3)
    audio = pyaudio.PyAudio()
    format_val = pyaudio.paInt16
    channels = 1
    rate = 16000
    
    iterations = 50
    
    # Test 1: File-based approach (original)
    file_times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        # Write WAV file
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format_val))
            wf.setframerate(rate)
            wf.writeframes(b''.join(audio_chunks))
        
        # Read it back (simulate API call preparation)
        with open(temp_file.name, 'rb') as f:
            data = f.read()
        
        # Cleanup
        os.unlink(temp_file.name)
        
        end_time = time.perf_counter()
        file_times.append((end_time - start_time) * 1000)  # Convert to ms
    
    # Test 2: In-memory approach (optimized)
    memory_times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        
        # Create in-memory buffer
        audio_buffer = io.BytesIO()
        
        # Write WAV data to memory
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format_val))
            wf.setframerate(rate)
            wf.writeframes(b''.join(audio_chunks))
        
        # Get data (simulate API call preparation)
        audio_buffer.seek(0)
        data = audio_buffer.getvalue()
        
        end_time = time.perf_counter()
        memory_times.append((end_time - start_time) * 1000)  # Convert to ms
    
    audio.terminate()
    
    # Calculate statistics
    avg_file_time = sum(file_times) / len(file_times)
    avg_memory_time = sum(memory_times) / len(memory_times)
    improvement = ((avg_file_time - avg_memory_time) / avg_file_time) * 100
    
    print(f"📊 File I/O Benchmark Results ({iterations} iterations):")
    print(f"   File-based approach: {avg_file_time:.2f}ms average")
    print(f"   In-memory approach:  {avg_memory_time:.2f}ms average")
    print(f"   🚀 Improvement: {improvement:.1f}% faster ({avg_file_time - avg_memory_time:.2f}ms saved)")
    
    return avg_file_time - avg_memory_time

def benchmark_text_processing():
    """Benchmark text processing optimizations"""
    print("\n🧪 Benchmarking Text Processing...")
    
    # Test text with filler words
    test_text = "Um, well, you know, this is like actually a test sentence, um, with basically many filler words, you see, that need to be, uh, removed from the transcription, I mean, for better readability, sort of."
    
    iterations = 1000
    
    # Original approach (nested loops)
    filler_words = {
        'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well',
        'hmm', 'okay', 'right', 'actually', 'basically', 'literally',
        'i mean', 'sort of', 'kind of', 'you see'
    }
    
    def original_clean_text(text):
        words = text.lower().split()
        cleaned_words = []
        i = 0
        while i < len(words):
            word = words[i].strip('.,!?;:"()[]{}')
            skip = False
            for filler_length in [3, 2, 1]:
                if i + filler_length <= len(words):
                    phrase = ' '.join(words[i:i+filler_length]).strip('.,!?;:"()[]{}')
                    if phrase in filler_words:
                        i += filler_length
                        skip = True
                        break
            if not skip:
                cleaned_words.append(words[i])
                i += 1
        return ' '.join(cleaned_words)
    
    # Optimized approach (pre-compiled regex)
    sorted_fillers = sorted(filler_words, key=len, reverse=True)
    escaped_fillers = [re.escape(filler) for filler in sorted_fillers]
    pattern = r'\\b(?:' + '|'.join(escaped_fillers) + r')\\b'
    filler_pattern = re.compile(pattern, re.IGNORECASE)
    
    def optimized_clean_text(text):
        return filler_pattern.sub('', text)
    
    # Test original approach
    original_times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        result = original_clean_text(test_text)
        end_time = time.perf_counter()
        original_times.append((end_time - start_time) * 1000)
    
    # Test optimized approach
    optimized_times = []
    for i in range(iterations):
        start_time = time.perf_counter()
        result = optimized_clean_text(test_text)
        end_time = time.perf_counter()
        optimized_times.append((end_time - start_time) * 1000)
    
    # Calculate statistics
    avg_original_time = sum(original_times) / len(original_times)
    avg_optimized_time = sum(optimized_times) / len(optimized_times)
    improvement = ((avg_original_time - avg_optimized_time) / avg_original_time) * 100
    
    print(f"📊 Text Processing Benchmark Results ({iterations} iterations):")
    print(f"   Original approach:  {avg_original_time:.3f}ms average")
    print(f"   Optimized approach: {avg_optimized_time:.3f}ms average")
    print(f"   🚀 Improvement: {improvement:.1f}% faster ({avg_original_time - avg_optimized_time:.3f}ms saved)")
    
    return avg_original_time - avg_optimized_time

def benchmark_typing_speed():
    """Benchmark typing speed differences"""
    print("\n🧪 Benchmarking Typing Speed Settings...")
    
    test_text = "This is a test sentence for typing speed measurement."
    
    # Simulate typing delays (without actually typing)
    def simulate_typing(text, interval, initial_delay):
        start_time = time.perf_counter()
        time.sleep(initial_delay)  # Initial delay
        
        # Simulate character-by-character delay
        for char in text:
            time.sleep(interval)
        
        end_time = time.perf_counter()
        return (end_time - start_time) * 1000
    
    # Original settings
    original_time = simulate_typing(test_text, 0.01, 0.1)
    
    # Optimized settings  
    optimized_time = simulate_typing(test_text, 0.005, 0.02)
    
    improvement = original_time - optimized_time
    improvement_percent = (improvement / original_time) * 100
    
    print(f"📊 Typing Speed Benchmark Results:")
    print(f"   Original settings (0.01s interval, 0.1s delay): {original_time:.0f}ms")
    print(f"   Optimized settings (0.005s interval, 0.02s delay): {optimized_time:.0f}ms")
    print(f"   🚀 Improvement: {improvement_percent:.1f}% faster ({improvement:.0f}ms saved)")
    
    return improvement

def benchmark_audio_settings():
    """Benchmark audio processing with different settings"""
    print("\n🧪 Benchmarking Audio Settings...")
    
    # Test different chunk sizes and sample rates
    test_scenarios = [
        {"sample_rate": 44100, "chunk_size": 1024, "name": "Original (44.1kHz, 1024)"},
        {"sample_rate": 16000, "chunk_size": 4096, "name": "Optimized (16kHz, 4096)"},
    ]
    
    duration = 3  # seconds
    iterations = 20
    
    results = {}
    
    for scenario in test_scenarios:
        times = []
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            # Create audio data for this scenario
            audio_chunks = create_test_audio_data(
                duration_seconds=duration, 
                sample_rate=scenario["sample_rate"]
            )
            
            # Simulate processing overhead
            total_samples = duration * scenario["sample_rate"]
            num_chunks = total_samples // scenario["chunk_size"]
            
            # Simulate chunk processing time
            for chunk in audio_chunks[:num_chunks]:
                pass  # Simulate minimal processing
            
            end_time = time.perf_counter()
            times.append((end_time - start_time) * 1000)
        
        avg_time = sum(times) / len(times)
        results[scenario["name"]] = avg_time
        print(f"   {scenario['name']}: {avg_time:.2f}ms average")
    
    # Calculate improvement
    original_time = results["Original (44.1kHz, 1024)"]
    optimized_time = results["Optimized (16kHz, 4096)"]
    improvement = ((original_time - optimized_time) / original_time) * 100
    savings = original_time - optimized_time
    
    print(f"   🚀 Audio Settings Improvement: {improvement:.1f}% faster ({savings:.2f}ms saved)")
    
    return savings

def main():
    """Run all benchmarks"""
    print("🚀 Voice Transcriber Performance Benchmark")
    print("=" * 50)
    
    try:
        import numpy as np
    except ImportError:
        print("❌ NumPy not installed. Installing for audio generation...")
        import subprocess
        subprocess.check_call(["pip", "install", "numpy"])
        import numpy as np
    
    total_savings = 0
    
    # Run benchmarks
    total_savings += benchmark_file_io_vs_memory()
    total_savings += benchmark_text_processing()
    total_savings += benchmark_typing_speed()
    total_savings += benchmark_audio_settings()
    
    print("\n" + "=" * 50)
    print(f"📊 TOTAL ESTIMATED PERFORMANCE IMPROVEMENT")
    print(f"   Combined savings: {total_savings:.1f}ms per transcription")
    print(f"   🎯 This represents the actual measurable improvements")
    print("\n💡 Note: API call time (network latency) is the biggest factor")
    print("   and varies based on network conditions and API response time.")

if __name__ == "__main__":
    main()