# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a VS Code extension project for automotive measurement data analysis, specifically designed for steering system engineers. The project analyzes MDF/BLF files containing automotive measurement data and provides AI-powered collaborative plotting and requirement validation.

**Current Status**: Planning phase - extensive documentation exists but no implementation code yet.

## Architecture

The system follows a multi-tier architecture:

### VS Code Extension (TypeScript)
- **File Handler**: Detects .mdf, .mf4, .blf, .asc files and shows metadata
- **Signal Explorer**: TreeView provider for browsing available signals
- **Plot Webview**: Displays Bokeh-generated interactive plots
- **AI Integration Layer**: Abstracts between GitHub Copilot, Claude, or local LLMs

### Python Backend (FastAPI)
- **Data Parsers**: Uses `asammdf` for MDF files, `python-can` for BLF files
- **Plot Manager**: Bokeh-based plotting with stateful session management
- **Analysis Engine**: Signal filtering, anomaly detection, correlation analysis
- **REST API**: Endpoints for file operations, signal data, and plot sessions

### Key Integration Points
- AI providers communicate via standardized `AIProvider` interface
- Plot sessions maintain state for collaborative user/AI interactions
- WebSocket communication enables real-time plot updates
- All data processing happens locally (no external data transmission)

## Development Workflow

### Project Structure (Planned)
```
src/                    # TypeScript extension code
python/                 # FastAPI backend
webview/               # Plot interface components
tasks/                 # Epic breakdowns and user stories
```

### Epic Dependencies
Development follows this sequence:
1. **Epic 1**: Core infrastructure and file handling
2. **Epic 2**: Signal management and Bokeh visualization  
3. **Epic 3**: AI integration with natural language commands
4. **Epic 4**: Advanced analysis (filtering, FFT, anomaly detection)
5. **Epic 5**: Requirements validation and reporting
6. **Epic 6**: Steering-specific templates and workflows

### AI Provider Abstraction
The extension supports multiple AI providers through a common interface:
- **Primary**: GitHub Copilot Chat API (for target deployment)
- **Development**: Claude via Claude Code  
- **Fallbacks**: Direct API calls, local LLMs (Ollama)

Example AI command: "Apply 5Hz lowpass filter to steering angle signal"

## Performance Requirements

- Parse 1GB+ MDF files within 5 seconds using data chunking
- Maintain <500ms latency for collaborative AI plotting
- Handle 100k+ data points smoothly in interactive plots
- Achieve 90%+ accuracy for natural language command interpretation

## Domain-Specific Context

### Steering System Signals
Signals are auto-categorized into:
- **Input**: SteeringWheelAngle, HandWheelTorque, DriverTorque
- **Assist**: AssistTorque, MotorCurrent, MotorVoltage  
- **Vehicle**: VehicleSpeed, YawRate, LateralAcceleration
- **Active Return**: ActiveReturnTorque, ActiveReturnStatus
- **System**: EPSStatus, ColumnTorque, RackForce

### Standard Analysis Templates
- On-center feel analysis (hysteresis, friction, dead-zone)
- Parking maneuver validation (torque limits, current consumption)
- Active return compliance (return rates, overshoot detection)
- NVH analysis (FFT, vibration frequencies, torque ripple)

## Key Technical Decisions

- **Bokeh over Plotly/Altair**: Server-side rendering handles large datasets better
- **FastAPI over Flask**: Async capabilities and automatic API documentation
- **Local-first processing**: All measurement data stays on machine for security
- **Multi-AI provider support**: Ensures extension works in different environments

## Development Environment Considerations

The extension is designed to work in both development (Cursor + Claude Code) and target environments (VS Code + GitHub Copilot). The AI provider abstraction ensures seamless operation across environments.