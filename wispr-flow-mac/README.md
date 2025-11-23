# Wispr Flow Lite - macOS Native App

Native macOS application for voice dictation using Fireworks AI's Whisper V3 Turbo.

## Features

- 🎙️ **Press-and-hold dictation** - Hold Option key to record
- ⚡ **Lightning-fast transcription** - Powered by Fireworks AI Whisper V3 Turbo
- 💬 **Auto text injection** - Transcribed text appears where your cursor is
- 🎨 **Menu bar app** - Minimal UI, maximum productivity
- 🔒 **Privacy-focused** - Runs locally on your Mac

## Building

```bash
# Build the app
./build_app.sh

# The app will be created as "Wispr Flow Lite.app"
# Drag it to your Applications folder
```

## Usage

1. **Launch the app** - It will appear in your menu bar
2. **Set your Fireworks API Key**
   - Click the menu bar icon → Settings
   - Paste your API key
3. **Grant permissions**
   - Microphone access (for recording)
   - Accessibility access (for global hotkey and text injection)
4. **Start dictating!**
   - Hold the Option key and speak
   - Release to transcribe
   - Text will appear at your cursor

## Requirements

- macOS 13.0 or later
- Fireworks AI API key ([get one here](https://fireworks.ai))

## Debug Logs

Logs are saved to `~/Documents/wispr_flow_debug.log` for troubleshooting.

## Architecture

- **Swift + SwiftUI** - Native macOS implementation
- **AVFoundation** - Audio recording
- **CGEvent API** - Global hotkey monitoring and text injection
- **URLSession** - Fireworks AI API integration

## License

MIT License - See parent directory for full license text.
