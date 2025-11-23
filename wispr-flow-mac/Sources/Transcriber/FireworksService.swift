import Foundation

class FireworksService {
    private let session = URLSession.shared
    
    func transcribe(audioFileURL: URL, apiKey: String, language: String = "en", completion: @escaping (Result<String, Error>) -> Void) {
        let url = URL(string: "https://audio-turbo.us-virginia-1.direct.fireworks.ai/v1/audio/transcriptions")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var data = Data()
        
        // Add model parameter
        data.append("--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"model\"\r\n\r\n".data(using: .utf8)!)
        data.append("whisper-v3-turbo\r\n".data(using: .utf8)!)
        
        // Add language parameter (only if not auto)
        if language != "auto" {
            data.append("--\(boundary)\r\n".data(using: .utf8)!)
            data.append("Content-Disposition: form-data; name=\"language\"\r\n\r\n".data(using: .utf8)!)
            data.append("\(language)\r\n".data(using: .utf8)!)
        }
        
        // Add audio file
        data.append("--\(boundary)\r\n".data(using: .utf8)!)
        data.append("Content-Disposition: form-data; name=\"file\"; filename=\"audio.m4a\"\r\n".data(using: .utf8)!)
        data.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
        
        do {
            let audioData = try Data(contentsOf: audioFileURL)
            data.append(audioData)
        } catch {
            completion(.failure(error))
            return
        }
        
        data.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = data
        
        let task = session.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "FireworksService", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                return
            }
            
            do {
                if let json = try JSONSerialization.jsonObject(with: data, options: []) as? [String: Any],
                   let text = json["text"] as? String {
                    completion(.success(text))
                } else {
                    completion(.failure(NSError(domain: "FireworksService", code: -2, userInfo: [NSLocalizedDescriptionKey: "Invalid response format"])))
                }
            } catch {
                completion(.failure(error))
            }
        }
        task.resume()
    }
}
