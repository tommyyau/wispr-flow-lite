#!/bin/bash

APP_NAME="Wispr Flow Lite"
BUILD_DIR=".build/release"
APP_BUNDLE="$APP_NAME.app"
ICON_SOURCE="../wispr_flow_icon.png" # Assuming I'll move the generated icon here

echo "🚀 Building Wispr Flow Lite..."

# 1. Build Release Binary
swift build -c release

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# 2. Create App Bundle Structure
echo "📦 Creating App Bundle..."
rm -rf "$APP_BUNDLE"
mkdir -p "$APP_BUNDLE/Contents/MacOS"
mkdir -p "$APP_BUNDLE/Contents/Resources"

# 3. Copy Binary
cp "$BUILD_DIR/WisprFlowLite" "$APP_BUNDLE/Contents/MacOS/"

# 4. Copy Info.plist
cp Info.plist "$APP_BUNDLE/Contents/"

# 5. Create Icon (Simple conversion)
if [ -f "$ICON_SOURCE" ]; then
    echo "🎨 Creating App Icon..."
    mkdir -p "WisprFlowLite.iconset"
    
    # Convert source to true PNG first
    sips -s format png "$ICON_SOURCE" --out "WisprFlowLite.iconset/source.png" > /dev/null
    REAL_SOURCE="WisprFlowLite.iconset/source.png"
    
    # Create various sizes (simplified)
    sips -z 16 16     "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_16x16.png" > /dev/null
    sips -z 32 32     "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_16x16@2x.png" > /dev/null
    sips -z 32 32     "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_32x32.png" > /dev/null
    sips -z 64 64     "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_32x32@2x.png" > /dev/null
    sips -z 128 128   "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_128x128.png" > /dev/null
    sips -z 256 256   "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_128x128@2x.png" > /dev/null
    sips -z 256 256   "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_256x256.png" > /dev/null
    sips -z 512 512   "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_256x256@2x.png" > /dev/null
    sips -z 512 512   "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_512x512.png" > /dev/null
    sips -z 1024 1024 "$REAL_SOURCE" --out "WisprFlowLite.iconset/icon_512x512@2x.png" > /dev/null
    
    iconutil -c icns "WisprFlowLite.iconset" -o "$APP_BUNDLE/Contents/Resources/AppIcon.icns"
    rm -rf "WisprFlowLite.iconset"
else
    echo "⚠️ Icon file not found at $ICON_SOURCE"
fi

echo "✅ Done! App created at: $(pwd)/$APP_BUNDLE"
echo "You can drag this to your Applications folder."
