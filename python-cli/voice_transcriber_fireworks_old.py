#!/usr/bin/env python3
"""
Voice-to-Text Transcription App - Fireworks AI Version
A system-wide voice dictation tool that transcribes speech using Fireworks AI's Whisper Turbo model.

Features:
- Global hotkey (Option/Alt) to start/stop recording
- Transcribes speech using Fireworks AI Whisper Turbo API
- Types text directly at cursor position
- Removes filler words (um, uh, er, etc.)
- Cross-platform support (Windows, macOS, Linux)

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
import re
import tempfile
import wave
import io
from pathlib import Path
from dotenv import load_dotenv
from pynput import keyboard
import logging

# Load environment variables first
load_dotenv()

# Configure logging based on performance settings
debug_logging = os.getenv('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true'
performance_mode = os.getenv('PERFORMANCE_MODE', 'true').lower() == 'true'

if performance_mode and not debug_logging:
    logging.basicConfig(level=logging.ERROR, format='%(message)s')  # Minimal logging
elif debug_logging:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_WAIT_SECONDS = 2

def get_input_device():
    """Find the best available input device"""
    audio = None
    try:
        audio = pyaudio.PyAudio()
        default_input = audio.get_default_input_device_info()
        logger.info(f"🎤 Using input device: {default_input['name']}")
        return default_input['index']
    except Exception as e:
        logger.warning(f"⚠️ Warning: Could not get default input device: {e}")
        # Try to find any working input device
        if audio:
            for i in range(audio.get_device_count()):
                try:
                    device_info = audio.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:
                        logger.info(f"🎤 Using alternative input device: {device_info['name']}")
                        return i
                except Exception as dev_e:
                    logger.debug(f"Failed to check device {i}: {dev_e}")
                    continue
        return None
    finally:
        if audio:
            try:
                audio.terminate()
            except Exception as e:
                logger.error(f"Failed to terminate PyAudio: {e}")

class VoiceTranscriber:
    def __init__(self):
        # Initialize Fireworks API key
        api_key = os.getenv('FIREWORKS_API_KEY')
        if not api_key or api_key == 'your-api-key-here':
            logger.error("❌ Fireworks API key not found!")
            print("Please set your API key in the .env file:")
            print("FIREWORKS_API_KEY=your-actual-api-key-here")
            sys.exit(1)
            
        self.api_key = api_key
        self.api_endpoint = "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions"
        
        # Create persistent HTTP session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        
        # Audio recording settings (optimized for speed)
        self.chunk = int(os.getenv('CHUNK_SIZE', 4096))  # Larger chunks for efficiency
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = int(os.getenv('SAMPLE_RATE', 16000))  # Whisper's native sample rate
        self.record_seconds = int(os.getenv('MAX_RECORDING_TIME', 30))
        
        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.audio = None
        self.stream = None
        self.temp_files = set()  # Track temporary files
        
        # Initialize audio with retry
        self._initialize_audio()
        
        # Using Globe/Fn key as hotkey
        self.using_globe_key = True
        self.globe_pressed = False
        
        # Language setting
        self.language = os.getenv('LANGUAGE', 'en')
        
        # Keyboard listener
        self.keyboard_listener = None
        
        # Filler words to remove
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'so', 'well',
            'hmm', 'okay', 'right', 'actually', 'basically', 'literally',
            'i mean', 'sort of', 'kind of', 'you see'
        }
        
        # Add custom filler words from config
        custom_fillers = os.getenv('CUSTOM_FILLER_WORDS', '')
        if custom_fillers:
            custom_list = [word.strip() for word in custom_fillers.split(',')]
            self.filler_words.update(custom_list)
            
        # Pre-compile regex patterns for performance
        self._compile_text_patterns()
        
        logger.info(f"🎙️ Voice Transcriber (Fireworks AI) initialized")
        logger.info(f"📋 Hotkey: Globe/Fn key")
        logger.info(f"🌍 Language: {self.language}")
        logger.info(f"⏱️ Max recording time: {self.record_seconds}s")
        logger.info(f"🚀 Using Fireworks AI Whisper Turbo model")

    def _compile_text_patterns(self):
        """Pre-compile regex patterns for faster text processing"""
        # Create regex pattern for filler word removal
        if self.filler_words:
            # Sort by length (longest first) to handle multi-word fillers
            sorted_fillers = sorted(self.filler_words, key=len, reverse=True)
            # Escape special regex characters and create word boundaries
            escaped_fillers = [re.escape(filler) for filler in sorted_fillers]
            pattern = r'\b(?:' + '|'.join(escaped_fillers) + r')\b'
            self.filler_pattern = re.compile(pattern, re.IGNORECASE)
        else:
            self.filler_pattern = None
            
        # Pre-compile other patterns for grammar improvement
        self.multiple_spaces_pattern = re.compile(r'\s+')
        self.space_before_punct_pattern = re.compile(r'\s+([.!?,:;])')
        self.period_capitalize_pattern = re.compile(r'(\. )([a-z])')
        self.i_word_pattern = re.compile(r'\bi\b')

    def _initialize_audio(self):
        """Initialize PyAudio with retry logic"""
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # Ensure any existing PyAudio instance is properly terminated
                if hasattr(self, 'audio') and self.audio:
                    try:
                        self.audio.terminate()
                        self.audio = None
                    except:
                        pass

                # Get input device with a fresh PyAudio instance
                self.input_device_index = get_input_device()
                if self.input_device_index is None:
                    raise Exception("No working input device found")

                # Create new PyAudio instance
                self.audio = pyaudio.PyAudio()
                
                # Test audio setup with proper cleanup
                test_stream = None
                try:
                    test_stream = self.audio.open(
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        input=True,
                        input_device_index=self.input_device_index,
                        frames_per_buffer=self.chunk,
                        start=False
                    )
                    # Test if stream can actually start
                    test_stream.start_stream()
                    test_stream.stop_stream()
                except Exception as e:
                    if test_stream:
                        try:
                            test_stream.close()
                        except:
                            pass
                    raise e
                finally:
                    if test_stream:
                        try:
                            test_stream.close()
                        except:
                            pass
                return
            except Exception as e:
                retry_count += 1
                logger.warning(f"Failed to initialize audio (attempt {retry_count}/{MAX_RETRIES}): {e}")
                if self.audio:
                    try:
                        self.audio.terminate()
                    except:
                        pass
                    self.audio = None
                if retry_count < MAX_RETRIES:
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    logger.error("❌ Failed to initialize audio after multiple attempts")
                    raise

    def clean_text(self, text):
        """Remove filler words and clean up the transcribed text (optimized)"""
        if not text:
            return ""
            
        # Remove filler words if enabled (using pre-compiled regex)
        remove_fillers = os.getenv('REMOVE_FILLER_WORDS', 'true').lower() == 'true'
        if remove_fillers and self.filler_pattern:
            text = self.filler_pattern.sub('', text)
        
        # Basic grammar improvements using pre-compiled patterns
        text = self.improve_grammar(text)
        
        return text
    
    def improve_grammar(self, text):
        """Basic grammar improvements (optimized with pre-compiled patterns)"""
        if not text:
            return ""
            
        # Fix common spacing issues using pre-compiled patterns
        text = self.multiple_spaces_pattern.sub(' ', text)  # Multiple spaces to single space
        text = self.space_before_punct_pattern.sub(r'\1', text)  # Remove space before punctuation
        
        # Capitalize after periods using pre-compiled pattern
        text = self.period_capitalize_pattern.sub(lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Capitalize 'I' using pre-compiled pattern
        text = self.i_word_pattern.sub('I', text)
        
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        return text.strip()
    
    def start_recording(self):
        """Start recording audio"""
        # Start recording in a separate thread
        recording_thread = threading.Thread(target=self._record_audio)
        recording_thread.daemon = True
        recording_thread.start()

    def _record_audio(self):
        """Internal method to handle the actual recording"""
        try:
            # Clean up any existing stream first
            self._cleanup_stream()

            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.input_device_index,
                frames_per_buffer=self.chunk
            )
            
            self.is_recording = True
            self.audio_frames = []
            self.recording_start_time = time.perf_counter()  # Track recording start time
            
            logger.info("🎤 Recording... Release Globe/Fn key when done.")
            
            start_time = time.time()
            last_device_check = time.time()
            estimated_memory = 0
            max_memory_mb = float(os.getenv('MAX_MEMORY_MB', 100))  # Default 100MB limit
            
            # Record in chunks
            while self.is_recording:
                try:
                    # Periodic device check (every 2 seconds)
                    current_time = time.time()
                    if current_time - last_device_check > 2:
                        if not self._check_device_available():
                            logger.error("❌ Audio device became unavailable")
                            break
                        last_device_check = current_time

                    # Check if stream is still active
                    if not self.stream.is_active():
                        logger.error("❌ Audio stream became inactive")
                        break

                    # Read audio data
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    self.audio_frames.append(data)
                    
                    # Estimate memory usage (2 bytes per sample)
                    chunk_memory = len(data)
                    estimated_memory += chunk_memory
                    if estimated_memory > max_memory_mb * 1024 * 1024:
                        logger.warning(f"⚠️ Memory limit reached ({max_memory_mb}MB)")
                        break
                    
                    # Check for maximum recording time
                    if time.time() - start_time > self.record_seconds:
                        logger.info(f"⏰ Maximum recording time ({self.record_seconds}s) reached")
                        break
                        
                except Exception as e:
                    logger.error(f"Error reading audio: {e}")
                    # Try to recover from transient errors
                    if "Input overflowed" in str(e):
                        logger.warning("⚠️ Input overflow detected, continuing recording")
                        continue
                    break
                
        except Exception as e:
            logger.error(f"❌ Error during recording: {e}")
            if "Invalid sample rate" in str(e):
                logger.info("💡 Try adjusting the sample rate in your .env file")
            elif "Device unavailable" in str(e):
                logger.info("💡 Check your microphone connection and permissions")
        finally:
            self._cleanup_stream()

    def _check_device_available(self):
        """Check if the audio device is still available"""
        try:
            audio = pyaudio.PyAudio()
            device_info = audio.get_device_info_by_index(self.input_device_index)
            audio.terminate()
            return device_info['maxInputChannels'] > 0
        except:
            return False

    def _cleanup_stream(self):
        """Clean up the audio stream with proper error handling"""
        if hasattr(self, 'stream') and self.stream:
            try:
                if self.stream.is_active():
                    self.stream.stop_stream()
                time.sleep(0.1)  # Give time for the stream to fully stop
                self.stream.close()
            except Exception as e:
                logger.debug(f"Error during stream cleanup: {e}")
            finally:
                self.stream = None

    def stop_recording(self):
        """Stop recording audio"""
        stop_time = time.perf_counter()
        
        # Set flag first to stop recording loop
        self.is_recording = False
        
        # Give time for recording loop to finish
        time.sleep(0.2)
        
        # Clean up stream
        self._cleanup_stream()

        if not self.audio_frames:
            logger.warning("⚠️ No audio data recorded")
            return

        # Calculate recording duration and data size
        if hasattr(self, 'recording_start_time'):
            recording_duration = stop_time - self.recording_start_time
            audio_size = sum(len(frame) for frame in self.audio_frames)
            logger.info(f"📊 Recording stats: {recording_duration:.1f}s duration, {audio_size} bytes, {len(self.audio_frames)} chunks")

        # Process the recording in a separate thread
        processing_thread = threading.Thread(target=self._process_audio)
        processing_thread.daemon = True
        processing_thread.start()

    def _process_audio(self):
        """Process the recorded audio with detailed timing"""
        process_start = time.perf_counter()
        try:
            # Create in-memory audio buffer
            buffer_start = time.perf_counter()
            audio_data = self.create_audio_buffer()
            buffer_time = (time.perf_counter() - buffer_start) * 1000
            
            if not audio_data:
                logger.error("❌ Failed to create audio buffer")
                return

            logger.info(f"📊 Audio buffer created in {buffer_time:.1f}ms")

            # Transcribe audio
            transcribe_start = time.perf_counter()
            logger.info("🔄 Transcribing audio with Fireworks AI...")
            text = self.transcribe_audio(audio_data)
            transcribe_time = (time.perf_counter() - transcribe_start) * 1000
            
            if not text:
                logger.warning("⚠️ No text transcribed")
                return

            logger.info(f"📊 Transcription completed in {transcribe_time:.0f}ms")

            # Clean up the text
            clean_start = time.perf_counter()
            cleaned_text = self.clean_text(text)
            clean_time = (time.perf_counter() - clean_start) * 1000
            
            logger.info(f"📊 Text cleaning completed in {clean_time:.1f}ms")
            
            # Type the text
            if cleaned_text:
                type_start = time.perf_counter()
                self.type_text(cleaned_text)
                type_time = (time.perf_counter() - type_start) * 1000
                logger.info(f"📊 Text typing completed in {type_time:.0f}ms")
            else:
                logger.warning("⚠️ No text to type after cleaning")

            # Total processing time
            total_time = (time.perf_counter() - process_start) * 1000
            logger.info(f"🏁 Total processing time: {total_time:.0f}ms")
            logger.info(f"📈 Transcribed: '{cleaned_text[:50]}{'...' if len(cleaned_text) > 50 else ''}'")

        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
        finally:
            # No file cleanup needed since we use in-memory buffers
            pass
    
    def transcribe_audio(self, audio_data):
        """Transcribe audio data using Fireworks AI Whisper API with retry logic"""
        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                # Measure API call time
                api_start = time.perf_counter()
                
                # Use in-memory audio data directly with persistent session
                response = self.session.post(
                    self.api_endpoint,
                    files={"file": ("audio.wav", io.BytesIO(audio_data), "audio/wav")},
                    data={
                        "model": "whisper-v3-turbo",
                        "temperature": "0",
                        "vad_model": "silero",
                        "language": self.language if self.language != 'auto' else None
                    }
                )
                
                api_time = (time.perf_counter() - api_start) * 1000
                logger.info(f"📊 API call completed in {api_time:.0f}ms")

                if response.status_code == 200:
                    result = response.json()
                    text = result.get('text', '')
                    logger.info(f"📊 Response size: {len(response.content)} bytes, text length: {len(text)} chars")
                    return text
                else:
                    error_msg = f"API Error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    
                    # Handle specific error codes
                    if response.status_code == 401:
                        logger.error("❌ Invalid API key. Please check your FIREWORKS_API_KEY")
                        return None
                    elif response.status_code == 429:
                        logger.warning("⚠️ Rate limit exceeded. Waiting before retry...")
                        time.sleep(RETRY_WAIT_SECONDS * (retry_count + 1))
                    
                    retry_count += 1
                    if retry_count >= MAX_RETRIES:
                        return None
                        
            except Exception as e:
                logger.error(f"Error during transcription (attempt {retry_count + 1}/{MAX_RETRIES}): {e}")
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    time.sleep(RETRY_WAIT_SECONDS)
                else:
                    return None
        
        return None
    
    def create_audio_buffer(self):
        """Create in-memory audio buffer instead of temporary file"""
        if not self.audio_frames:
            return None

        try:
            # Create in-memory WAV file
            audio_buffer = io.BytesIO()
            
            with wave.open(audio_buffer, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))
            
            # Get the WAV data as bytes
            audio_buffer.seek(0)
            return audio_buffer.getvalue()
        except Exception as e:
            logger.error(f"Error creating audio buffer: {e}")
            return None
    
    def type_text(self, text):
        """Type the transcribed text at the current cursor position (optimized)"""
        try:
            # Reduced delay for faster response
            time.sleep(0.02)
            
            # Get typing interval from config (faster default)
            interval = float(os.getenv('TYPING_INTERVAL', 0.005))
            
            # Type the text
            pyautogui.write(text, interval=interval)
            
        except Exception as e:
            print(f"❌ Error typing text: {e}")
            print("💡 Make sure to click in a text field before recording")
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            # Check for Globe key (Fn key) - multiple detection methods
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
                # Start recording immediately
                self.start_recording()
                
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle key release events"""
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
            
            if globe_key_released:
                self.globe_pressed = False
                # Stop recording and process immediately
                self.stop_recording()
                
        except AttributeError:
            pass
    
    def run(self):
        """Main loop - listen for hotkey"""
        try:
            # Start keyboard listener with both press and release handlers
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release
            )
            self.keyboard_listener.start()
            
            print(f"🎯 Ready! Press and hold Globe/Fn key (or Right Cmd/F13) to record, release to transcribe.")
            print("💡 Note: If Globe key doesn't work, try Right Command or F13 key")
            print("💡 Position your cursor where you want text to appear")
            print("⏹️ Press Ctrl+C to quit")
            print("🚀 Using Fireworks AI Whisper Turbo model")
            print()
            
            # Keep the program running
            self.keyboard_listener.join()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
        except Exception as e:
            print(f"❌ Error: {e}")
            if "permissions" in str(e).lower():
                self.print_permission_help()
        finally:
            self.cleanup()
    
    def print_permission_help(self):
        """Print platform-specific permission help"""
        import platform
        system = platform.system()
        
        if system == "Darwin":  # macOS
            print("\n🍎 macOS Permission Required:")
            print("Go to System Preferences > Security & Privacy > Privacy")
            print("• Enable 'Microphone' access")
            print("• Enable 'Accessibility' access")
            print("• Enable 'Input Monitoring' access")
        elif system == "Linux":
            print("\n🐧 Linux Permission Required:")
            print("Add your user to the audio group:")
            print("sudo usermod -a -G audio $USER")
            print("Then logout and login again")
    
    def cleanup(self):
        """Clean up resources"""
        try:
            # Stop recording if still active
            if self.is_recording:
                self.is_recording = False
                time.sleep(0.2)  # Give recording thread time to stop

            # Clean up keyboard listener
            if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
                try:
                    self.keyboard_listener.stop()
                except:
                    pass

            # Clean up audio resources
            self._cleanup_stream()
            
            if hasattr(self, 'audio') and self.audio:
                try:
                    self.audio.terminate()
                except Exception as e:
                    logger.debug(f"Error terminating PyAudio: {e}")
                self.audio = None

            # Clean up HTTP session
            if hasattr(self, 'session') and self.session:
                try:
                    self.session.close()
                except Exception as e:
                    logger.debug(f"Error closing HTTP session: {e}")

            # Clean up temporary files
            if hasattr(self, 'temp_files'):
                for temp_file in self.temp_files:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            logger.debug(f"Removed temporary file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file {temp_file}: {e}")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass  # Suppress errors during interpreter shutdown

def check_dependencies():
    """Check if all required packages are installed"""
    required = ['requests', 'pyaudio', 'pynput', 'pyautogui']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)} python-dotenv")
        return False
    return True

if __name__ == "__main__":
    print("🎙️ Voice-to-Text Transcription App - Fireworks AI")
    print("================================================")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize and run
    try:
        transcriber = VoiceTranscriber()
        transcriber.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        sys.exit(1)