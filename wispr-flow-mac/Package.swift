// swift-tools-version: 5.9
// The swift-tools-version declares the minimum version of Swift required to build this package.

import PackageDescription

let package = Package(
    name: "WisprFlowLite",
    platforms: [
        .macOS(.v13)
    ],
    products: [
        .executable(
            name: "WisprFlowLite",
            targets: ["WisprFlowLite"]),
    ],
    dependencies: [
        // No external dependencies needed for the core functionality
        // We use native AVFoundation, URLSession, and SwiftUI
    ],
    targets: [
        .executableTarget(
            name: "WisprFlowLite",
            dependencies: [],
            path: "Sources",
            resources: [
                // Add resources here if needed (e.g. icons, sounds)
            ]
        ),
    ]
)
