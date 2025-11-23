import Foundation
import Carbon
import Cocoa

protocol GlobalHotkeyDelegate: AnyObject {
    func hotkeyPressed()
    func hotkeyReleased()
}

class GlobalHotkey {
    weak var delegate: GlobalHotkeyDelegate?
    private var eventTap: CFMachPort?
    private var runLoopSource: CFRunLoopSource?
    private var isPressed = false
    
    init() {
        // We will use a simple CGEvent tap to listen for the Option key
        // Note: This requires Accessibility permissions
    }
    
    func startMonitoring() {
        // Check permissions first
        if !AXIsProcessTrusted() {
            Logger.shared.log("Accessibility permissions not granted. Prompting user.")
            let options: NSDictionary = [kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String : true]
            AXIsProcessTrustedWithOptions(options)
        }
        
        let eventMask = (1 << CGEventType.flagsChanged.rawValue)
        
        guard let eventTap = CGEvent.tapCreate(
            tap: .cgSessionEventTap,
            place: .headInsertEventTap,
            options: .defaultTap,
            eventsOfInterest: CGEventMask(eventMask),
            callback: { (proxy, type, event, refcon) -> Unmanaged<CGEvent>? in
                if let observer = Unmanaged<GlobalHotkey>.fromOpaque(refcon!).takeUnretainedValue() as GlobalHotkey? {
                    if type == .tapDisabledByTimeout {
                        Logger.shared.log("Event tap disabled by timeout - Re-enabling")
                        CGEvent.tapEnable(tap: observer.eventTap!, enable: true)
                        return Unmanaged.passUnretained(event)
                    } else if type == .tapDisabledByUserInput {
                        Logger.shared.log("Event tap disabled by user input - Re-enabling")
                        CGEvent.tapEnable(tap: observer.eventTap!, enable: true)
                        return Unmanaged.passUnretained(event)
                    }
                    
                    observer.handleEvent(event: event)
                }
                return Unmanaged.passUnretained(event)
            },
            userInfo: Unmanaged.passUnretained(self).toOpaque()
        ) else {
            Logger.shared.log("Failed to create event tap")
            return
        }
        
        self.eventTap = eventTap
        self.runLoopSource = CFMachPortCreateRunLoopSource(kCFAllocatorDefault, eventTap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
        CGEvent.tapEnable(tap: eventTap, enable: true)
        Logger.shared.log("Global Hotkey Monitoring Started")
    }
    
    func stopMonitoring() {
        if let eventTap = eventTap {
            CGEvent.tapEnable(tap: eventTap, enable: false)
            if let runLoopSource = runLoopSource {
                CFRunLoopRemoveSource(CFRunLoopGetCurrent(), runLoopSource, .commonModes)
            }
        }
        Logger.shared.log("Global Hotkey Monitoring Stopped")
    }
    
    private func handleEvent(event: CGEvent) {
        let flags = event.flags
        let isOptionPressed = flags.contains(.maskAlternate)
        
        // Logger.shared.log("Flags changed: \(flags.rawValue), Option: \(isOptionPressed)")
        
        if isOptionPressed && !isPressed {
            isPressed = true
            Logger.shared.log("Hotkey Pressed (Option)")
            DispatchQueue.main.async {
                self.delegate?.hotkeyPressed()
            }
        } else if !isOptionPressed && isPressed {
            isPressed = false
            Logger.shared.log("Hotkey Released (Option)")
            DispatchQueue.main.async {
                self.delegate?.hotkeyReleased()
            }
        }
    }
}
