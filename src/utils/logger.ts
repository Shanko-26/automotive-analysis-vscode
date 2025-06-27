import * as vscode from 'vscode';

export class Logger {
    private readonly outputChannel: vscode.OutputChannel;
    private readonly context: string;

    constructor(context: string) {
        this.context = context;
        this.outputChannel = vscode.window.createOutputChannel('Automotive Analysis');
    }

    info(message: string, data?: any): void {
        this.log('INFO', message, data);
    }

    warn(message: string, data?: any): void {
        this.log('WARN', message, data);
    }

    error(message: string, error?: any): void {
        this.log('ERROR', message, error);
    }

    debug(message: string, data?: any): void {
        this.log('DEBUG', message, data);
    }

    private log(level: string, message: string, data?: any): void {
        const timestamp = new Date().toISOString();
        const logEntry = {
            timestamp,
            level,
            context: this.context,
            message,
            data: data || null
        };

        const formattedMessage = `[${timestamp}] ${level} [${this.context}] ${message}`;
        this.outputChannel.appendLine(formattedMessage);

        if (data) {
            this.outputChannel.appendLine(JSON.stringify(data, null, 2));
        }
    }

    show(): void {
        this.outputChannel.show();
    }

    dispose(): void {
        this.outputChannel.dispose();
    }
} 