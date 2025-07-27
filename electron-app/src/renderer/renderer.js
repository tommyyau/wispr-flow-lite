// Renderer process JavaScript for WisprFlow Lite Electron app

class WisprFlowRenderer {
    constructor() {
        this.isRecording = false;
        this.recordingStartTime = null;
        this.timerInterval = null;
        this.transcriptions = [];
        
        this.initializeElements();
        this.bindEvents();
        this.checkPermissions();
        this.loadConfiguration();
        
        // Listen for Python messages
        window.electronAPI.onPythonMessage((data) => {
            this.handlePythonMessage(data);
        });
        
        // Listen for tray recording events
        window.electronAPI.onStartRecording(() => {
            this.startRecording();
        });
    }

    initializeElements() {
        // Status elements
        this.statusIndicator = document.getElementById('status-indicator');
        this.statusText = document.getElementById('status-text');
        this.statusDot = this.statusIndicator.querySelector('.status-dot');
        
        // Recording timer (no longer using record button)
        this.recordingTimer = document.getElementById('recording-timer');
        this.timerText = document.getElementById('timer-text');
        
        // Permission elements
        this.permissionsSection = document.getElementById('permissions-section');
        this.micPermissionIcon = document.getElementById('mic-permission-icon');
        this.accessibilityPermissionIcon = document.getElementById('accessibility-permission-icon');
        this.requestMicBtn = document.getElementById('request-mic-btn');
        this.openAccessibilityBtn = document.getElementById('open-accessibility-btn');
        
        // Configuration elements
        this.apiKeyInput = document.getElementById('api-key');
        this.toggleApiKeyBtn = document.getElementById('toggle-api-key');
        this.languageSelect = document.getElementById('language');
        this.maxRecordingTimeInput = document.getElementById('max-recording-time');
        this.removeFillerWordsCheckbox = document.getElementById('remove-filler-words');
        this.typingSpeedSelect = document.getElementById('typing-speed');
        this.saveConfigBtn = document.getElementById('save-config-btn');
        
        // Transcriptions elements
        this.transcriptionsList = document.getElementById('transcriptions-list');
    }

    bindEvents() {
        // No longer using record button - recording controlled by Option key in Python process
        
        // Permission buttons
        this.requestMicBtn.addEventListener('click', () => {
            this.requestMicrophonePermission();
        });
        
        this.openAccessibilityBtn.addEventListener('click', () => {
            this.openAccessibilitySettings();
        });
        
        // Configuration
        this.toggleApiKeyBtn.addEventListener('click', () => {
            this.toggleApiKeyVisibility();
        });
        
        this.saveConfigBtn.addEventListener('click', () => {
            this.saveConfiguration();
        });
        
        // Auto-save configuration on changes
        [this.apiKeyInput, this.languageSelect, this.maxRecordingTimeInput, 
         this.removeFillerWordsCheckbox, this.typingSpeedSelect].forEach(element => {
            element.addEventListener('change', () => {
                this.saveConfiguration();
            });
        });
    }

    async checkPermissions() {
        try {
            const permissions = await window.electronAPI.getPermissions();
            this.updatePermissionStatus('microphone', permissions.microphone);
            this.updatePermissionStatus('accessibility', permissions.accessibility);
            
            // Show/hide permissions section based on status
            const allGranted = permissions.microphone && permissions.accessibility;
            if (allGranted) {
                this.permissionsSection.style.display = 'none';
                this.updateStatus('Background Mode Active', 'ready');
            } else {
                this.permissionsSection.style.display = 'block';
                this.updateStatus('Permissions Required', 'error');
            }
        } catch (error) {
            console.error('Error checking permissions:', error);
            this.updateStatus('Error checking permissions', 'error');
        }
    }

    updatePermissionStatus(type, granted) {
        const iconElement = type === 'microphone' ? this.micPermissionIcon : this.accessibilityPermissionIcon;
        iconElement.textContent = granted ? '✅' : '❌';
        
        const btnElement = type === 'microphone' ? this.requestMicBtn : this.openAccessibilityBtn;
        btnElement.style.display = granted ? 'none' : 'inline-block';
    }

    async requestMicrophonePermission() {
        try {
            await this.checkPermissions();
        } catch (error) {
            console.error('Error requesting microphone permission:', error);
        }
    }

    openAccessibilitySettings() {
        // This would ideally open System Preferences > Privacy & Security > Accessibility
        // For now, show instructions
        alert('Please open System Preferences > Privacy & Security > Privacy > Accessibility and enable access for WisprFlow Lite.');
    }

    toggleApiKeyVisibility() {
        const isPassword = this.apiKeyInput.type === 'password';
        this.apiKeyInput.type = isPassword ? 'text' : 'password';
        this.toggleApiKeyBtn.textContent = isPassword ? '🙈' : '👁️';
    }

    loadConfiguration() {
        // Load from localStorage or use defaults
        const config = {
            apiKey: localStorage.getItem('wisprflow_api_key') || '',
            language: localStorage.getItem('wisprflow_language') || 'en',
            maxRecordingTime: localStorage.getItem('wisprflow_max_recording_time') || '30',
            removeFillerWords: localStorage.getItem('wisprflow_remove_filler_words') !== 'false',
            typingSpeed: localStorage.getItem('wisprflow_typing_speed') || '0.01'
        };
        
        this.apiKeyInput.value = config.apiKey;
        this.languageSelect.value = config.language;
        this.maxRecordingTimeInput.value = config.maxRecordingTime;
        this.removeFillerWordsCheckbox.checked = config.removeFillerWords;
        this.typingSpeedSelect.value = config.typingSpeed;
    }

    async saveConfiguration() {
        const config = {
            apiKey: this.apiKeyInput.value,
            language: this.languageSelect.value,
            maxRecordingTime: this.maxRecordingTimeInput.value,
            removeFillerWords: this.removeFillerWordsCheckbox.checked,
            typingSpeed: this.typingSpeedSelect.value
        };
        
        // Save to localStorage
        localStorage.setItem('wisprflow_api_key', config.apiKey);
        localStorage.setItem('wisprflow_language', config.language);
        localStorage.setItem('wisprflow_max_recording_time', config.maxRecordingTime);
        localStorage.setItem('wisprflow_remove_filler_words', config.removeFillerWords.toString());
        localStorage.setItem('wisprflow_typing_speed', config.typingSpeed);
        
        // Send to Python process
        try {
            await window.electronAPI.configureApp(config);
            this.showToast('Configuration saved', 'success');
        } catch (error) {
            console.error('Error saving configuration:', error);
            this.showToast('Error saving configuration', 'error');
        }
    }

    // Recording is now handled automatically by Python Option key detection
    // GUI just monitors the status via IPC messages

    startTimer() {
        this.recordingTimer.style.display = 'block';
        this.timerInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.recordingStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            this.timerText.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        this.recordingTimer.style.display = 'none';
    }

    updateStatus(text, type = 'ready') {
        this.statusText.textContent = text;
        this.statusDot.className = 'status-dot';
        if (type !== 'ready') {
            this.statusDot.classList.add(type);
        }
    }

    handlePythonMessage(data) {
        console.log('Received from Python:', data);
        
        switch (data.type) {
            case 'transcription_complete':
                this.handleTranscriptionComplete(data);
                break;
            case 'recording_started':
                this.updateStatus('Recording...', 'recording');
                break;
            case 'recording_stopped':
                this.updateStatus('Processing...', 'processing');
                break;
            case 'error':
                this.handleError(data);
                break;
            case 'status':
                this.handleStatusUpdate(data);
                break;
        }
    }

    handleTranscriptionComplete(data) {
        this.updateStatus('Background Mode Active', 'ready');
        
        const transcription = {
            text: data.text,
            timestamp: new Date(),
            duration: data.duration || null
        };
        
        this.addTranscription(transcription);
        this.showToast('Text transcribed and typed!', 'success');
    }

    handleError(data) {
        this.updateStatus('Error', 'error');
        this.isRecording = false;
        this.stopTimer();
        this.showToast(data.message || 'An error occurred', 'error');
    }

    handleStatusUpdate(data) {
        // Handle status updates from Python Option key detection
        if (data.recording !== undefined) {
            if (data.recording && !this.isRecording) {
                this.isRecording = true;
                this.recordingStartTime = Date.now();
                this.updateStatus('Recording via Option Key...', 'recording');
                this.startTimer();
            } else if (!data.recording && this.isRecording) {
                this.isRecording = false;
                this.updateStatus('Processing...', 'processing');
                this.stopTimer();
            }
        }
    }

    addTranscription(transcription) {
        this.transcriptions.unshift(transcription);
        
        // Keep only last 10 transcriptions
        if (this.transcriptions.length > 10) {
            this.transcriptions = this.transcriptions.slice(0, 10);
        }
        
        this.renderTranscriptions();
    }

    renderTranscriptions() {
        if (this.transcriptions.length === 0) {
            this.transcriptionsList.innerHTML = '<p class="no-transcriptions">No transcriptions yet. Start recording to see them here.</p>';
            return;
        }
        
        this.transcriptionsList.innerHTML = this.transcriptions.map(transcription => `
            <div class="transcription-item">
                <div class="transcription-time">${transcription.timestamp.toLocaleTimeString()}</div>
                <div class="transcription-text">${transcription.text}</div>
            </div>
        `).join('');
    }

    showToast(message, type = 'info') {
        // Simple toast notification
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#34c759' : type === 'error' ? '#ff3b30' : '#007aff'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => toast.style.opacity = '1', 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WisprFlowRenderer();
});