#!/usr/bin/env python3
"""
IPC Handler for WisprFlow Lite Electron App
Handles communication between Electron main process and Python voice transcriber.
"""

import json
import sys
import threading
import time
from typing import Dict, Any, Optional
import logging

# Configure logging for IPC
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - IPC - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/wisprflow_ipc.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class IPCHandler:
    """Handles IPC communication with Electron main process"""
    
    def __init__(self, voice_transcriber):
        self.transcriber = voice_transcriber
        self.running = True
        self.input_thread = None
        
    def start(self):
        """Start the IPC communication loop"""
        logger.info("Starting IPC handler")
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
    def stop(self):
        """Stop the IPC handler"""
        self.running = False
        logger.info("Stopping IPC handler")
        
    def send_message(self, message_type: str, data: Dict[str, Any] = None):
        """Send a message to Electron main process"""
        message = {
            'type': message_type,
            'timestamp': time.time(),
            **(data or {})
        }
        
        try:
            json_message = json.dumps(message)
            print(json_message, flush=True)  # Send to stdout for Electron to read
            logger.debug(f"Sent message: {message_type}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    
    def _input_loop(self):
        """Listen for commands from Electron main process"""
        logger.info("Started input loop")
        
        while self.running:
            try:
                # Read from stdin (non-blocking with timeout)
                line = sys.stdin.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                    
                line = line.strip()
                if not line:
                    continue
                    
                try:
                    command = json.loads(line)
                    self._handle_command(command)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {line} - {e}")
                    self.send_message('error', {'message': 'Invalid JSON command'})
                    
            except Exception as e:
                logger.error(f"Error in input loop: {e}")
                if not self.running:
                    break
                time.sleep(0.1)
    
    def _handle_command(self, command: Dict[str, Any]):
        """Handle a command received from Electron"""
        cmd_type = command.get('command')
        logger.info(f"Received command: {cmd_type}")
        
        try:
            if cmd_type == 'start_recording':
                self._handle_start_recording()
            elif cmd_type == 'stop_recording':
                self._handle_stop_recording()
            elif cmd_type == 'configure':
                self._handle_configure(command.get('config', {}))
            elif cmd_type == 'get_status':
                self._handle_get_status()
            else:
                logger.warning(f"Unknown command: {cmd_type}")
                self.send_message('error', {'message': f'Unknown command: {cmd_type}'})
                
        except Exception as e:
            logger.error(f"Error handling command {cmd_type}: {e}")
            self.send_message('error', {'message': str(e)})
    
    def _handle_start_recording(self):
        """Handle start recording command"""
        if self.transcriber.is_recording:
            self.send_message('error', {'message': 'Already recording'})
            return
            
        try:
            self.transcriber.start_recording()
            self.send_message('recording_started')
        except Exception as e:
            self.send_message('error', {'message': f'Failed to start recording: {e}'})
    
    def _handle_stop_recording(self):
        """Handle stop recording command"""
        if not self.transcriber.is_recording:
            self.send_message('error', {'message': 'Not recording'})
            return
            
        try:
            self.transcriber.stop_recording()
            self.send_message('recording_stopped')
        except Exception as e:
            self.send_message('error', {'message': f'Failed to stop recording: {e}'})
    
    def _handle_configure(self, config: Dict[str, Any]):
        """Handle configuration update"""
        try:
            # Update transcriber configuration
            if 'api_key' in config:
                self.transcriber.client.api_key = config['api_key']
            if 'language' in config:
                self.transcriber.language = config['language']
            if 'max_recording_time' in config:
                self.transcriber.record_seconds = int(config['max_recording_time'])
            if 'typing_speed' in config:
                # Store typing speed for later use
                self.transcriber.typing_interval = float(config['typing_speed'])
            
            logger.info("Configuration updated")
            self.send_message('configured', {'status': 'success'})
            
        except Exception as e:
            self.send_message('error', {'message': f'Configuration error: {e}'})
    
    def _handle_get_status(self):
        """Handle get status command"""
        try:
            status = {
                'recording': self.transcriber.is_recording,
                'language': self.transcriber.language,
                'max_recording_time': self.transcriber.record_seconds,
                'audio_initialized': hasattr(self.transcriber, 'audio') and self.transcriber.audio is not None
            }
            self.send_message('status', status)
        except Exception as e:
            self.send_message('error', {'message': f'Status error: {e}'})
    
    def on_transcription_complete(self, text: str, duration: Optional[float] = None):
        """Called when transcription is complete"""
        self.send_message('transcription_complete', {
            'text': text,
            'duration': duration
        })
    
    def on_recording_started(self):
        """Called when recording starts"""
        self.send_message('recording_started')
    
    def on_recording_stopped(self):
        """Called when recording stops"""  
        self.send_message('recording_stopped')
    
    def on_error(self, error_message: str):
        """Called when an error occurs"""
        self.send_message('error', {'message': error_message})