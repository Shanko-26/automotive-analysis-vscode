#!/bin/bash

echo "🚀 Installing Automotive Analysis VS Code Extension"
echo "=================================================="

# Check if VS Code is installed
if ! command -v code &> /dev/null; then
    echo "❌ VS Code not found. Please install VS Code first."
    exit 1
fi

echo "✅ VS Code found"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
if ! npm install; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
if ! npm run compile; then
    echo "❌ Failed to compile TypeScript"
    exit 1
fi

# Package extension
echo "📦 Packaging extension..."
if ! npx vsce package --no-dependencies; then
    echo "❌ Failed to package extension"
    exit 1
fi

# Install extension
echo "🔧 Installing extension..."
VSIX_FILE=$(ls *.vsix | head -n 1)
if [ -n "$VSIX_FILE" ]; then
    code --install-extension "$VSIX_FILE"
    echo "✅ Extension installed successfully!"
else
    echo "❌ No VSIX file found"
    exit 1
fi

echo ""
echo "🎉 Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Restart VS Code"
echo "2. Open a workspace with .mdf, .mf4, .blf, or .asc files"
echo "3. The extension will automatically try to start the best available backend:"
echo "   • 🐳 Docker (if available) - most reliable"
echo "   • ⚡ UV (if available) - fastest setup"
echo "   • 🐍 Python (fallback) - traditional approach"
echo ""
echo "💡 For best experience, install Docker Desktop:"
echo "   https://www.docker.com/products/docker-desktop/"
echo ""
echo "🔧 Available commands:"
echo "   • Automotive Analysis: Start Backend"
echo "   • Automotive Analysis: Switch Backend Type"
echo "   • Automotive Analysis: Show Backend Status"
echo "   • Automotive Analysis: Troubleshooting Guide" 