import Foundation
import ApplicationServices
import Carbon
import AppKit

class InputInjector {
    static func inject(text: String) {
        Logger.shared.log("InputInjector: Starting injection of \(text.count) characters")
        
        // Check if we have accessibility permissions
        if !AXIsProcessTrusted() {
            Logger.shared.log("InputInjector: ERROR - No accessibility permissions!")
            showPermissionAlert()
            return
        }
        
        // Method 1: Using CGEvent (Simulates keyboard input)
        // This is robust but can be slow for long text
        
        // Method 2: Using AXUIElement (Accessibility API) to set value
        // This is faster but requires the target app to support AX
        
        // We will use a hybrid approach or just CGEvent for compatibility similar to pyautogui
        
        let source = CGEventSource(stateID: .hidSystemState)
        
        for (index, char) in text.enumerated() {
            if let event = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: true) {
                var charArray = [UniChar](String(char).utf16)
                event.keyboardSetUnicodeString(stringLength: charArray.count, unicodeString: &charArray)
                event.post(tap: .cghidEventTap)
            }
            
            if let event = CGEvent(keyboardEventSource: source, virtualKey: 0, keyDown: false) {
                var charArray = [UniChar](String(char).utf16)
                event.keyboardSetUnicodeString(stringLength: charArray.count, unicodeString: &charArray)
                event.post(tap: .cghidEventTap)
            }
            
            // Small delay to prevent buffer overflow in target app
            usleep(2000) // 2ms
            
            if (index + 1) % 10 == 0 {
                Logger.shared.log("InputInjector: Injected \(index + 1)/\(text.count) characters")
            }
        }
        
        Logger.shared.log("InputInjector: Completed injection")
    }
    
    private static func showPermissionAlert() {
        DispatchQueue.main.async {
            let alert = NSAlert()
            alert.messageText = "Accessibility Permissions Required"
            alert.informativeText = """
            Wispr Flow Lite needs Accessibility permissions to type text.
            
            Please go to:
            System Settings → Privacy & Security → Accessibility
            
            Then add or enable "Wispr Flow Lite"
            """
            alert.alertStyle = .warning
            alert.addButton(withTitle: "Open System Settings")
            alert.addButton(withTitle: "OK")
            
            if alert.runModal() == .alertFirstButtonReturn {
                NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility")!)
            }
        }
    }
}
