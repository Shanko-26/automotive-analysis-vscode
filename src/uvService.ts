import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import axios, { AxiosInstance } from 'axios';
import { Logger } from './utils/logger';

export interface UVBackendStatus {
    isRunning: boolean;
    venvPath: string;
    port: number;
    pid?: number;
    lastError?: string;
}

export class UVService {
    private readonly logger: Logger;
    private readonly context: vscode.ExtensionContext;
    private backendProcess?: any;
    private httpClient: AxiosInstance;
    private status: UVBackendStatus;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.logger = new Logger('UVService');
        
        const venvPath = path.join(context.extensionPath, '.venv');
        this.status = { 
            isRunning: false, 
            port: 8000,
            venvPath 
        };
        
        const config = vscode.workspace.getConfiguration('automotiveAnalysis');
        this.status.port = config.get('backendPort', 8000);
        
        this.httpClient = axios.create({
            baseURL: `http://localhost:${this.status.port}`,
            timeout: 5000
        });
    }

    async startBackend(): Promise<void> {
        if (this.status.isRunning) {
            this.logger.info('UV backend is already running');
            return;
        }

        try {
            this.logger.info('Starting UV-managed Python backend...');
            
            // Check if UV is available
            await this.checkUVAvailability();
            
            // Setup virtual environment with UV
            await this.setupVirtualEnvironment();
            
            // Install dependencies using UV
            await this.installDependencies();
            
            // Start backend process
            await this.startBackendProcess();
            
            // Wait for backend to be ready
            await this.waitForBackend();
            
            this.status.isRunning = true;
            this.logger.info(`UV backend started successfully on port ${this.status.port}`);
            
        } catch (error) {
            this.logger.error('Failed to start UV backend:', error);
            this.status.lastError = error instanceof Error ? error.message : String(error);
            throw error;
        }
    }

    private async checkUVAvailability(): Promise<void> {
        const { exec } = require('child_process');
        
        return new Promise((resolve, reject) => {
            exec('uv --version', (error: any, stdout: string) => {
                if (error) {
                    // Try to install UV automatically
                    this.logger.info('UV not found, attempting automatic installation...');
                    this.installUV().then(resolve).catch(reject);
                } else {
                    this.logger.info(`UV found: ${stdout.trim()}`);
                    resolve();
                }
            });
        });
    }

    private async installUV(): Promise<void> {
        const { exec } = require('child_process');
        
        return new Promise((resolve, reject) => {
            // Use the official UV installer
            const installCommand = process.platform === 'win32' 
                ? 'powershell -c "irm https://astral.sh/uv/install.ps1 | iex"'
                : 'curl -LsSf https://astral.sh/uv/install.sh | sh';
            
            this.logger.info('Installing UV package manager...');
            exec(installCommand, (error: any, stdout: string, stderr: string) => {
                if (error) {
                    reject(new Error(`Failed to install UV: ${stderr}`));
                } else {
                    this.logger.info('UV installed successfully');
                    resolve();
                }
            });
        });
    }

    private async setupVirtualEnvironment(): Promise<void> {
        const { exec } = require('child_process');
        const extensionPath = this.context.extensionPath;
        
        return new Promise((resolve, reject) => {
            // UV creates virtual environments much faster than venv
            const command = `uv venv ${this.status.venvPath} --python 3.11`;
            
            this.logger.info('Creating virtual environment with UV...');
            exec(command, { cwd: extensionPath }, (error: any, stdout: string, stderr: string) => {
                if (error) {
                    reject(new Error(`Failed to create virtual environment: ${stderr}`));
                } else {
                    this.logger.info('Virtual environment created successfully');
                    resolve();
                }
            });
        });
    }

    private async installDependencies(): Promise<void> {
        const { exec } = require('child_process');
        const extensionPath = this.context.extensionPath;
        
        return new Promise((resolve, reject) => {
            // UV installs dependencies in parallel and uses a global cache
            const command = `uv pip install -r python/requirements.txt`;
            
            this.logger.info('Installing dependencies with UV (this is much faster)...');
            exec(command, { 
                cwd: extensionPath,
                env: {
                    ...process.env,
                    VIRTUAL_ENV: this.status.venvPath
                }
            }, (error: any, stdout: string, stderr: string) => {
                if (error) {
                    reject(new Error(`Failed to install dependencies: ${stderr}`));
                } else {
                    this.logger.info('Dependencies installed successfully');
                    resolve();
                }
            });
        });
    }

    private async startBackendProcess(): Promise<void> {
        const { spawn } = require('child_process');
        
        // Get Python executable from UV venv
        const pythonExe = process.platform === 'win32' 
            ? path.join(this.status.venvPath, 'Scripts', 'python.exe')
            : path.join(this.status.venvPath, 'bin', 'python');
        
        const backendScript = path.join(this.context.extensionPath, 'python', 'server.py');
        
        if (!fs.existsSync(pythonExe)) {
            throw new Error(`Python executable not found: ${pythonExe}`);
        }
        
        if (!fs.existsSync(backendScript)) {
            throw new Error(`Backend script not found: ${backendScript}`);
        }

        this.backendProcess = spawn(pythonExe, [backendScript], {
            stdio: ['pipe', 'pipe', 'pipe'],
            cwd: path.join(this.context.extensionPath, 'python'),
            env: {
                ...process.env,
                VIRTUAL_ENV: this.status.venvPath,
                PATH: `${path.dirname(pythonExe)}${path.delimiter}${process.env.PATH}`
            }
        });

        // Handle process events
        this.backendProcess.stdout?.on('data', (data: Buffer) => {
            this.logger.info(`Backend stdout: ${data.toString().trim()}`);
        });

        this.backendProcess.stderr?.on('data', (data: Buffer) => {
            this.logger.warn(`Backend stderr: ${data.toString().trim()}`);
        });

        this.backendProcess.on('error', (error: Error) => {
            this.logger.error('Backend process error:', error);
            this.status.isRunning = false;
            this.status.lastError = error.message;
        });

        this.backendProcess.on('exit', (code: number) => {
            this.logger.info(`Backend process exited with code ${code}`);
            this.status.isRunning = false;
        });

        this.status.pid = this.backendProcess.pid;
    }

    private async waitForBackend(): Promise<void> {
        const maxAttempts = 30;
        const delay = 1000;
        
        for (let attempt = 1; attempt <= maxAttempts; attempt++) {
            try {
                await this.httpClient.get('/health');
                this.logger.info('Backend health check passed');
                return;
            } catch (error) {
                if (attempt === maxAttempts) {
                    throw new Error('Backend failed to start - health check timeout');
                }
                
                this.logger.info(`Health check attempt ${attempt}/${maxAttempts} failed, retrying...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    // Reuse API methods from PythonService
    async getFileInfo(filePath: string): Promise<any> {
        try {
            const response = await this.httpClient.post('/files/info', {
                file_path: filePath
            });
            return response.data;
        } catch (error) {
            this.logger.error('Failed to get file info:', error);
            throw error;
        }
    }

    async getSignals(filePath: string): Promise<any> {
        try {
            const response = await this.httpClient.post('/signals', {
                file_path: filePath
            });
            return response.data;
        } catch (error) {
            this.logger.error('Failed to get signals:', error);
            throw error;
        }
    }

    async getSignalData(filePath: string, signals: string[], startTime?: number, endTime?: number): Promise<any> {
        try {
            const response = await this.httpClient.post('/data', {
                file_path: filePath,
                signals,
                start_time: startTime,
                end_time: endTime
            });
            return response.data;
        } catch (error) {
            this.logger.error('Failed to get signal data:', error);
            throw error;
        }
    }

    async stopBackend(): Promise<void> {
        if (!this.status.isRunning || !this.backendProcess) {
            return;
        }

        try {
            this.logger.info('Stopping UV backend...');
            this.backendProcess.kill('SIGTERM');
            
            await new Promise(resolve => {
                this.backendProcess.on('exit', resolve);
                setTimeout(resolve, 5000);
            });

            this.status.isRunning = false;
            this.status.pid = undefined;
            this.logger.info('Backend stopped successfully');

        } catch (error) {
            this.logger.error('Error stopping backend:', error);
        }
    }

    getStatus(): UVBackendStatus {
        return { ...this.status };
    }
} 