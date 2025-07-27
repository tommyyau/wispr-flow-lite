# Electron Conversion Plan for WisprFlow Lite

## Status: 📋 PLANNING

## Problem Statement

Convert the existing Python voice transcription application (WisprFlow Lite) into a standalone Mac Electron application distributed as a DMG file. The current application is a command-line Python script that requires manual environment setup and dependency management.

## Root Cause Analysis

**Current Limitations:**
1. **Installation Complexity**: Users must install Python, pip dependencies, and configure environment variables
2. **No GUI**: Command-line interface limits user experience and adoption
3. **Distribution Challenges**: No simple installation method (DMG) for Mac users
4. **System Integration**: Requires manual permission setup for microphone/accessibility

**Requirements for Electron Conversion:**
1. **Standalone Distribution**: Single .app bundle installable via DMG
2. **GUI Interface**: User-friendly interface for configuration and control
3. **System Permissions**: Proper macOS permission handling
4. **Native Integration**: Maintain current audio/keyboard functionality

## Implementation Plan

### Phase 1: Architecture Setup (PyInstaller + Subprocess)
**Rationale**: Based on research, subprocess communication provides the best balance of performance, security, and maintainability for system-level access applications.

#### 1.0 Repository Reorganization
- Move existing Python CLI app to `python-cli/` folder (preserve completely)
- Create new `electron-app/` folder for Electron version
- Maintain separate README files for each version
- Keep original functionality 100% intact and usable

#### 1.1 Python Backend Preparation  
- Copy `voice_transcriber.py` to `electron-app/src/python/voice_transcriber_ipc.py`
- Create communication interface (IPC) between Python and Electron
- Modify copied Python app to accept commands via stdin/stdout or named pipes
- Ensure all dependencies (PyAudio, OpenAI client) are properly bundled
- **Original CLI version remains untouched**

#### 1.2 Electron Frontend Creation
- Initialize new Electron project structure
- Create main process to manage Python subprocess
- Design simple GUI for:
  - API key configuration
  - Recording status display
  - Settings management (language, hotkeys, etc.)
  - Permission status indicators

#### 1.3 IPC Communication Protocol
- Design message format for Electron ↔ Python communication
- Implement commands: start_recording, stop_recording, configure, get_status
- Handle errors and subprocess management
- Implement graceful shutdown and resource cleanup

### Phase 2: GUI Development
**Target**: Create intuitive interface replacing command-line experience

#### 2.1 Main Window Design
- Status dashboard showing recording state
- Visual feedback for hotkey activation
- Configuration panel for all .env settings
- Permission status with helper links

#### 2.2 System Tray Integration
- Minimize to system tray for background operation
- Quick access menu for common functions
- Persistent operation like current CLI version

#### 2.3 Settings Management
- GUI forms for all configuration options
- Real-time validation (API key testing, audio device detection)
- Import/export of configuration

### Phase 3: Native Integration & Permissions
**Target**: Seamless macOS integration with proper permission handling

#### 3.1 macOS Permissions
- Request microphone access programmatically
- Guide users through Accessibility permissions setup
- Input Monitoring permissions for global hotkeys
- Proper entitlements configuration

#### 3.2 Native Features
- Integration with macOS notification system
- Native hotkey registration (alternative to current pynput approach)
- Audio device selection and monitoring

### Phase 4: Packaging & Distribution
**Target**: Professional DMG distribution

#### 4.1 Build Configuration
- electron-builder setup for macOS packaging
- Code signing configuration (developer certificate)
- Icon and branding assets
- Version management and updates

#### 4.2 DMG Creation
- Custom DMG background and layout
- Installation instructions
- Automated build pipeline
- Testing on clean macOS systems

## Technical Architecture

```
┌─────────────────────────────────────┐
│           Electron App              │
├─────────────────────────────────────┤
│  Main Process (Node.js)             │
│  ├─ Python Subprocess Manager       │
│  ├─ IPC Communication               │
│  ├─ System Permissions Handler      │
│  └─ Native Integration              │
├─────────────────────────────────────┤
│  Renderer Process (GUI)             │
│  ├─ Configuration Interface         │
│  ├─ Status Dashboard               │
│  └─ Settings Management            │
└─────────────────────────────────────┘
              │ IPC Communication
              ▼
┌─────────────────────────────────────┐
│      Python Backend                │
│      (PyInstaller Bundle)           │
├─────────────────────────────────────┤
│  ├─ voice_transcriber.py           │
│  ├─ PyAudio (native)               │
│  ├─ OpenAI Client                  │
│  ├─ pynput (keyboard)              │
│  └─ All dependencies bundled       │
└─────────────────────────────────────┘
```

## File Structure

**Dual-Version Structure**: Maintain original Python CLI alongside new Electron app

```
wispr-flow-lite/
├── python-cli/         # ORIGINAL standalone Python app
│   ├── voice_transcriber.py
│   ├── requirements.txt
│   ├── .env_example
│   ├── install.py
│   └── README.md       # CLI-specific instructions
│
├── electron-app/       # NEW Electron application
│   ├── src/
│   │   ├── main/       # Electron main process
│   │   │   ├── main.js
│   │   │   ├── python-manager.js
│   │   │   └── permissions.js
│   │   ├── renderer/   # GUI frontend
│   │   │   ├── index.html
│   │   │   ├── renderer.js
│   │   │   └── styles.css
│   │   └── python/     # Python backend (copy + IPC modifications)
│   │       ├── voice_transcriber_ipc.py
│   │       ├── ipc_handler.py
│   │       └── requirements.txt
│   ├── build/          # Build configuration
│   │   ├── entitlements.mac.plist
│   │   ├── icon.icns
│   │   └── dmg-background.png
│   ├── dist/           # Build output
│   └── package.json
│
├── docs/               # Shared documentation
├── .gitignore
└── README.md           # Project overview with both options
```

## Key Implementation Decisions

### 1. Communication Method: Subprocess + IPC
**Choice**: PyInstaller + subprocess communication via stdin/stdout
**Reasoning**: 
- Clean separation of concerns
- No Python installation required on target machines
- Better security isolation
- Easier maintenance and debugging
- Full native performance for audio processing

### 2. GUI Framework: Electron + HTML/CSS/JS
**Choice**: Standard Electron web technologies
**Reasoning**:
- Rapid development and prototyping
- Rich ecosystem for UI components
- Easy styling and responsive design
- Cross-platform consistency (future expansion)

### 3. Packaging Strategy: electron-builder
**Choice**: electron-builder with PyInstaller preprocessing
**Reasoning**:
- Industry standard for Electron app distribution
- Built-in DMG creation and code signing
- Automatic native dependency handling
- Professional installation experience

## Success Criteria

### Functional Requirements
- [ ] Single-click installation via DMG
- [ ] GUI configuration of all settings
- [ ] Identical voice transcription functionality
- [ ] System tray operation
- [ ] Proper macOS permission handling
- [ ] Hotkey functionality preservation

### Technical Requirements
- [ ] <100MB total application size
- [ ] <3 second startup time
- [ ] Proper resource cleanup on exit
- [ ] Error handling and user feedback
- [ ] Automatic updates capability

### User Experience Requirements
- [ ] No command-line knowledge required
- [ ] Clear permission setup guidance
- [ ] Visual feedback for all operations
- [ ] Professional macOS app appearance

## Potential Challenges & Mitigations

### Challenge 1: PyAudio Native Dependencies
**Risk**: PyAudio compilation issues with electron-builder
**Mitigation**: Pre-compile with PyInstaller on macOS, bundle as binary

### Challenge 2: Subprocess Management
**Risk**: Zombie processes or resource leaks
**Mitigation**: Implement proper process lifecycle management and cleanup

### Challenge 3: Permission Complexity
**Risk**: Users confused by multiple permission dialogs
**Mitigation**: Guided setup wizard with clear explanations

### Challenge 4: Code Signing & Notarization
**Risk**: Distribution blocked by macOS security
**Mitigation**: Proper developer certificate and notarization workflow

## Development Timeline Estimate

- **Phase 1 (Architecture)**: 2-3 days
- **Phase 2 (GUI Development)**: 3-4 days  
- **Phase 3 (Native Integration)**: 2-3 days
- **Phase 4 (Packaging)**: 2-3 days
- **Total**: 9-13 days

## Next Steps

1. **Reorganize repository**: Move current files to `python-cli/`, create `electron-app/` folder
2. **Test original CLI**: Verify Python app works perfectly in new `python-cli/` location
3. **Create Electron project structure** in `electron-app/`
4. **Copy and modify Python app** for IPC communication (keep original intact)
5. **Implement basic GUI** with configuration
6. **Test subprocess communication** between Electron and Python
7. **Test both versions**: Ensure CLI still works independently and Electron app functions
8. **Add native macOS integration**
9. **Configure build and packaging**
10. **Final testing**: Test both CLI and Electron app on clean macOS system
11. **Create final DMG distribution**

**Key Principle**: Original Python CLI remains 100% functional and unchanged throughout entire process.

## Testing Strategy

### CLI Testing (After Reorganization)
- [ ] Test virtual environment creation in `python-cli/`
- [ ] Verify all dependencies install correctly
- [ ] Test voice recording and transcription functionality
- [ ] Verify hotkey functionality (Option/Alt)
- [ ] Test configuration via `.env` file
- [ ] Ensure all original features work identically

### Electron App Testing (During Development)
- [ ] Test Python subprocess communication
- [ ] Verify GUI configuration interface
- [ ] Test voice recording through Electron interface
- [ ] Verify system tray functionality
- [ ] Test macOS permissions handling
- [ ] Ensure hotkey functionality works in packaged app

### Cross-Version Testing
- [ ] Verify both versions can run simultaneously (different hotkeys)
- [ ] Test that CLI version is completely independent
- [ ] Ensure no conflicts between versions
- [ ] Verify both can use same OpenAI API key

---

This plan transforms the current command-line Python application into a professional macOS application while preserving all existing functionality and improving user experience significantly.