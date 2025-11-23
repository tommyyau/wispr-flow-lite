# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MANDATORY WORKFLOW - NO EXCEPTIONS

### BEFORE ANY WORK (BLOCKING REQUIREMENTS)
**🛑 STOP: Complete ALL steps below before any implementation**

- [ ] **MANDATORY**: Enter plan mode first (if not already)
- [ ] **MANDATORY**: Create TodoWrite with task tracking
- [ ] **MANDATORY**: Write detailed plan to `.claude/tasks/TASK_NAME.md`
  - Problem statement and root cause analysis
  - Detailed implementation plan with reasoning
  - Tasks broken down into specific steps
  - Success criteria and test plan
- [ ] **MANDATORY**: If task requires external knowledge, use Task tool for research
- [ ] **MANDATORY**: Keep plan focused (MVP approach, don't over-plan)
- [ ] **MANDATORY**: Use ExitPlanMode tool to request user approval
- [ ] **🛑 BLOCKING**: Do NOT proceed until user explicitly approves the plan

### WHILE IMPLEMENTING (REQUIRED UPDATES)
**These are NOT optional - MUST be done throughout work:**

- [ ] **MANDATORY**: Update TodoWrite tool with progress as you work
- [ ] **MANDATORY**: Update task document in `.claude/tasks/` with implementation details
- [ ] **MANDATORY**: Document any deviations from original plan with reasoning
- [ ] **MANDATORY**: Append detailed descriptions of each change for engineer handoff

### AFTER COMPLETING WORK (COMPLETION REQUIREMENTS)
**🛑 STOP: Complete ALL steps before considering task done**

- [ ] **MANDATORY**: Update task document with final results and test outcomes
- [ ] **MANDATORY**: Update TodoWrite to mark all tasks as completed
- [ ] **MANDATORY**: Update task status to ✅ COMPLETED in `.claude/tasks/TASK_NAME.md`
- [ ] **MANDATORY**: Verify all changes are documented for easy handoff to other engineers
- [ ] **MANDATORY**: Include file paths, line numbers, and rationale for all changes

### WORKFLOW ENFORCEMENT
**If you find yourself implementing without following this workflow:**
1. **IMMEDIATELY STOP** what you are doing
2. **CREATE** the missing task document
3. **DOCUMENT** what you've already done
4. **ASK FOR APPROVAL** before continuing
5. **FOLLOW** the complete workflow going forward

**No exceptions. No shortcuts. This ensures consistency and trackability.**

### SELF-MONITORING CHECKLIST

Before proceeding with ANY task, verify:

**Pre-Work Validation** (Before any implementation):
- [ ] I am in plan mode
- [ ] I have created a TodoWrite with this task
- [ ] I have written a plan to `.claude/tasks/TASK_NAME.md` using the template
- [ ] I have used ExitPlanMode to request approval
- [ ] The user has explicitly approved my plan
- [ ] I understand exactly what needs to be done

**Mid-Work Validation** (Check every 15 minutes):
- [ ] I am updating TodoWrite with my progress
- [ ] I am documenting changes in the task file as I make them
- [ ] I am following the approved plan (or documenting deviations)
- [ ] I can explain each change I'm making and why

**Post-Work Validation** (Before marking complete):
- [ ] All changes are documented with file paths and line numbers
- [ ] All TodoWrite tasks are marked completed
- [ ] Task status is updated to ✅ COMPLETED
- [ ] Another engineer could understand and continue my work
- [ ] I have tested the changes work as expected

**Emergency Stop Conditions**:
If ANY of these occur, IMMEDIATELY stop and follow the enforcement workflow:
- 🚨 I realize I'm implementing without a plan
- 🚨 I'm modifying code without documenting it
- 🚨 I can't remember what I'm supposed to be doing
- 🚨 The user hasn't approved my plan yet

## Project Overview

WisprFlow Lite is a dual-version voice-to-text transcription application that works system-wide. It uses OpenAI's Whisper API for transcription and provides push-to-talk functionality. The project offers both a Python CLI version for developers and an Electron GUI app for end users.

## Dual-Version Architecture

### Python CLI Version (`python-cli/`)
- **Status**: ✅ Ready to use
- **Target**: Developers and power users
- **Multiple stable versions available**:
  - `voice_transcriber_openai.py` - Original OpenAI implementation
  - `voice_transcriber_fireworks.py` - Fireworks AI integration with filler word removal (66% faster)
  - `voice_transcriber_fireworks_no_filler.py` - **RECOMMENDED** - Fireworks AI without text processing (66% faster, maximum stability)
- **Key components**:
  - Audio recording with PyAudio
  - Fireworks AI Whisper Turbo API integration 
  - Performance-optimized logging for maximum speed
  - Global keyboard listener using pynput
  - Text injection via pyautogui
  - Robust error handling and resource cleanup
  - Configuration via `.env` files

### Electron GUI App (`electron-app/`)
- **Status**: 🚧 In development
- **Target**: All users wanting a native Mac app
- **Architecture**: Electron wrapper around Python backend
- **Key files**:
  - `src/main/main.js`: Electron main process
  - `src/renderer/`: Frontend interface
  - `src/python/`: Python backend integration
  - IPC communication between Electron and Python processes

### Configuration Structure
- **Python CLI**: `.env` files in `python-cli/` directory
- **Electron app**: Configuration managed through GUI with backend `.env` generation
- **Template**: `.env_example` shows all available configuration options

## Common Development Commands

### Python CLI Version Development
```bash
# Navigate to Python CLI directory
cd python-cli

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies (includes VAD and MP3 support)
pip install -r requirements.txt

# Setup configuration
cp .env_example .env
# Edit .env with your Fireworks API key (FIREWORKS_API_KEY=your-key-here)

# Run the RECOMMENDED version (maximum stability)
python voice_transcriber_fireworks_no_filler.py

# Alternative versions:
python voice_transcriber_openai.py           # Original OpenAI version
python voice_transcriber_fireworks.py        # Fireworks with filler word removal
```

### Electron App Development
```bash
# Navigate to Electron app directory
cd electron-app

# Install Node.js dependencies
npm install

# Development mode (with hot reload)
npm run dev

# Build Python backend
npm run build-python

# Build complete application
npm run build

# Create distribution package
npm run dist
```

### Cross-Version Testing
```bash
# Test stable Python CLI from root
cd python-cli && source venv/bin/activate && python voice_transcriber_fireworks_no_filler.py

# Test other Python versions
cd python-cli && source venv/bin/activate && python voice_transcriber_fireworks.py

# Test Electron app from root
cd electron-app && npm run dev
```

## Key Configuration Options

Essential settings in `.env` (all versions):
- `FIREWORKS_API_KEY`: Required Fireworks AI API key (recommended)
- `OPENAI_API_KEY`: Required for OpenAI version only
- `LANGUAGE`: Transcription language (en, es, fr, auto, etc.)
- `HOTKEY`: Keyboard trigger - **Note**: Globe/Fn key is now default for all versions
- `SAMPLE_RATE`: Audio quality (16000 optimal for Whisper)
- `MAX_RECORDING_TIME`: Maximum recording duration in seconds (default: 30)
- `VAD_ENABLED`: Enable Voice Activity Detection (true recommended)
- `VAD_THRESHOLD`: VAD sensitivity (0.5 default, lower = more sensitive)
- `ENABLE_DEBUG_LOGGING`: Enable detailed logging (false for max performance)
- `PERFORMANCE_MODE`: Enable performance optimizations (true recommended)
- `REMOVE_FILLER_WORDS`: Enable/disable filler word removal
- `CUSTOM_FILLER_WORDS`: Additional filler words to remove
- `TYPING_INTERVAL`: Delay between typed characters (0.005 = very fast)
- `CHUNK_SIZE`: Audio chunk size (4096 optimal)

## Platform-Specific Considerations

### macOS Requirements (Critical for both versions)
Both Python CLI and Electron app require these system permissions:
- **Microphone access**: For audio recording
- **Accessibility permissions**: For keyboard monitoring and text injection
- **Input Monitoring permissions**: For global hotkey detection

**Setup**: See `docs/macos-setup.md` for detailed permission setup guide. Permissions must be granted to:
- Terminal.app (for CLI version)
- Python executable path (for CLI version)
- Electron app bundle (for GUI version)
- Any IDE being used for development (Cursor, VSCode, etc.)

### Audio Device Management
Both versions include sophisticated audio device detection:
- Automatic device selection with fallback options
- Resource cleanup with retry logic and delays
- Memory management for long recordings
- Graceful error handling for device unavailability

## Development Architecture Notes

### Python CLI Version (`python-cli/voice_transcriber.py`)
- **Pattern**: Single-class design with clear separation of concerns
- **Threading**: Thread-safe audio recording and processing
- **Memory**: Temporary file management with automatic cleanup
- **Error handling**: Uses tenacity library for API retry logic
- **Resources**: Comprehensive cleanup in destructors with device monitoring

### Electron GUI Version
- **Pattern**: Main process communicates with Python backend via IPC
- **Frontend**: HTML/CSS/JS renderer process
- **Backend**: Python integration through spawn processes
- **Build**: PyInstaller creates standalone Python executable
- **Distribution**: Electron-builder creates native macOS DMG

### Inter-Version Code Reuse
- Core transcription logic shared between versions
- Configuration management patterns consistent
- Error handling and retry logic unified
- Audio device detection algorithms identical

## Performance Comparison

### Speed Improvements by Version
| Version | Avg Response Time | Improvement | Best For |
|---------|------------------|-------------|----------|
| OpenAI Original | 2058ms | Baseline | OpenAI API required |
| Fireworks Basic | 693ms | 66% faster | Simple migration |
| **Fireworks + VAD** | **157-587ms** | **30-82% faster** | **All use cases (recommended)** |

### Benefits Summary
- **VAD Filtering**: Reduces API calls by 30-60% by skipping silence
- **Performance Logging**: Eliminates 20-50ms console I/O overhead
- **Combined**: Up to 15x faster than original OpenAI implementation
- **Cost Savings**: ~60% reduction in API costs through efficiency gains

### Performance Testing
```bash
# Test VAD performance with different silence levels
python test_vad_performance.py

# Compare all transcriber versions
python compare_transcribers.py

# Quick performance comparison
python quick_performance_test.py
```

## Testing and Validation

**Manual testing workflow**:
- Verify system permissions are properly configured
- Test microphone detection across different audio devices
- Validate transcription accuracy with various speech patterns and languages
- Test text injection across different applications (TextEdit, browsers, IDEs)
- Confirm proper resource cleanup after recording interruption
- Test configuration changes take effect without restart
- Validate hotkey combinations work globally
- Test memory management during extended recording sessions

**Platform testing**: Focus on macOS permission edge cases and audio device switching scenarios.