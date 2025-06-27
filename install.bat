@echo off
echo 🚀 Installing Automotive Analysis VS Code Extension
echo ==================================================

REM Check if VS Code is installed
where code >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ VS Code not found. Please install VS Code first.
    pause
    exit /b 1
)

echo ✅ VS Code found

REM Install Node.js dependencies
echo 📦 Installing Node.js dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

REM Compile TypeScript
echo 🔨 Compiling TypeScript...
call npm run compile
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to compile TypeScript
    pause
    exit /b 1
)

REM Package extension
echo 📦 Packaging extension...
call npx vsce package --no-dependencies
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Failed to package extension
    pause
    exit /b 1
)

REM Install extension
echo 🔧 Installing extension...
for %%f in (*.vsix) do (
    code --install-extension "%%f"
    echo ✅ Extension installed successfully!
    goto :installed
)

echo ❌ No VSIX file found
pause
exit /b 1

:installed
echo.
echo 🎉 Installation Complete!
echo.
echo 📋 Next Steps:
echo 1. Restart VS Code
echo 2. Open a workspace with .mdf, .mf4, .blf, or .asc files
echo 3. The extension will automatically try to start the best available backend:
echo    • 🐳 Docker (if available) - most reliable
echo    • ⚡ UV (if available) - fastest setup
echo    • 🐍 Python (fallback) - traditional approach
echo.
echo 💡 For best experience, install Docker Desktop:
echo    https://www.docker.com/products/docker-desktop/
echo.
echo 🔧 Available commands:
echo    • Automotive Analysis: Start Backend
echo    • Automotive Analysis: Switch Backend Type
echo    • Automotive Analysis: Show Backend Status
echo    • Automotive Analysis: Troubleshooting Guide
echo.
pause 