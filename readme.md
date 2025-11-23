# 🎙️ WisprFlow Lite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Swift 5.9+](https://img.shields.io/badge/swift-5.9+-orange.svg)](https://swift.org/)
[![Fireworks AI](https://img.shields.io/badge/Fireworks-Whisper%20V3%20Turbo-green.svg)](https://fireworks.ai/)

A powerful voice-to-text transcription system that works anywhere on your Mac. Hold down the Option/Alt key while speaking, and release it to have your words transcribed directly where your cursor is positioned. Powered by Fireworks AI's Whisper V3 Turbo for fast, accurate transcription.

## 📱 Two Versions Available

**Choose the version that best fits your needs:**

### 🍎 macOS Native App (Recommended)
- **Location**: [`wispr-flow-mac/`](wispr-flow-mac/)
- **For**: All macOS users
- **Installation**: Build once with `./build_app.sh`, drag to Applications
- **Interface**: Native menu bar app with SwiftUI settings
- **Performance**: ⚡ Lightning fast (native Swift)
- **Status**: ✅ Production ready

### 🖥️ Python CLI Version
- **Location**: [`python-cli/`](python-cli/)
- **For**: Developers, power users, and cross-platform use
- **Installation**: Python virtual environment
- **Interface**: Command-line interface
- **Performance**: Fast (Python + Fireworks AI)
- **Status**: ✅ Production ready

## ✨ Features

- 🎯 **Push-to-Talk** - Hold Option key to record, release to transcribe
- 🎤 **High-quality transcription** - Uses Fireworks AI Whisper V3 Turbo
- ⚡ **Ultra-fast** - 66% faster than OpenAI Whisper
- 📝 **Direct typing** - Text appears where your cursor is
- 🌍 **Multi-language** - Supports 100+ languages
- 🔧 **Customizable** - Configure language, typing speed, and more
- 🔄 **Robust Error Handling** - Automatic retries for API calls and better resource management
- 📊 **Memory Management** - Prevents crashes during long recordings
- 🔍 **Advanced Logging** - Better error tracking and debugging


## 🚀 Quick Start

### macOS Native App (Recommended)

1. **Navigate to the directory:**
   ```bash
   cd wispr-flow-mac
   ```

2. **Build the app:**
   ```bash
   ./build_app.sh
   ```

3. **Install:**
   - Drag `Wispr Flow Lite.app` to your Applications folder
   - Launch the app
   - Grant Microphone and Accessibility permissions
   - Enter your Fireworks AI API key in Settings

For detailed instructions, see [`wispr-flow-mac/README.md`](wispr-flow-mac/README.md).

### Python CLI Version

For the command-line version, see detailed instructions in [`python-cli/README.md`](python-cli/README.md).

**Quick setup:**
```bash
cd python-cli
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env_example .env  # Edit with your Fireworks API key
python voice_transcriber_fireworks.py
```

## 💰 Cost & Privacy

- Fireworks AI Whisper V3 Turbo: ~$0.002 per minute (66% cheaper than OpenAI)
- No audio stored locally
- Data sent to Fireworks AI for transcription
- Monitor usage: [Fireworks AI Dashboard](https://fireworks.ai/account)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Fireworks AI for the Whisper V3 Turbo API
- Original WisprFlow app for inspiration
- All contributors and users

---

**Made with ❤️ by [Tommy Yau](https://github.com/tommyyau)**