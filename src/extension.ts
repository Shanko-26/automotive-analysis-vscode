import * as vscode from 'vscode';
import { FileHandler } from './fileHandler';
import { BackendManager } from './backendManager';
import { Logger } from './utils/logger';

export function activate(context: vscode.ExtensionContext) {
    console.log('Automotive Analysis extension is now active (console.log)');
    const logger = new Logger('Extension');
    logger.info('Automotive Analysis extension is now active');

    // Initialize services
    const backendManager = new BackendManager(context);
    const fileHandler = new FileHandler(backendManager);

    // Register commands
    const openFileCommand = vscode.commands.registerCommand(
        'automotive-analysis.openFile',
        (uri: vscode.Uri) => fileHandler.openFile(uri)
    );

    const startBackendCommand = vscode.commands.registerCommand(
        'automotive-analysis.startBackend',
        () => backendManager.startBackend()
    );

    const stopBackendCommand = vscode.commands.registerCommand(
        'automotive-analysis.stopBackend',
        () => backendManager.stopBackend()
    );

    const switchBackendCommand = vscode.commands.registerCommand(
        'automotive-analysis.switchBackend',
        async () => {
            const backendTypes = [
                { label: '🐳 Docker (Recommended)', value: 'docker' },
                { label: '⚡ UV (Fast)', value: 'uv' },
                { label: '🐍 Python (Traditional)', value: 'python' },
                { label: '🤖 Auto-select', value: 'auto' }
            ];

            const selected = await vscode.window.showQuickPick(backendTypes, {
                placeHolder: 'Select backend type'
            });

            if (selected) {
                if (selected.value === 'auto') {
                    await backendManager.startBackend();
                } else {
                    await backendManager.switchBackend(selected.value as any);
                }
            }
        }
    );

    const backendStatusCommand = vscode.commands.registerCommand(
        'automotive-analysis.backendStatus',
        () => {
            const status = backendManager.getStatus();
            const statusIcon = status.isRunning ? '✅' : '❌';
            const message = `${statusIcon} Backend: ${status.type} (Port: ${status.port})`;
            
            vscode.window.showInformationMessage(message);
        }
    );

    const troubleshootCommand = vscode.commands.registerCommand(
        'automotive-analysis.troubleshoot',
        () => {
            // This will be handled by the BackendManager's showTroubleshootingGuide
            const troubleshootingContent = `
# Automotive Analysis Backend Troubleshooting

## Quick Fixes

### Option 1: Docker (Recommended) 🐳
1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Restart VS Code
3. Extension will automatically use Docker

### Option 2: UV (Fast Alternative) ⚡
1. UV will auto-install when extension starts
2. If issues, manually install: \`curl -LsSf https://astral.sh/uv/install.sh | sh\`
3. Restart VS Code

### Option 3: Manual Python Setup 🐍
1. Install Python 3.11+
2. Run: \`python setup.py\` in extension directory
3. Use "Start Backend" command

## Common Issues

### "Docker not found"
- Install Docker Desktop
- Ensure Docker daemon is running
- Check Docker is in PATH

### "Python version issues"
- Use Python 3.11 or 3.12
- Avoid Python 3.13 (not yet supported by asammdf)

### "Permission errors"
- Run VS Code as administrator (Windows)
- Check file permissions in workspace

### "Port 8000 already in use"
- Change port in settings: automotiveAnalysis.backendPort
- Kill existing processes: \`lsof -ti:8000 | xargs kill\`

## Need Help?
Open an issue: https://github.com/your-repo/automotive-analysis/issues
            `;

            vscode.workspace.openTextDocument({
                content: troubleshootingContent,
                language: 'markdown'
            }).then(doc => {
                vscode.window.showTextDocument(doc);
            });
        }
    );

    const showSignalsCommand = vscode.commands.registerCommand(
        'automotive-analysis.showSignals',
        (uri: vscode.Uri) => fileHandler.showSignals(uri)
    );

    // Add commands to subscriptions
    context.subscriptions.push(
        openFileCommand, 
        startBackendCommand, 
        stopBackendCommand,
        switchBackendCommand,
        backendStatusCommand,
        troubleshootCommand,
        showSignalsCommand
    );

    // Auto-start backend if configured
    const config = vscode.workspace.getConfiguration('automotiveAnalysis');
    if (config.get('autoStartBackend', true)) {
        backendManager.startBackend().catch(error => {
            logger.error('Failed to auto-start backend:', error);
            vscode.window.showWarningMessage('Failed to start backend. Use command "Start Backend" to retry.');
        });
    }

    // Register file hover provider for metadata
    const hoverProvider = vscode.languages.registerHoverProvider(
        { pattern: '**/*.{mdf,mf4,blf,asc}' },
        {
            provideHover(document, position, token) {
                return fileHandler.provideHover(document, position);
            }
        }
    );

    context.subscriptions.push(hoverProvider);

    logger.info('Extension activation completed');
}

export function deactivate() {
    const logger = new Logger('Extension');
    logger.info('Automotive Analysis extension is deactivating');
} 