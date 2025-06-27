import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { Logger } from './utils/logger';

// Interface for backend services
export interface BackendServiceInterface {
    getStatus(): { isRunning: boolean; port: number; lastError?: string };
    startBackend(): Promise<void>;
    getFileInfo(filePath: string): Promise<any>;
    getSignals(filePath: string): Promise<any>;
}

export interface FileMetadata {
    file_path: string;
    file_size: number;
    file_type: string;
    duration: number;
    signal_count: number;
    recording_date?: string;
    measurement_system?: string;
    channels: Array<{
        name: string;
        unit: string;
        sample_rate: number;
        min_value: number;
        max_value: number;
    }>;
}

export class FileHandler {
    private readonly logger: Logger;
    private readonly backendService: BackendServiceInterface;
    private readonly supportedExtensions = ['.mdf', '.mf4', '.blf', '.asc'];

    constructor(backendService: BackendServiceInterface) {
        this.backendService = backendService;
        this.logger = new Logger('FileHandler');
    }

    async openFile(uri: vscode.Uri): Promise<void> {
        try {
            this.logger.info(`Opening file: ${uri.fsPath}`);
            
            // Check if backend is running
            const status = this.backendService.getStatus();
            if (!status.isRunning) {
                await vscode.window.showErrorMessage(
                    'Backend is not running. Please start it first.',
                    'Start Backend'
                ).then(async (action) => {
                    if (action === 'Start Backend') {
                        await this.backendService.startBackend();
                    }
                });
                return;
            }

            // Get file metadata
            const metadata = await this.backendService.getFileInfo(uri.fsPath);
            
            // Show file info
            await this.showFileInfo(uri, metadata);

        } catch (error) {
            this.logger.error('Failed to open file:', error);
            vscode.window.showErrorMessage(`Failed to open file: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    async showSignals(uri: vscode.Uri): Promise<void> {
        try {
            this.logger.info(`Showing signals for: ${uri.fsPath}`);
            
            const signals = await this.backendService.getSignals(uri.fsPath);
            await this.showSignalsList(uri, signals);

        } catch (error) {
            this.logger.error('Failed to show signals:', error);
            vscode.window.showErrorMessage(`Failed to get signals: ${error instanceof Error ? error.message : String(error)}`);
        }
    }

    async provideHover(document: vscode.TextDocument, position: vscode.Position): Promise<vscode.Hover | undefined> {
        const filePath = document.uri.fsPath;
        const extension = path.extname(filePath).toLowerCase();
        
        if (!this.supportedExtensions.includes(extension)) {
            return undefined;
        }

        try {
            // Check if backend is running
            const status = this.backendService.getStatus();
            if (!status.isRunning) {
                return new vscode.Hover([
                    '**Automotive Measurement File**',
                    'Backend not running. Use "Start Backend" command to enable analysis.'
                ]);
            }

            // Get basic file info for hover
            const fileStats = fs.statSync(filePath);
            const fileSizeMB = (fileStats.size / (1024 * 1024)).toFixed(1);
            
            const hoverContent = [
                '**Automotive Measurement File**',
                `**Size:** ${fileSizeMB} MB`,
                `**Type:** ${extension.toUpperCase()}`,
                '',
                'Click "Open in Analysis View" to analyze this file.'
            ];

            return new vscode.Hover(hoverContent);

        } catch (error) {
            this.logger.error('Error providing hover:', error);
            return new vscode.Hover([
                '**Automotive Measurement File**',
                'Error loading file information.'
            ]);
        }
    }

    private async showFileInfo(uri: vscode.Uri, metadata: FileMetadata): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'fileInfo',
            `File Info: ${path.basename(uri.fsPath)}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        const fileSizeMB = (metadata.file_size / (1024 * 1024)).toFixed(1);
        const durationMinutes = (metadata.duration / 60).toFixed(1);

        panel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>File Information</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; }
                    .info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
                    .info-item { background: #f5f5f5; padding: 15px; border-radius: 5px; }
                    .info-label { font-weight: bold; color: #333; margin-bottom: 5px; }
                    .info-value { color: #666; }
                    .signals-list { max-height: 300px; overflow-y: auto; border: 1px solid #ddd; border-radius: 5px; }
                    .signal-item { padding: 10px; border-bottom: 1px solid #eee; }
                    .signal-item:last-child { border-bottom: none; }
                    .signal-name { font-weight: bold; }
                    .signal-details { font-size: 0.9em; color: #666; margin-top: 5px; }
                </style>
            </head>
            <body>
                <h1>${path.basename(uri.fsPath)}</h1>
                
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">File Size</div>
                        <div class="info-value">${fileSizeMB} MB</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Duration</div>
                        <div class="info-value">${durationMinutes} minutes</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Signal Count</div>
                        <div class="info-value">${metadata.signal_count}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">File Type</div>
                        <div class="info-value">${metadata.file_type}</div>
                    </div>
                </div>

                ${metadata.recording_date ? `
                <div class="info-item">
                    <div class="info-label">Recording Date</div>
                    <div class="info-value">${metadata.recording_date}</div>
                </div>
                ` : ''}

                ${metadata.measurement_system ? `
                <div class="info-item">
                    <div class="info-label">Measurement System</div>
                    <div class="info-value">${metadata.measurement_system}</div>
                </div>
                ` : ''}

                <h2>Available Signals (${metadata.channels.length})</h2>
                <div class="signals-list">
                    ${metadata.channels.map(channel => `
                        <div class="signal-item">
                            <div class="signal-name">${channel.name}</div>
                            <div class="signal-details">
                                Unit: ${channel.unit} | 
                                Sample Rate: ${channel.sample_rate} Hz | 
                                Range: ${channel.min_value.toFixed(2)} - ${channel.max_value.toFixed(2)}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </body>
            </html>
        `;
    }

    private async showSignalsList(uri: vscode.Uri, signals: any): Promise<void> {
        const panel = vscode.window.createWebviewPanel(
            'signalsList',
            `Signals: ${path.basename(uri.fsPath)}`,
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Available Signals</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 20px; }
                    .search-box { width: 100%; padding: 10px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; }
                    .signals-list { max-height: 500px; overflow-y: auto; }
                    .signal-item { padding: 15px; border: 1px solid #eee; margin-bottom: 10px; border-radius: 5px; cursor: pointer; }
                    .signal-item:hover { background: #f5f5f5; }
                    .signal-name { font-weight: bold; font-size: 1.1em; }
                    .signal-details { margin-top: 10px; color: #666; }
                    .signal-unit { background: #e1f5fe; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
                </style>
            </head>
            <body>
                <h1>Available Signals</h1>
                <input type="text" class="search-box" placeholder="Search signals..." id="searchBox">
                
                <div class="signals-list" id="signalsList">
                    ${signals.channels.map((signal: any) => `
                        <div class="signal-item" data-signal="${signal.name}">
                            <div class="signal-name">${signal.name}</div>
                            <div class="signal-details">
                                <span class="signal-unit">${signal.unit}</span> | 
                                Sample Rate: ${signal.sample_rate} Hz | 
                                Range: ${signal.min_value.toFixed(2)} - ${signal.max_value.toFixed(2)}
                            </div>
                        </div>
                    `).join('')}
                </div>

                <script>
                    const searchBox = document.getElementById('searchBox');
                    const signalsList = document.getElementById('signalsList');
                    const signalItems = signalsList.querySelectorAll('.signal-item');

                    searchBox.addEventListener('input', (e) => {
                        const searchTerm = e.target.value.toLowerCase();
                        
                        signalItems.forEach(item => {
                            const signalName = item.getAttribute('data-signal').toLowerCase();
                            if (signalName.includes(searchTerm)) {
                                item.style.display = 'block';
                            } else {
                                item.style.display = 'none';
                            }
                        });
                    });

                    signalItems.forEach(item => {
                        item.addEventListener('click', () => {
                            const signalName = item.getAttribute('data-signal');
                            // TODO: Add signal to plot (will be implemented in Epic 2)
                            console.log('Selected signal:', signalName);
                        });
                    });
                </script>
            </body>
            </html>
        `;
    }
} 