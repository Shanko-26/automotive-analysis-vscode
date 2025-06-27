import * as vscode from 'vscode';
import { DockerService, DockerBackendStatus } from './dockerService';
import { UVService, UVBackendStatus } from './uvService';
import { PythonService, BackendStatus } from './pythonService';
import { Logger } from './utils/logger';
import { BackendServiceInterface } from './fileHandler';

export type BackendType = 'docker' | 'uv' | 'python' | 'auto';

export interface UnifiedBackendStatus {
    type: BackendType;
    isRunning: boolean;
    port: number;
    lastError?: string;
    details: DockerBackendStatus | UVBackendStatus | BackendStatus;
}

export class BackendManager implements BackendServiceInterface {
    private readonly logger: Logger;
    private readonly context: vscode.ExtensionContext;
    private currentService: DockerService | UVService | PythonService | null = null;
    private currentType: BackendType | null = null;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.logger = new Logger('BackendManager');
    }

    async startBackend(): Promise<void> {
        const config = vscode.workspace.getConfiguration('automotiveAnalysis');
        const preferredType = config.get<BackendType>('backendType', 'auto');

        if (preferredType === 'auto') {
            await this.autoSelectBackend();
        } else {
            await this.startSpecificBackend(preferredType);
        }
    }

    private async autoSelectBackend(): Promise<void> {
        this.logger.info('Auto-selecting best backend option...');

        // Strategy 1: Try Docker first (most reliable)
        try {
            this.logger.info('Attempting Docker backend...');
            const dockerService = new DockerService(this.context);
            await dockerService.startBackend();
            
            this.currentService = dockerService;
            this.currentType = 'docker';
            this.logger.info('✅ Docker backend started successfully');
            
            vscode.window.showInformationMessage(
                'Automotive Analysis: Backend started using Docker 🐳'
            );
            return;
            
        } catch (error) {
            this.logger.warn('Docker backend failed:', error);
            
            // Show Docker installation hint
            const installDocker = await vscode.window.showWarningMessage(
                'Docker not available. Install Docker Desktop for best experience?',
                'Install Docker',
                'Continue with alternative'
            );
            
            if (installDocker === 'Install Docker') {
                vscode.env.openExternal(vscode.Uri.parse('https://www.docker.com/products/docker-desktop/'));
            }
        }

        // Strategy 2: Try UV (fast and modern)
        try {
            this.logger.info('Attempting UV backend...');
            const uvService = new UVService(this.context);
            await uvService.startBackend();
            
            this.currentService = uvService;
            this.currentType = 'uv';
            this.logger.info('✅ UV backend started successfully');
            
            vscode.window.showInformationMessage(
                'Automotive Analysis: Backend started using UV ⚡'
            );
            return;
            
        } catch (error) {
            this.logger.warn('UV backend failed:', error);
        }

        // Strategy 3: Fallback to traditional Python (last resort)
        try {
            this.logger.info('Attempting traditional Python backend...');
            const pythonService = new PythonService(this.context);
            await pythonService.startBackend();
            
            this.currentService = pythonService;
            this.currentType = 'python';
            this.logger.info('✅ Traditional Python backend started successfully');
            
            vscode.window.showWarningMessage(
                'Automotive Analysis: Backend started using system Python. Consider installing Docker or UV for better performance.'
            );
            return;
            
        } catch (error) {
            this.logger.error('All backend options failed:', error);
            
            const troubleshoot = await vscode.window.showErrorMessage(
                'Failed to start any backend. Check the troubleshooting guide?',
                'Open Guide',
                'Retry'
            );
            
            if (troubleshoot === 'Open Guide') {
                this.showTroubleshootingGuide();
            } else if (troubleshoot === 'Retry') {
                await this.startBackend();
            }
            
            throw new Error('All backend startup strategies failed');
        }
    }

    private async startSpecificBackend(type: BackendType): Promise<void> {
        this.logger.info(`Starting specific backend: ${type}`);

        try {
            switch (type) {
                case 'docker':
                    this.currentService = new DockerService(this.context);
                    break;
                case 'uv':
                    this.currentService = new UVService(this.context);
                    break;
                case 'python':
                    this.currentService = new PythonService(this.context);
                    break;
                default:
                    throw new Error(`Unknown backend type: ${type}`);
            }

            await this.currentService.startBackend();
            this.currentType = type;
            this.logger.info(`✅ ${type} backend started successfully`);

        } catch (error) {
            this.logger.error(`Failed to start ${type} backend:`, error);
            throw error;
        }
    }

    async stopBackend(): Promise<void> {
        if (this.currentService) {
            await this.currentService.stopBackend();
            this.currentService = null;
            this.currentType = null;
        }
    }

    async getFileInfo(filePath: string): Promise<any> {
        if (!this.currentService) {
            throw new Error('No backend service running');
        }
        return this.currentService.getFileInfo(filePath);
    }

    async getSignals(filePath: string): Promise<any> {
        if (!this.currentService) {
            throw new Error('No backend service running');
        }
        return this.currentService.getSignals(filePath);
    }

    // Implement BackendServiceInterface methods for FileHandler compatibility
    async getSignalData(filePath: string, signals: string[], startTime?: number, endTime?: number): Promise<any> {
        if (!this.currentService) {
            throw new Error('No backend service running');
        }
        return this.currentService.getSignalData(filePath, signals, startTime, endTime);
    }

    getStatus(): UnifiedBackendStatus {
        if (!this.currentService || !this.currentType) {
            return {
                type: 'python',
                isRunning: false,
                port: 8000,
                details: { isRunning: false, port: 8000 }
            };
        }

        const details = this.currentService.getStatus();
        return {
            type: this.currentType,
            isRunning: details.isRunning,
            port: details.port,
            lastError: details.lastError,
            details
        };
    }

    private showTroubleshootingGuide(): void {
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
3. Use "Start Python Backend" command

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

        // Create and show troubleshooting document
        vscode.workspace.openTextDocument({
            content: troubleshootingContent,
            language: 'markdown'
        }).then(doc => {
            vscode.window.showTextDocument(doc);
        });
    }

    async switchBackend(newType: BackendType): Promise<void> {
        this.logger.info(`Switching to ${newType} backend...`);
        
        // Stop current backend
        await this.stopBackend();
        
        // Start new backend
        await this.startSpecificBackend(newType);
        
        vscode.window.showInformationMessage(
            `Switched to ${newType} backend successfully`
        );
    }
} 