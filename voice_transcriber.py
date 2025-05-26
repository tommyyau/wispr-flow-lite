#!/usr/bin/env python3
"""
Voice-to-Text Transcription App
A system-wide voice dictation tool that transcribes speech directly to cursor position.
Similar to WisprFlow functionality using OpenAI Whisper.

Features:
- Global hotkey (Option/Alt) to start/stop recording
- Transcribes speech using OpenAI Whisper API
- Types text directly at cursor position
- Removes filler words (um, uh, er, etc.)
- Cross-platform support (Windows, macOS, Linux)

Requirements:
pip install openai pyaudio keyboard pyautogui pynput python-dotenv
"""

import os
import sys
import time
import threading
import pyaudio
from openai import OpenAI
import pyautogui
import re
import tempfile
import wave
from pathlib import Path
from dotenv import load_dotenv
from pynput import keyboard
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key or api_key == 'your-api-key-here':
            logger.error("❌ OpenAI API key not found!")
            print("Please set your API key in the .env file:")
            print("OPENAI_API_KEY=your-actual-api-key-here")
            sys.exit(1)
            
        self.client = OpenAI(api_key=api_key)
        
        # Audio recording settings
        self.chunk = int(os.getenv('CHUNK_SIZE', 2048))
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = int(os.getenv('SAMPLE_RATE', 16000))
        self.record_seconds = int(os.getenv('MAX_RECORDING_TIME', 30))
        
        # Recording state
        self.is_recording = False
        self.audio_frames = []
        self.audio = None
        self.stream = None
        self.temp_files = set()  # Track temporary files
        
        # Initialize audio with retry
        self._initialize_audio()
        
        # Using Option/Alt key as hotkey
        self.using_option_key = True
        self.option_pressed = False
        
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
        
        logger.info(f"🎙️ Voice Transcriber initialized")
        logger.info(f"📋 Hotkey: Option/Alt key")
        logger.info(f"🌍 Language: {self.language}")
        logger.info(f"⏱️ Max recording time: {self.record_seconds}s")

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
        """Remove filler words and clean up the transcribed text"""
        if not text:
            return ""
            
        # Convert to lowercase for processing
        words = text.lower().split()
        
        # Remove filler words if enabled
        remove_fillers = os.getenv('REMOVE_FILLER_WORDS', 'true').lower() == 'true'
        if remove_fillers:
            cleaned_words = []
            i = 0
            while i < len(words):
                word = words[i].strip('.,!?;:"()[]{}')
                
                # Check for multi-word fillers like "you know", "i mean"
                skip = False
                for filler_length in [3, 2, 1]:  # Check longer phrases first
                    if i + filler_length <= len(words):
                        phrase = ' '.join(words[i:i+filler_length]).strip('.,!?;:"()[]{}')
                        if phrase in self.filler_words:
                            i += filler_length
                            skip = True
                            break
                
                if not skip:
                    cleaned_words.append(words[i])
                    i += 1
            
            words = cleaned_words
        
        # Reconstruct text
        cleaned_text = ' '.join(words)
        
        # Basic grammar improvements
        cleaned_text = self.improve_grammar(cleaned_text)
        
        return cleaned_text
    
    def improve_grammar(self, text):
        """Basic grammar improvements"""
        if not text:
            return ""
            
        # Capitalize first letter
        text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Capitalize after periods
        text = re.sub(r'(\. )([a-z])', lambda m: m.group(1) + m.group(2).upper(), text)
        
        # Fix common spacing issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r'\s+([.!?,:;])', r'\1', text)  # Remove space before punctuation
        
        # Capitalize 'I'
        text = re.sub(r'\bi\b', 'I', text)
        
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
            
            logger.info("🎤 Recording... Release Option/Alt key when done.")
            
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
        # Set flag first to stop recording loop
        self.is_recording = False
        
        # Give time for recording loop to finish
        time.sleep(0.2)
        
        # Clean up stream
        self._cleanup_stream()

        if not self.audio_frames:
            logger.warning("⚠️ No audio data recorded")
            return

        # Process the recording in a separate thread
        processing_thread = threading.Thread(target=self._process_audio)
        processing_thread.daemon = True
        processing_thread.start()

    def _process_audio(self):
        """Process the recorded audio"""
        try:
            # Save audio to file
            audio_file = self.save_audio_to_file()
            if not audio_file:
                logger.error("❌ Failed to save audio file")
                return

            # Transcribe audio
            logger.info("🔄 Transcribing audio...")
            text = self.transcribe_audio(audio_file)
            
            if not text:
                logger.warning("⚠️ No text transcribed")
                return

            # Clean up the text
            cleaned_text = self.clean_text(text)
            
            # Type the text
            if cleaned_text:
                self.type_text(cleaned_text)
            else:
                logger.warning("⚠️ No text to type after cleaning")

        except Exception as e:
            logger.error(f"❌ Processing error: {e}")
        finally:
            # Cleanup is handled by the temp_files tracking system
            pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file using OpenAI Whisper API with retry logic"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.language
                )
                return transcript.text
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def save_audio_to_file(self):
        """Save recorded audio to a temporary file"""
        if not self.audio_frames:
            return None

        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            self.temp_files.add(temp_file.name)  # Track the temporary file

            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(self.audio_frames))

            return temp_file.name
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.remove(temp_file.name)
                except:
                    pass
            return None
    
    def type_text(self, text):
        """Type the transcribed text at the current cursor position"""
        try:
            # Small delay to ensure the cursor is ready
            time.sleep(0.1)
            
            # Get typing interval from config
            interval = float(os.getenv('TYPING_INTERVAL', 0.01))
            
            # Type the text
            pyautogui.write(text, interval=interval)
            
        except Exception as e:
            print(f"❌ Error typing text: {e}")
            print("💡 Make sure to click in a text field before recording")
    
    def on_press(self, key):
        """Handle key press events"""
        try:
            # Check if it's the Option/Alt key
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                if not self.option_pressed:
                    self.option_pressed = True
                    # Start recording immediately
                    self.start_recording()
        except AttributeError:
            pass

    def on_release(self, key):
        """Handle key release events"""
        try:
            # Check if it's the Option/Alt key
            if key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.option_pressed = False
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
            
            print(f"🎯 Ready! Press and hold Option/Alt key to record, release to transcribe.")
            print("💡 Position your cursor where you want text to appear")
            print("⏹️ Press Ctrl+C to quit")
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
    required = ['openai', 'pyaudio', 'pynput', 'pyautogui']
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
    print("🎙️ Voice-to-Text Transcription App")
    print("==================================")
    
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