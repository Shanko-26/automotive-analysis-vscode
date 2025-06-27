import * as vscode from 'vscode';
import * as path from 'path';
import axios, { AxiosInstance } from 'axios';
import { Logger } from './utils/logger';

export interface DockerBackendStatus {
    isRunning: boolean;
    containerName: string;
    port: number;
    lastError?: string;
}

export class DockerService {
    private readonly logger: Logger;
    private readonly context: vscode.ExtensionContext;
    private httpClient: AxiosInstance;
    private status: DockerBackendStatus;
    private readonly containerName = 'automotive-analysis-backend';

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.logger = new Logger('DockerService');
        this.status = { 
            isRunning: false, 
            containerName: this.containerName,
            port: 8000 
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
            this.logger.info('Docker backend is already running');
            return;
        }

        try {
            this.logger.info('Starting Docker backend...');
            
            // Check if Docker is available
            await this.checkDockerAvailability();
            
            // Stop existing container if any
            await this.stopExistingContainer();
            
            // Build image if needed
            await this.buildImageIfNeeded();
            
            // Start container
            await this.startContainer();
            
            // Wait for health check
            await this.waitForHealthCheck();
            
            this.status.isRunning = true;
            this.logger.info(`Docker backend started successfully on port ${this.status.port}`);
            
        } catch (error) {
            this.logger.error('Failed to start Docker backend:', error);
            this.status.lastError = error instanceof Error ? error.message : String(error);
            throw error;
        }
    }

    async stopBackend(): Promise<void> {
        if (!this.status.isRunning) {
            return;
        }

        try {
            this.logger.info('Stopping Docker backend...');
            
            const { exec } = require('child_process');
            await new Promise<void>((resolve, reject) => {
                exec(`docker stop ${this.containerName}`, (error: any, stdout: string, stderr: string) => {
                    if (error && !stderr.includes('No such container')) {
                        reject(error);
                    } else {
                        resolve();
                    }
                });
            });
            
            this.status.isRunning = false;
            this.logger.info('Docker backend stopped successfully');
            
        } catch (error) {
            this.logger.error('Error stopping Docker backend:', error);
        }
    }

    private async checkDockerAvailability(): Promise<void> {
        const { exec } = require('child_process');
        
        return new Promise((resolve, reject) => {
            exec('docker --version', (error: any, stdout: string) => {
                if (error) {
                    reject(new Error('Docker is not installed or not accessible. Please install Docker Desktop.'));
                } else {
                    this.logger.info(`Docker found: ${stdout.trim()}`);
                    resolve();
                }
            });
        });
    }

    private async stopExistingContainer(): Promise<void> {
        const { exec } = require('child_process');
        
        return new Promise<void>((resolve) => {
            exec(`docker stop ${this.containerName} && docker rm ${this.containerName}`, 
                (error: any, stdout: string, stderr: string) => {
                    // Ignore errors - container might not exist
                    resolve();
                });
        });
    }

    private async buildImageIfNeeded(): Promise<void> {
        const { exec } = require('child_process');
        const extensionPath = this.context.extensionPath;
        
        return new Promise((resolve, reject) => {
            const buildCommand = `docker build -t ${this.containerName} "${extensionPath}"`;
            
            this.logger.info('Building Docker image...');
            exec(buildCommand, { cwd: extensionPath }, (error: any, stdout: string, stderr: string) => {
                if (error) {
                    this.logger.error('Docker build failed:', stderr);
                    reject(new Error(`Docker build failed: ${stderr}`));
                } else {
                    this.logger.info('Docker image built successfully');
                    resolve();
                }
            });
        });
    }

    private async startContainer(): Promise<void> {
        const { exec } = require('child_process');
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        const workspacePath = workspaceFolder?.uri.fsPath || path.join(this.context.extensionPath, 'sampledata');
        
        const runCommand = [
            'docker run',
            '-d',
            `--name ${this.containerName}`,
            `-p ${this.status.port}:8000`,
            `-v "${workspacePath}:/data:ro"`,
            '--restart unless-stopped',
            this.containerName
        ].join(' ');
        
        return new Promise((resolve, reject) => {
            exec(runCommand, (error: any, stdout: string, stderr: string) => {
                if (error) {
                    this.logger.error('Failed to start Docker container:', stderr);
                    reject(new Error(`Failed to start container: ${stderr}`));
                } else {
                    this.logger.info(`Docker container started: ${stdout.trim()}`);
                    resolve();
                }
            });
        });
    }

    private async waitForHealthCheck(): Promise<void> {
        const maxAttempts = 30;
        const delay = 2000;
        
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

    // Reuse existing API methods from PythonService
    async getFileInfo(filePath: string): Promise<any> {
        try {
            // Convert local path to container path
            const containerPath = this.convertToContainerPath(filePath);
            const response = await this.httpClient.post('/files/info', {
                file_path: containerPath
            });
            return response.data;
        } catch (error) {
            this.logger.error('Failed to get file info:', error);
            throw error;
        }
    }

    async getSignals(filePath: string): Promise<any> {
        try {
            const containerPath = this.convertToContainerPath(filePath);
            const response = await this.httpClient.post('/signals', {
                file_path: containerPath
            });
            return response.data;
        } catch (error) {
            this.logger.error('Failed to get signals:', error);
            throw error;
        }
    }

    async getSignalData(filePath: string, signals: string[], startTime?: number, endTime?: number): Promise<any> {
        try {
            const containerPath = this.convertToContainerPath(filePath);
            const response = await this.httpClient.post('/data', {
                file_path: containerPath,
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

    private convertToContainerPath(localPath: string): string {
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (workspaceFolder) {
            const relativePath = path.relative(workspaceFolder.uri.fsPath, localPath);
            return path.posix.join('/data', relativePath.replace(/\\/g, '/'));
        }
        return path.posix.join('/data', path.basename(localPath));
    }

    getStatus(): DockerBackendStatus {
        return { ...this.status };
    }
} 