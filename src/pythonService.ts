import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import axios, { AxiosInstance } from 'axios';
import { Logger } from './utils/logger';

export interface BackendStatus {
    isRunning: boolean;
    port: number;
    pid?: number;
    lastError?: string;
}

export class PythonService {
    private readonly logger: Logger;
    private readonly context: vscode.ExtensionContext;
    private backendProcess?: any;
    private httpClient: AxiosInstance;
    private status: BackendStatus;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.logger = new Logger('PythonService');
        this.status = { isRunning: false, port: 8000 };
        
        const config = vscode.workspace.getConfiguration('automotiveAnalysis');
        this.status.port = config.get('backendPort', 8000);
        
        this.httpClient = axios.create({
            baseURL: `http://localhost:${this.status.port}`,
            timeout: 5000
        });
    }

    async startBackend(): Promise<void> {
        if (this.status.isRunning) {
            this.logger.info('Backend is already running');
            return;
        }

        try {
            this.logger.info('Starting Python backend...');
            
            // Get Python executable path
            const pythonPath = await this.getPythonPath();
            if (!pythonPath) {
                throw new Error('Python not found. Please install Python 3.11+ and ensure it\'s in PATH.');
            }

            // Check and install dependencies if needed
            await this.ensureDependencies(pythonPath);

            // Get backend script path
            const backendScript = path.join(this.context.extensionPath, 'python', 'server.py');
            if (!fs.existsSync(backendScript)) {
                throw new Error(`Backend script not found: ${backendScript}`);
            }

            // Start backend process
            const { spawn } = require('child_process');
            const packagesDir = path.join(this.context.extensionPath, 'python_packages');
            const pythonDir = path.join(this.context.extensionPath, 'python');
            
            const pythonEnv = {
                ...process.env,
                PYTHONPATH: `${packagesDir}${path.delimiter}${pythonDir}${path.delimiter}${process.env.PYTHONPATH || ''}`,
                PYTHONUSERBASE: this.context.extensionPath
            };

            this.backendProcess = spawn(pythonPath, [backendScript], {
                stdio: ['pipe', 'pipe', 'pipe'],
                env: pythonEnv,
                cwd: pythonDir
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

            // Wait for backend to start
            await this.waitForBackend();
            
            this.status.isRunning = true;
            this.status.pid = this.backendProcess.pid;
            this.logger.info(`Backend started successfully on port ${this.status.port}`);

        } catch (error) {
            this.logger.error('Failed to start backend:', error);
            this.status.lastError = error instanceof Error ? error.message : String(error);
            throw error;
        }
    }

    async stopBackend(): Promise<void> {
        if (!this.status.isRunning || !this.backendProcess) {
            return;
        }

        try {
            this.logger.info('Stopping Python backend...');
            this.backendProcess.kill('SIGTERM');
            
            // Wait for graceful shutdown
            await new Promise(resolve => {
                this.backendProcess.on('exit', resolve);
                setTimeout(resolve, 5000); // Force kill after 5s
            });

            this.status.isRunning = false;
            this.status.pid = undefined;
            this.logger.info('Backend stopped successfully');

        } catch (error) {
            this.logger.error('Error stopping backend:', error);
        }
    }

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

    getStatus(): BackendStatus {
        return { ...this.status };
    }

    private async getPythonPath(): Promise<string | null> {
        try {
            const { exec } = require('child_process');
            return new Promise((resolve) => {
                exec('python --version', (error: any, stdout: string) => {
                    if (error) {
                        exec('python3 --version', (error3: any, stdout3: string) => {
                            if (error3) {
                                resolve(null);
                            } else {
                                resolve('python3');
                            }
                        });
                    } else {
                        resolve('python');
                    }
                });
            });
        } catch (error) {
            return null;
        }
    }

    private async getPythonVersion(pythonPath: string): Promise<number> {
        try {
            const { exec } = require('child_process');
            return new Promise((resolve) => {
                exec(`${pythonPath} --version`, (error: any, stdout: string) => {
                    if (error) {
                        resolve(3.11); // Default fallback
                    } else {
                        // Parse version from "Python 3.12.0" format
                        const match = stdout.match(/Python (\d+\.\d+)/);
                        if (match) {
                            resolve(parseFloat(match[1]));
                        } else {
                            resolve(3.11); // Default fallback
                        }
                    }
                });
            });
        } catch (error) {
            return 3.11; // Default fallback
        }
    }

    private async waitForBackend(): Promise<void> {
        const maxAttempts = 30;
        const delay = 1000;

        for (let attempt = 0; attempt < maxAttempts; attempt++) {
            try {
                await this.httpClient.get('/health');
                return;
            } catch (error) {
                if (attempt === maxAttempts - 1) {
                    throw new Error('Backend failed to start within timeout');
                }
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }

    private async ensureDependencies(pythonPath: string): Promise<void> {
        try {
            this.logger.info('Checking Python dependencies...');
            
            // Check if uvicorn is available
            const { exec } = require('child_process');
            const packagesDir = path.join(this.context.extensionPath, 'python_packages');
            const pythonDir = path.join(this.context.extensionPath, 'python');
            
            const checkUvicorn = new Promise<boolean>((resolve) => {
                const env = {
                    ...process.env,
                    PYTHONPATH: `${packagesDir}${path.delimiter}${pythonDir}${path.delimiter}${process.env.PYTHONPATH || ''}`
                };
                
                exec(`${pythonPath} -c "import uvicorn; print('OK')"`, { env }, (error: any) => {
                    resolve(!error);
                });
            });

            const uvicornAvailable = await checkUvicorn;
            
            if (!uvicornAvailable) {
                this.logger.info('Installing Python dependencies...');
                
                // Detect Python version to use the right requirements file
                const pythonVersion = await this.getPythonVersion(pythonPath);
                const requirementsFile = pythonVersion >= 3.12 ? 'requirements-py312.txt' : 'requirements.txt';
                this.logger.info(`Detected Python ${pythonVersion}, using ${requirementsFile}`);
                
                // Try to install dependencies in the extension directory
                const requirementsPath = path.join(this.context.extensionPath, 'python', requirementsFile);
                const installTarget = path.join(this.context.extensionPath, 'python_packages');
                
                // Create python_packages directory if it doesn't exist
                if (!fs.existsSync(installTarget)) {
                    fs.mkdirSync(installTarget, { recursive: true });
                }

                const installPromise = new Promise<void>((resolve, reject) => {
                    const installProcess = exec(
                        `${pythonPath} -m pip install -r "${requirementsPath}" --target "${installTarget}" --no-cache-dir`,
                        { cwd: path.join(this.context.extensionPath, 'python') },
                        (error: any, stdout: string, stderr: string) => {
                            if (error) {
                                this.logger.error(`Pip install failed: ${error.message}`);
                                this.logger.error(`Stdout: ${stdout}`);
                                this.logger.error(`Stderr: ${stderr}`);
                                reject(new Error(`Failed to install dependencies: ${error.message}`));
                            } else {
                                this.logger.info('Dependencies installed successfully');
                                resolve();
                            }
                        }
                    );

                    installProcess.stdout?.on('data', (data: Buffer) => {
                        this.logger.info(`Pip stdout: ${data.toString().trim()}`);
                    });

                    installProcess.stderr?.on('data', (data: Buffer) => {
                        this.logger.info(`Pip stderr: ${data.toString().trim()}`);
                    });
                });

                await installPromise;
            } else {
                this.logger.info('Python dependencies are already available');
            }
            
        } catch (error) {
            this.logger.error('Failed to ensure dependencies:', error);
            
            // Detect Python version for error message
            const pythonVersion = await this.getPythonVersion(pythonPath);
            const requirementsFile = pythonVersion >= 3.12 ? 'requirements-py312.txt' : 'requirements.txt';
            
            // Show user-friendly error message
            const message = `Failed to install Python dependencies. Please run the following commands manually:\n\n` +
                           `cd "${path.join(this.context.extensionPath, 'python')}"\n` +
                           `python -m pip install -r ${requirementsFile}\n\n` +
                           'Then restart the extension.';
            
            vscode.window.showErrorMessage(message, 'Copy Commands').then(selection => {
                if (selection === 'Copy Commands') {
                    vscode.env.clipboard.writeText(
                        `cd "${path.join(this.context.extensionPath, 'python')}"\n` +
                        `python -m pip install -r ${requirementsFile}`
                    );
                }
            });
            
            throw error;
        }
    }

    dispose(): void {
        this.stopBackend();
        this.logger.dispose();
    }
} 