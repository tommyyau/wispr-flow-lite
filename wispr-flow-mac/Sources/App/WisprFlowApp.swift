import SwiftUI
import AppKit

@main
struct WisprFlowApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        MenuBarExtra("Wispr Flow", systemImage: appState.isRecording ? "record.circle.fill" : "waveform") {
            Button("Start Recording") {
                appState.startRecording()
            }
            .keyboardShortcut("r", modifiers: .command)
            .disabled(appState.isRecording)
            
            Button("Stop Recording") {
                appState.stopRecording()
            }
            .disabled(!appState.isRecording)
            
            Divider()
            
            Button("Settings") {
                WindowManager.shared.openSettings()
            }
            
            Divider()
            
            Button("Quit") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q", modifiers: .command)
        }
        .menuBarExtraStyle(.menu)
    }
}

class SettingsWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

class WindowManager: NSObject, NSWindowDelegate {
    static let shared = WindowManager()
    private var settingsWindow: SettingsWindow?
    
    func openSettings() {
        print("WindowManager: openSettings called")
        
        // Force app to be a "regular" app temporarily to ensure keyboard focus works
        NSApp.setActivationPolicy(.regular)
        
        if settingsWindow == nil {
            print("WindowManager: Creating new window")
            let settingsView = SettingsView()
            let hostingController = NSHostingController(rootView: settingsView)
            
            let window = SettingsWindow(contentViewController: hostingController)
            window.title = "Settings"
            window.setContentSize(NSSize(width: 400, height: 300))
            window.styleMask = [.titled, .closable, .miniaturizable]
            window.level = .floating
            window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]
            window.center()
            window.isReleasedWhenClosed = false
            window.delegate = self // Set delegate to handle closing
            
            settingsWindow = window
        } else {
            print("WindowManager: Window already exists")
        }
        
        settingsWindow?.center()
        settingsWindow?.makeKeyAndOrderFront(nil)
        settingsWindow?.orderFrontRegardless()
        NSApp.activate(ignoringOtherApps: true)
        print("WindowManager: Window activated (Regular Policy)")
    }
    
    func windowWillClose(_ notification: Notification) {
        // Switch back to "accessory" (menu bar only) mode when window closes
        NSApp.setActivationPolicy(.accessory)
        print("WindowManager: Switched back to Accessory Policy")
    }
}

class AppState: ObservableObject, GlobalHotkeyDelegate {
    @Published var isRecording = false
    @Published var isProcessing = false
    
    private var audioRecorder = AudioRecorder()
    private var fireworksService = FireworksService()
    private var globalHotkey = GlobalHotkey()
    
    init() {
        globalHotkey.delegate = self
        globalHotkey.startMonitoring()
        Logger.shared.log("Wispr Flow Lite V2 Initialized")
    }
    
    func startRecording() {
        guard !isRecording else { return }
        if let _ = audioRecorder.startRecording() {
            isRecording = true
            Logger.shared.log("Started Recording")
        }
    }
    
    func stopRecording() {
        guard isRecording else { return }
        audioRecorder.stopRecording()
        isRecording = false
        isProcessing = true
        Logger.shared.log("Stopped Recording")
        
        // Process audio
        processAudio()
    }
    
    private func processAudio() {
        let tempDir = FileManager.default.temporaryDirectory
        let fileURL = tempDir.appendingPathComponent("wispr_recording.m4a")
        
        // Get API Key from UserDefaults (Settings)
        let apiKey = UserDefaults.standard.string(forKey: "fireworksApiKey") ?? ""
        let language = UserDefaults.standard.string(forKey: "selectedLanguage") ?? "en"
        
        guard !apiKey.isEmpty else {
            Logger.shared.log("API Key missing")
            self.isProcessing = false
            return
        }
        
        fireworksService.transcribe(audioFileURL: fileURL, apiKey: apiKey, language: language) { [weak self] result in
            DispatchQueue.main.async {
                guard let self = self else { return }
                self.isProcessing = false
                switch result {
                case .success(let text):
                    Logger.shared.log("Transcribed: \(text)")
                    InputInjector.inject(text: text)
                case .failure(let error):
                    Logger.shared.log("Transcription failed: \(error)")
                }
            }
        }
    }
    
    // MARK: - GlobalHotkeyDelegate
    func hotkeyPressed() {
        startRecording()
    }
    
    func hotkeyReleased() {
        stopRecording()
    }
}
