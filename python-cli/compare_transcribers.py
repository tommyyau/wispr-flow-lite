#!/usr/bin/env python3
"""
Comprehensive comparison test between Fireworks and OpenAI transcribers.
Tests both performance and accuracy using the same audio data.
"""

import os
import sys
import time
import io
import wave
import pyaudio
import tempfile
import statistics
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_test_audio(duration_seconds=3, sample_rate=16000, save_to_file=None):
    """Create test audio data for consistent testing"""
    try:
        import numpy as np
    except ImportError:
        print("Installing NumPy for audio generation...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
        import numpy as np
    
    # Generate a sine wave with some modulation for more realistic testing
    frequency = 440  # A4 note
    mod_frequency = 5  # Modulation frequency
    frames = int(duration_seconds * sample_rate)
    t = np.linspace(0, duration_seconds, frames, False)
    
    # Create a modulated sine wave
    carrier = np.sin(2 * np.pi * frequency * t)
    modulation = 0.3 * np.sin(2 * np.pi * mod_frequency * t)
    audio_data = carrier * (0.7 + modulation)
    
    # Convert to 16-bit integers
    audio_16bit = (audio_data * 16383).astype(np.int16)  # Slightly quieter to avoid clipping
    
    # Save to file if requested
    if save_to_file:
        audio = pyaudio.PyAudio()
        with wave.open(save_to_file, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(sample_rate)
            wf.writeframes(audio_16bit.tobytes())
        audio.terminate()
    
    # Convert to chunks like the real recording would produce
    chunk_size = 4096
    audio_chunks = []
    for i in range(0, len(audio_16bit), chunk_size):
        chunk = audio_16bit[i:i + chunk_size]
        audio_chunks.append(chunk.tobytes())
    
    return audio_chunks, audio_16bit.tobytes()

def test_fireworks_transcriber(audio_chunks, audio_data):
    """Test Fireworks transcriber performance"""
    print("🚀 Testing Fireworks Transcriber...")
    
    api_key = os.getenv('FIREWORKS_API_KEY')
    if not api_key or api_key == 'your-api-key-here':
        print("❌ FIREWORKS_API_KEY not found in .env file")
        return None
    
    try:
        import requests
        
        results = {}
        total_start = time.perf_counter()
        
        # Step 1: Create in-memory audio buffer (optimized approach)
        buffer_start = time.perf_counter()
        audio_buffer = io.BytesIO()
        audio = pyaudio.PyAudio()
        
        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(audio_chunks))
        
        audio_buffer.seek(0)
        audio_data_wav = audio_buffer.getvalue()
        audio.terminate()
        results['buffer_creation'] = (time.perf_counter() - buffer_start) * 1000
        
        # Step 2: API call
        api_start = time.perf_counter()
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {api_key}"})
        
        response = session.post(
            "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions",
            files={"file": ("audio.wav", io.BytesIO(audio_data_wav), "audio/wav")},
            data={
                "model": "whisper-v3-turbo",
                "temperature": "0",
                "vad_model": "silero",
                "language": "en"
            }
        )
        
        results['api_call'] = (time.perf_counter() - api_start) * 1000
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('text', '')
            results['success'] = True
            results['transcribed_text'] = text
            results['response_size'] = len(response.content)
        else:
            print(f"❌ Fireworks API error: {response.status_code} - {response.text}")
            results['success'] = False
            results['error'] = f"{response.status_code}: {response.text}"
        
        session.close()
        results['total_time'] = (time.perf_counter() - total_start) * 1000
        
        return results
        
    except Exception as e:
        print(f"❌ Fireworks test failed: {e}")
        return {'success': False, 'error': str(e)}

def test_openai_transcriber(audio_chunks, audio_data):
    """Test OpenAI transcriber performance"""
    print("🤖 Testing OpenAI Transcriber...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-api-key-here':
        print("❌ OPENAI_API_KEY not found in .env file")
        return None
    
    try:
        from openai import OpenAI
        
        results = {}
        total_start = time.perf_counter()
        
        # Step 1: Create temporary file (original approach)
        file_start = time.perf_counter()
        audio = pyaudio.PyAudio()
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        
        with wave.open(temp_file.name, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(16000)
            wf.writeframes(b''.join(audio_chunks))
        
        audio.terminate()
        results['file_creation'] = (time.perf_counter() - file_start) * 1000
        
        # Step 2: API call
        api_start = time.perf_counter()
        client = OpenAI(api_key=api_key)
        
        with open(temp_file.name, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"
            )
        
        results['api_call'] = (time.perf_counter() - api_start) * 1000
        
        # Cleanup temp file
        os.unlink(temp_file.name)
        
        results['success'] = True
        results['transcribed_text'] = transcript.text
        results['total_time'] = (time.perf_counter() - total_start) * 1000
        
        return results
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return {'success': False, 'error': str(e)}

def run_multiple_tests(num_tests=3):
    """Run multiple tests for statistical accuracy"""
    print(f"🧪 Running {num_tests} test iterations for statistical accuracy...")
    
    fireworks_results = []
    openai_results = []
    
    for i in range(num_tests):
        print(f"\\n--- Test {i+1}/{num_tests} ---")
        
        # Create consistent test audio for this iteration
        audio_chunks, audio_raw = create_test_audio(duration_seconds=3)
        
        # Test Fireworks
        fw_result = test_fireworks_transcriber(audio_chunks, audio_raw)
        if fw_result:
            fireworks_results.append(fw_result)
        
        # Test OpenAI
        oa_result = test_openai_transcriber(audio_chunks, audio_raw)
        if oa_result:
            openai_results.append(oa_result)
        
        # Small delay between tests
        if i < num_tests - 1:
            time.sleep(1)
    
    return fireworks_results, openai_results

def analyze_results(fireworks_results, openai_results):
    """Analyze and compare the test results"""
    print("\\n" + "=" * 60)
    print("📊 COMPREHENSIVE COMPARISON RESULTS")
    print("=" * 60)
    
    if not fireworks_results and not openai_results:
        print("❌ No results to analyze. Check your API keys.")
        return
    
    # Performance Analysis
    print("\\n🏁 PERFORMANCE COMPARISON:")
    print("-" * 40)
    
    if fireworks_results:
        fw_times = [r['total_time'] for r in fireworks_results if r['success']]
        fw_api_times = [r['api_call'] for r in fireworks_results if r['success']]
        if fw_times:
            print(f"🚀 Fireworks AI (Optimized):")
            print(f"   Total time: {statistics.mean(fw_times):.0f}ms avg ({min(fw_times):.0f}-{max(fw_times):.0f}ms range)")
            print(f"   API time: {statistics.mean(fw_api_times):.0f}ms avg")
            print(f"   Buffer creation: ~{statistics.mean([r.get('buffer_creation', 0) for r in fireworks_results]):.1f}ms avg")
    
    if openai_results:
        oa_times = [r['total_time'] for r in openai_results if r['success']]
        oa_api_times = [r['api_call'] for r in openai_results if r['success']]
        if oa_times:
            print(f"\\n🤖 OpenAI (Original):")
            print(f"   Total time: {statistics.mean(oa_times):.0f}ms avg ({min(oa_times):.0f}-{max(oa_times):.0f}ms range)")
            print(f"   API time: {statistics.mean(oa_api_times):.0f}ms avg")
            print(f"   File creation: ~{statistics.mean([r.get('file_creation', 0) for r in openai_results]):.1f}ms avg")
    
    # Speed Comparison
    if fw_times and oa_times:
        fw_avg = statistics.mean(fw_times)
        oa_avg = statistics.mean(oa_times)
        if fw_avg < oa_avg:
            improvement = ((oa_avg - fw_avg) / oa_avg) * 100
            faster = oa_avg - fw_avg
            print(f"\\n🎯 SPEED WINNER: Fireworks AI")
            print(f"   {improvement:.1f}% faster ({faster:.0f}ms saved on average)")
        else:
            improvement = ((fw_avg - oa_avg) / fw_avg) * 100
            faster = fw_avg - oa_avg
            print(f"\\n🎯 SPEED WINNER: OpenAI")
            print(f"   {improvement:.1f}% faster ({faster:.0f}ms saved on average)")
    
    # Accuracy Analysis
    print("\\n📝 TRANSCRIPTION QUALITY:")
    print("-" * 40)
    
    if fireworks_results:
        fw_texts = [r['transcribed_text'] for r in fireworks_results if r['success'] and 'transcribed_text' in r]
        if fw_texts:
            print("🚀 Fireworks AI outputs:")
            for i, text in enumerate(fw_texts, 1):
                print(f"   {i}: \"{text}\"")
    
    if openai_results:
        oa_texts = [r['transcribed_text'] for r in openai_results if r['success'] and 'transcribed_text' in r]
        if oa_texts:
            print("\\n🤖 OpenAI outputs:")
            for i, text in enumerate(oa_texts, 1):
                print(f"   {i}: \"{text}\"")
    
    # Success Rate Analysis
    print("\\n✅ RELIABILITY:")
    print("-" * 40)
    
    if fireworks_results:
        fw_success_rate = len([r for r in fireworks_results if r['success']]) / len(fireworks_results) * 100
        print(f"🚀 Fireworks AI: {fw_success_rate:.0f}% success rate ({len([r for r in fireworks_results if r['success']])}/{len(fireworks_results)})")
    
    if openai_results:
        oa_success_rate = len([r for r in openai_results if r['success']]) / len(openai_results) * 100
        print(f"🤖 OpenAI: {oa_success_rate:.0f}% success rate ({len([r for r in openai_results if r['success']])}/{len(openai_results)})")
    
    # Cost Analysis (rough estimates)
    print("\\n💰 ESTIMATED COST COMPARISON:")
    print("-" * 40)
    print("🚀 Fireworks AI: FREE tier available, then ~$0.20/hour")
    print("🤖 OpenAI: ~$0.006 per minute of audio (~$0.36/hour)")
    print("💡 For heavy usage, Fireworks AI is significantly cheaper")

def check_prerequisites():
    """Check if both API keys are available"""
    fireworks_key = os.getenv('FIREWORKS_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print("🔑 API Key Check:")
    print(f"   Fireworks AI: {'✅ Found' if fireworks_key and fireworks_key != 'your-api-key-here' else '❌ Missing'}")
    print(f"   OpenAI: {'✅ Found' if openai_key and openai_key != 'your-api-key-here' else '❌ Missing'}")
    
    if not fireworks_key and not openai_key:
        print("\\n❌ No API keys found! Add them to your .env file:")
        print("   FIREWORKS_API_KEY=your-fireworks-key")
        print("   OPENAI_API_KEY=your-openai-key")
        return False
    elif not fireworks_key or fireworks_key == 'your-api-key-here':
        print("\\n⚠️ Only OpenAI key found. Will test OpenAI only.")
    elif not openai_key or openai_key == 'your-api-key-here':
        print("\\n⚠️ Only Fireworks key found. Will test Fireworks only.")
    else:
        print("\\n✅ Both API keys found. Will test both services.")
    
    return True

def main():
    """Run the comprehensive comparison"""
    print("🥊 FIREWORKS vs OPENAI TRANSCRIBER COMPARISON")
    print("=" * 60)
    
    if not check_prerequisites():
        return
    
    print("\\n🎵 Test Setup:")
    print("   • Audio: 3-second generated sine wave")
    print("   • Sample rate: 16kHz (Whisper native)")
    print("   • Format: 16-bit mono WAV")
    print("   • Tests: 3 iterations for statistical accuracy")
    
    # Run the tests
    fireworks_results, openai_results = run_multiple_tests(num_tests=3)
    
    # Analyze results
    analyze_results(fireworks_results, openai_results)
    
    print("\\n" + "=" * 60)
    print("🎯 RECOMMENDATION:")
    
    fw_success = len([r for r in fireworks_results if r.get('success')]) if fireworks_results else 0
    oa_success = len([r for r in openai_results if r.get('success')]) if openai_results else 0
    
    if fw_success > 0 and oa_success > 0:
        fw_avg = statistics.mean([r['total_time'] for r in fireworks_results if r['success']])
        oa_avg = statistics.mean([r['total_time'] for r in openai_results if r['success']])
        
        if fw_avg < oa_avg:
            print("🚀 Use Fireworks AI for: Speed + Cost savings")
            print("🤖 Use OpenAI for: Maximum reliability + established service")
        else:
            print("🤖 Use OpenAI for: Speed + reliability")
            print("🚀 Use Fireworks AI for: Cost savings + free tier")
    elif fw_success > 0:
        print("🚀 Fireworks AI is working and available")
    elif oa_success > 0:
        print("🤖 OpenAI is working and available")
    else:
        print("❌ Neither service worked. Check API keys and network connection.")

if __name__ == "__main__":
    main()