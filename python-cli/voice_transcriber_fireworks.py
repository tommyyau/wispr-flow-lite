#!/usr/bin/env python3
"""
Voice-to-Text Transcription App - Fireworks AI (No Filler Word Processing)
Test version with filler word processing completely disabled to isolate segfault cause.

Features:
- Global hotkey (Globe/Fn key) to start/stop recording
- Transcribes speech using Fireworks AI Whisper Turbo API
- Types text directly at cursor position
- NO filler word removal (disabled to prevent segfaults)

Requirements:
pip install requests pyaudio keyboard pyautogui pynput python-dotenv
"""

import os
import sys
import time
import threading
import pyaudio
import requests
import pyautogui
import io
import wave
from dotenv import load_dotenv
from pynput import keyboard
import logging

# Load environment variables first
load_dotenv()

# Configure logging - minimal for stability
logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)

def get_input_device():
    """Find available input device"""
    audio = None
    try:
        audio = pyaudio.PyAudio()
        default_input = audio.get_default_input_device_info()
        print(f"🎤 Using input device: {default_input['name']}")
        return default_input['index']
    except Exception as e:
        print(f"Audio device error: {e}")
        return None
    finally:
        if audio:
            audio.terminate()

class VoiceTranscriberNoFiller:
    def __init__(self):
        # API setup
        api_key = os.getenv('FIREWORKS_API_KEY')
        if not api_key or api_key == 'your-api-key-here':
            print("❌ Fireworks API key not found!")
            print("Please set FIREWORKS_API_KEY in .env file")
            sys.exit(1)
            
        self.api_key = api_key
        self.api_endpoint = "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions"
        
        # Audio settings
        self.chunk = int(os.getenv('CHUNK_SIZE', 2048))
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = int(os.getenv('SAMPLE_RATE', 16000))
        self.record_seconds = int(os.getenv('MAX_RECORDING_TIME', 30))
        
        # State
        self.is_recording = False
        self.audio_frames = []
        self.audio = None
        self.globe_pressed = False
        
        # Language
        self.language = os.getenv('LANGUAGE', 'en')
        
        # Initialize audio
        self._init_audio()
        
        # HTTP session
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
        print("🎙️ Voice Transcriber (Fireworks AI - No Filler Processing)")
        print("🚫 Filler word removal DISABLED for stability testing")
        
    def _init_audio(self):
        """Initialize audio system"""
        try:
            self.audio = pyaudio.PyAudio()
            self.input_device = get_input_device()
            if self.input_device is None:
                raise Exception("No input device found")
        except Exception as e:
            print(f"Audio initialization failed: {e}")
            sys.exit(1)
    
    def start_recording(self):
        """Start recording"""
        if self.is_recording:
            return
            
        print("🎤 Recording...")
        self.is_recording = True
        self.audio_frames = []
        
        self.recording_thread = threading.Thread(target=self._record_audio)
        self.recording_thread.daemon = True
        self.recording_thread.start()
    
    def _record_audio(self):
        """Record audio in background"""
        stream = None
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
                input_device_index=self.input_device
            )
            
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    self.audio_frames.append(data)
                except:
                    break
                    
        except Exception as e:
            print(f"Recording error: {e}")
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
    
    def stop_recording(self):
        """Stop recording and process"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        print("⏹️ Processing...")
        
        # Wait for recording to finish
        if hasattr(self, 'recording_thread'):
            self.recording_thread.join(timeout=1.0)
        
        # Process audio in separate thread to avoid blocking
        processing_thread = threading.Thread(target=self._process_audio)
        processing_thread.daemon = True
        processing_thread.start()
    
    def _process_audio(self):
        """Process recorded audio - NO TEXT PROCESSING"""
        if not self.audio_frames:
            print("❌ No audio recorded")
            return
            
        try:
            # Create audio buffer
            audio_buffer = io.BytesIO()
            with wave.open(audio_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            audio_buffer.seek(0)
            audio_data = audio_buffer.getvalue()
            
            # Transcribe
            print("🔄 Transcribing...")
            text = self._transcribe(audio_data)
            
            if text and text.strip():
                # CRITICAL: NO TEXT PROCESSING - Direct output only
                print(f"📝 Raw transcription: '{text}'")
                
                # Type the raw text directly - NO FILLER WORD REMOVAL
                self._type_text(text.strip())
                print("✅ Text typed")
            else:
                print("❌ No transcription received")
                
        except Exception as e:
            print(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Ensure clean state for next recording
            self.audio_frames = []
            print("🎯 Ready for next recording...")
    
    def _transcribe(self, audio_data):
        """Send to Fireworks API"""
        try:
            files = {
                'file': ('audio.wav', io.BytesIO(audio_data), 'audio/wav')
            }
            
            data = {
                'model': 'whisper-v3-turbo',
                'response_format': 'text'
            }
            
            if self.language != 'auto':
                data['language'] = self.language
            
            response = self.session.post(
                self.api_endpoint,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.text.strip()
            else:
                print(f"API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
    
    def _type_text(self, text):
        """Type the transcribed text - NO PROCESSING"""
        try:
            time.sleep(0.1)  # Allow key release
            
            # Get typing speed
            interval = float(os.getenv('TYPING_INTERVAL', '0.01'))
            
            # Type raw text directly - NO FILLER WORD PROCESSING
            pyautogui.typewrite(text, interval=interval)
            
        except Exception as e:
            print(f"Typing error: {e}")
            import traceback
            traceback.print_exc()
    
    def on_press(self, key):
        """Handle key press"""
        try:
            # Check for Globe/Fn key - multiple detection methods
            globe_key_detected = False
            
            # Method 1: Direct Fn key detection (if available)
            if hasattr(keyboard.Key, 'fn') and key == keyboard.Key.fn:
                globe_key_detected = True
            
            # Method 2: String comparison for Fn key
            elif str(key) == 'Key.fn':
                globe_key_detected = True
                
            # Method 3: Virtual key code for Fn key (macOS specific)
            elif hasattr(key, 'vk') and key.vk == 179:
                globe_key_detected = True
                
            # Method 4: Right Command key as alternative (more reliable on macOS)
            elif key == keyboard.Key.cmd_r:
                globe_key_detected = True
                
            # Method 5: F13 key as alternative (often unmapped and available)
            elif hasattr(key, 'name') and key.name == 'f13':
                globe_key_detected = True
            
            if globe_key_detected and not self.globe_pressed:
                self.globe_pressed = True
                print(f"🔴 Key pressed (globe_pressed={self.globe_pressed}, is_recording={self.is_recording})")
                if not self.is_recording:
                    self.start_recording()
                
        except Exception as e:
            print(f"Key press error: {e}")
    
    def on_release(self, key):
        """Handle key release"""
        try:
            # Check for Globe key (Fn key) release - multiple detection methods
            globe_key_released = False
            
            # Method 1: Direct Fn key detection (if available)
            if hasattr(keyboard.Key, 'fn') and key == keyboard.Key.fn:
                globe_key_released = True
            
            # Method 2: String comparison for Fn key
            elif str(key) == 'Key.fn':
                globe_key_released = True
                
            # Method 3: Virtual key code for Fn key (macOS specific)
            elif hasattr(key, 'vk') and key.vk == 179:
                globe_key_released = True
                
            # Method 4: Right Command key as alternative (more reliable on macOS)
            elif key == keyboard.Key.cmd_r:
                globe_key_released = True
                
            # Method 5: F13 key as alternative (often unmapped and available)
            elif hasattr(key, 'name') and key.name == 'f13':
                globe_key_released = True
            
            if globe_key_released and self.globe_pressed:
                print(f"🟢 Key released (globe_pressed={self.globe_pressed}, is_recording={self.is_recording})")
                self.globe_pressed = False
                if self.is_recording:
                    self.stop_recording()
                    
        except Exception as e:
            print(f"Key release error: {e}")
    
    def run(self):
        """Main loop"""
        print("\n" + "=" * 60)
        print("🧪 TESTING VERSION - Filler word processing DISABLED")
        print("Press and hold Globe/Fn key (or Right Cmd) to record")
        print("Release to stop and transcribe")
        print("Text will include ALL words (um, uh, well, etc.)")
        print("Press Ctrl+C to exit")
        print("=" * 60)
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self.keyboard_listener.start()
        
        try:
            self.keyboard_listener.join()
        except KeyboardInterrupt:
            print("\n👋 Exiting...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            self.is_recording = False
            
            if hasattr(self, 'keyboard_listener'):
                self.keyboard_listener.stop()
            
            if hasattr(self, 'session'):
                self.session.close()
            
            if self.audio:
                time.sleep(0.1)
                self.audio.terminate()
                
        except Exception as e:
            print(f"Cleanup error: {e}")

def main():
    """Entry point"""
    try:
        app = VoiceTranscriberNoFiller()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        sys.exit(0)

if __name__ == "__main__":
    main()