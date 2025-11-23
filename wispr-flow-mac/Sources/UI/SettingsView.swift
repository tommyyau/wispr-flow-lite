import SwiftUI

struct SettingsView: View {
    // @EnvironmentObject var appState: AppState // Unused
    @AppStorage("fireworksApiKey") private var apiKey: String = ""
    @AppStorage("selectedLanguage") private var selectedLanguage: String = "en"
    @AppStorage("removeFillerWords") private var removeFillerWords: Bool = true
    
    var body: some View {
        Form {
            Section(header: Text("Fireworks AI Configuration")) {
                SecureField("API Key", text: $apiKey)
                    .textFieldStyle(.roundedBorder)
                Text("Your API key is stored securely.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Section(header: Text("Transcription Settings")) {
                Picker("Language", selection: $selectedLanguage) {
                    Text("English").tag("en")
                    Text("Spanish").tag("es")
                    Text("French").tag("fr")
                    Text("German").tag("de")
                    Text("Chinese").tag("zh")
                    // Add more languages as needed
                }
                
                Toggle("Remove Filler Words", isOn: $removeFillerWords)
            }
            
            Section(header: Text("About")) {
                Text("Wispr Flow Lite V2")
                    .font(.headline)
                Text("Native macOS Version")
                    .font(.caption)
            }
        }
        .padding()
        .frame(width: 400, height: 300)
    }
}
