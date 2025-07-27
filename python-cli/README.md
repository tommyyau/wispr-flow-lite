# WisprFlow Lite - Python CLI Version

This is the original command-line Python voice transcription application.

## Quick Start

1. **Setup Virtual Environment**:
   ```bash
   cd python-cli
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**:
   ```bash
   cp .env_example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run Application**:
   ```bash
   python voice_transcriber.py
   ```

## Usage

- Press and hold **Option/Alt key** to record
- Release to transcribe and type text
- Press **Ctrl+C** to quit

## macOS Permissions

The app requires these permissions:
- Microphone access
- Accessibility access (for typing text)
- Input Monitoring (for global hotkeys)

See `../docs/macos-setup.md` for detailed setup instructions.

## Configuration

Edit `.env` to customize:
- `OPENAI_API_KEY`: Your OpenAI API key
- `LANGUAGE`: Transcription language (en, es, fr, auto, etc.)
- `MAX_RECORDING_TIME`: Maximum recording duration
- `REMOVE_FILLER_WORDS`: Enable/disable filler word removal
- `TYPING_INTERVAL`: Speed of text typing

## Troubleshooting

- **No microphone detected**: Check microphone permissions
- **Global hotkey not working**: Enable Input Monitoring permissions
- **Text not typing**: Enable Accessibility permissions