# 🎙️ WisprFlow Lite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![OpenAI](https://img.shields.io/badge/OpenAI-Whisper-green.svg)](https://platform.openai.com/)
[![Platform](https://img.shields.io/badge/platform-macOS%20|%20Linux%20|%20Windows-lightgrey.svg)](https://github.com/tommyyau/wispr-flow-lite)

A powerful voice-to-text transcription app that works system-wide. Simply hold down the Option/Alt key while speaking, and release it to have your words transcribed directly where your cursor is positioned. Built with OpenAI's Whisper API for high-quality transcription.

<p align="center">
  <img src="https://raw.githubusercontent.com/tommyyau/wispr-flow-lite/main/docs/demo.gif" alt="WisprFlow Lite Demo">
</p>

## ✨ Features

- 🎯 **Push-to-Talk** - Hold Option key to record, release to transcribe
- 🎤 **High-quality transcription** - Uses OpenAI Whisper API
- 🧹 **Smart text cleaning** - Removes filler words (um, uh, etc.)
- 📝 **Direct typing** - Text appears where your cursor is
- ⚡ **Fast processing** - Quick transcription and typing
- 🌍 **Multi-language** - Supports 100+ languages
- 🔧 **Customizable** - Configure language, filler words, and more
- 🔄 **Robust Error Handling** - Automatic retries for API calls and better resource management
- 📊 **Memory Management** - Prevents crashes during long recordings
- 🔍 **Advanced Logging** - Better error tracking and debugging

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- OpenAI API key
- macOS, Linux, or Windows
- For macOS: Homebrew (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tommyyau/wispr-flow-lite.git
   cd wispr-flow-lite
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate it (macOS/Linux)
   source venv/bin/activate

   # Install packages
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy example configuration
   cp .env_example .env
   
   # Edit .env with your settings
   nano .env  # or use any text editor
   ```

4. **Set up permissions (macOS only)**
   
   Go to System Settings > Privacy & Security > Privacy and enable:
   - Microphone
   - Accessibility
   - Input Monitoring

   For detailed permission setup, see [macOS Setup Guide](docs/macos-setup.md)

### Usage

1. **Start the app**
   ```bash
   source venv/bin/activate && python voice_transcriber.py
   ```

2. **Basic controls**
   - Hold Option/Alt key to record
   - Release to transcribe
   - Ctrl+C to quit

For detailed usage instructions and configuration options, see our [User Guide](docs/user-guide.md).

## 💰 Cost & Privacy

- OpenAI Whisper API: $0.006 per minute
- No audio stored locally
- Data sent to OpenAI for transcription
- Monitor usage: [OpenAI Dashboard](https://platform.openai.com/usage)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for the Whisper API
- Original WisprFlow app for inspiration
- All contributors and users

---

**Made with ❤️ by [Tommy Yau](https://github.com/tommyyau)**