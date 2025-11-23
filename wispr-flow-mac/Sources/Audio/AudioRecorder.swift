import Foundation
import AVFoundation

class AudioRecorder: NSObject, ObservableObject {
    private var audioRecorder: AVAudioRecorder?
    // private var recordingSession: AVAudioSession? // Not needed on macOS
    
    @Published var isRecording = false
    
    override init() {
        super.init()
        // Request permission
        switch AVCaptureDevice.authorizationStatus(for: .audio) {
            case .authorized:
                break
            case .notDetermined:
                AVCaptureDevice.requestAccess(for: .audio) { granted in
                    if granted { print("Microphone access granted") }
                }
            default:
                print("Microphone access denied")
        }
    }
    
    func startRecording() -> URL? {
        let tempDir = FileManager.default.temporaryDirectory
        let fileName = "wispr_recording.m4a"
        let fileURL = tempDir.appendingPathComponent(fileName)
        
        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 16000,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]
        
        do {
            audioRecorder = try AVAudioRecorder(url: fileURL, settings: settings)
            audioRecorder?.record()
            isRecording = true
            return fileURL
        } catch {
            print("Could not start recording: \(error)")
            return nil
        }
    }
    
    func stopRecording() {
        audioRecorder?.stop()
        audioRecorder = nil
        isRecording = false
    }
}
