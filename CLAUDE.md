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

WisprFlow Lite is a voice-to-text transcription application built in Python that works system-wide. It uses OpenAI's Whisper API for transcription and provides push-to-talk functionality using the Option/Alt key.

## Core Architecture

### Main Application
- **`voice_transcriber.py`**: Single-file Python application containing the complete VoiceTranscriber class
- **Key components**:
  - Audio recording with PyAudio
  - OpenAI Whisper API integration 
  - Global keyboard listener using pynput
  - Text injection via pyautogui
  - Robust error handling and resource cleanup

### Configuration
- **`.env`**: Environment configuration (API keys, audio settings, text processing)
- **`.env_example`**: Template with all available configuration options
- **`requirements.txt`**: Python dependencies

## Common Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the voice transcriber
source venv/bin/activate && python voice_transcriber.py

# Using the installer script
python install.py
```

### Configuration Management
```bash
# Copy example configuration
cp .env_example .env

# Edit configuration
nano .env  # or any text editor
```

## Key Configuration Options

Essential settings in `.env`:
- `OPENAI_API_KEY`: Required OpenAI API key
- `LANGUAGE`: Transcription language (en, es, fr, auto, etc.)
- `SAMPLE_RATE`: Audio quality (16000 or 44100)
- `MAX_RECORDING_TIME`: Maximum recording duration in seconds
- `REMOVE_FILLER_WORDS`: Enable/disable filler word removal
- `TYPING_INTERVAL`: Delay between typed characters

## Platform-Specific Considerations

### macOS Requirements
- Microphone permissions required
- Accessibility permissions for keyboard monitoring
- Input Monitoring permissions for global hotkeys
- See `docs/macos-setup.md` for detailed permission setup

### Audio Device Management
The application includes sophisticated audio device detection and error handling:
- Automatic device selection with fallback options
- Resource cleanup with retry logic
- Memory management for long recordings

## Development Notes

### Error Handling Patterns
- Uses tenacity library for API retry logic
- Comprehensive resource cleanup in destructors
- Device availability monitoring during recording
- Graceful degradation when permissions are missing

### Code Structure
- Single-class design with clear separation of concerns
- Thread-safe audio recording and processing
- Temporary file management with automatic cleanup
- Configurable text processing pipeline

## Testing and Validation

No formal test suite exists. Manual testing involves:
- Verifying microphone permissions and audio device detection
- Testing transcription accuracy with various speech patterns
- Validating text injection across different applications
- Confirming proper resource cleanup after interruption