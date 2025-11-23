import Foundation

class Logger {
    static let shared = Logger()
    private let logFileURL: URL
    
    init() {
        let docsDir = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
        logFileURL = docsDir.appendingPathComponent("wispr_flow_debug.log")
    }
    
    func log(_ message: String) {
        let timestamp = ISO8601DateFormatter().string(from: Date())
        let logMessage = "[\(timestamp)] \(message)\n"
        
        if let data = logMessage.data(using: .utf8) {
            if FileManager.default.fileExists(atPath: logFileURL.path) {
                if let fileHandle = try? FileHandle(forWritingTo: logFileURL) {
                    fileHandle.seekToEndOfFile()
                    fileHandle.write(data)
                    fileHandle.closeFile()
                }
            } else {
                try? data.write(to: logFileURL)
            }
        }
        
        // Also print to console for terminal usage
        print(message)
    }
}
