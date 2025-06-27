# Automotive Measurement Analysis VS Code Extension - Product Requirements Document

## Project Overview
Build a VS Code extension that enables automotive engineers to analyze measurement data (MDF/BLF files) directly in their IDE, with AI-powered collaborative plotting and insights for steering system analysis and requirement validation.

## Core Objectives
1. Provide seamless integration of measurement data analysis within VS Code
2. Enable collaborative plotting where users and AI work together on visualizations
3. Leverage existing AI tools (GitHub Copilot, Claude) without requiring additional installations
4. Automate requirement validation and report generation
5. Start with steering system analysis, expandable to other automotive domains

## Technical Architecture

### Extension Components
1. **File Handler Service**
   - Detect and preview MDF/BLF files in VS Code explorer
   - Display file metadata (size, duration, signal count)
   - Custom icons for measurement files

2. **Python Backend Service**
   - FastAPI server running locally
   - Uses `asammdf` for MDF file parsing
   - Uses `python-can` for BLF file parsing
   - Provides REST API for data operations
   - Stateful plot session management

3. **Signal Explorer View**
   - VS Code TreeView showing available signals
   - Group signals by ECU/category
   - Quick search/filter functionality
   - Signal metadata display (unit, sample rate, min/max)
   - Click to add signals to active plot

4. **Collaborative Plot Manager**
   - Bokeh-based interactive visualizations
   - Stateful sessions maintaining plot context
   - Operation history tracking
   - Support for both user and AI modifications

5. **AI Integration Layer**
   - Primary: GitHub Copilot Chat API (existing setup)
   - Fallback: Direct API calls or local LLMs
   - No dependency on Claude Code installation
   - Natural language command processing

### Visualization Architecture

```python
# Bokeh-based plotting with collaborative features
class PlotSession:
    id: str
    figure: bokeh.plotting.figure
    data_sources: Dict[str, ColumnDataSource]
    signals: Dict[str, np.ndarray]
    timestamps: np.ndarray
    history: List[Dict[str, Any]]  # Track all operations
```

## Feature Specifications

### Phase 1: MVP (Week 1-2)
1. **File Detection & Preview**
   - Register file associations for .mdf, .mf4, .blf, .asc files
   - Show file info on hover
   - "Open in Analysis View" command

2. **Basic Signal Viewer**
   - List all signals with search
   - Display signal properties
   - Click to add to plot

3. **Interactive Plotting with Bokeh**
   - Time series plots with pan/zoom
   - Hover tooltips showing values
   - Multi-signal synchronized views
   - Export plot as image

4. **Python Backend**
   - REST endpoints: `/files`, `/signals`, `/data`, `/plot/session`
   - Efficient data chunking for large files
   - Plot session management

### Phase 2: Collaborative AI Plotting (Week 3-4)
1. **Natural Language Commands**
   - Integration with GitHub Copilot Chat
   - Command examples:
     - "Add filtered engine speed signal"
     - "Apply 5Hz lowpass to steering angle"
     - "Show correlation between torque and speed"
   - Generate Python/action from natural language

2. **Stateful Plot Sessions**
   - Maintain plot state across operations
   - Track user vs AI actions
   - Undo/redo functionality
   - Session persistence

3. **AI-Assisted Analysis**
   - Signal filtering (butterworth, moving average)
   - Derived signals (math expressions)
   - Anomaly detection
   - Correlation analysis

### Phase 3: Advanced Features (Week 5-6)
1. **Requirement Validation**
   - YAML/JSON requirement parser
   - Automatic validation against data
   - Violation highlighting in plots
   - Compliance reporting

2. **Report Generation**
   - Markdown reports with embedded plots
   - Requirement compliance summary
   - Export to PDF/PowerPoint

3. **Steering-Specific Templates**
   - On-center feel analysis
   - Parking maneuver validation
   - Active return compliance
   - NVH analysis

## Implementation Details

### VS Code Extension Structure
```
automotive-analysis/
├── src/
│   ├── extension.ts          # Main extension entry
│   ├── fileExplorer.ts       # File detection/preview
│   ├── signalExplorer.ts     # TreeView provider
│   ├── plotWebview.ts        # Bokeh plot interface
│   ├── aiIntegration.ts      # Copilot/AI integration
│   ├── plotManager.ts        # Plot session management
│   └── pythonService.ts      # Backend communication
├── python/
│   ├── server.py             # FastAPI server
│   ├── mdf_parser.py         # MDF handling
│   ├── blf_parser.py         # BLF handling
│   ├── plot_manager.py       # Bokeh plotting
│   ├── ai_assistant.py       # AI command processing
│   └── analysis.py           # Analysis functions
├── webview/
│   ├── index.html            # Plot interface
│   ├── plot.js               # Bokeh integration
│   └── collaborative.js      # User/AI interaction
└── package.json              # Extension manifest
```

### AI Integration Without Claude Code

```typescript
// Multiple AI provider support
export interface AIProvider {
    processCommand(command: string, context: PlotContext): Promise<PlotAction>;
}

class CopilotChatProvider implements AIProvider {
    async processCommand(command: string, context: PlotContext) {
        // Use GitHub Copilot Chat API
        return await vscode.chat.sendRequest({
            prompt: `Convert to plot action: ${command}`,
            model: 'claude-3-sonnet'
        });
    }
}

class APIProvider implements AIProvider {
    // Direct API calls as fallback
}

class LocalLLMProvider implements AIProvider {
    // Ollama or similar for offline use
}
```

### Collaborative Plotting Workflow

1. **User-Initiated Actions**
   - Click signals in explorer to add to plot
   - Use toolbar for zoom/pan operations
   - Right-click context menus for common actions

2. **AI-Assisted Actions**
   - Natural language command input
   - AI interprets and executes plot modifications
   - Results shown immediately in plot

3. **Example Interaction Flow**
   ```
   User: [Clicks "SteeringAngle" in signal browser]
   Plot: Adds steering angle time series
   
   User: "Apply lowpass filter to remove noise above 5Hz"
   AI: Generates filter parameters, adds filtered signal in red
   
   User: "Why is there oscillation at 14:23?"
   AI: Analyzes frequency, adds relevant signals for comparison
   ```

### Key Commands
- `automotive.openFile`: Open measurement file
- `automotive.addSignal`: Add signal to plot
- `automotive.aiCommand`: Execute AI plotting command
- `automotive.validateRequirements`: Check requirements
- `automotive.generateReport`: Create analysis report
- `automotive.exportPlot`: Export current visualization

### Configuration Options
```json
{
  "automotive.pythonPath": "python",
  "automotive.serverPort": 8765,
  "automotive.visualization": {
    "library": "bokeh",
    "theme": "dark",
    "defaultHeight": 400,
    "defaultWidth": 800
  },
  "automotive.ai": {
    "provider": "auto",  // auto|copilot|api|local|none
    "apiEndpoint": "${env:AI_API_ENDPOINT}",
    "enableSuggestions": true,
    "commandTimeout": 30000
  }
}
```

## Steering-Specific Signal Detection
Automatically detect and categorize steering signals:
- **Input**: SteeringWheelAngle, HandWheelTorque, DriverTorque
- **Assist**: AssistTorque, MotorCurrent, MotorVoltage
- **Vehicle**: VehicleSpeed, YawRate, LateralAcceleration
- **Active Return**: ActiveReturnTorque, ActiveReturnStatus
- **System**: EPSStatus, ColumnTorque, RackForce

## Technical Decisions

### Visualization Library: Bokeh
- **Reasons**: Server-side architecture, handles large datasets, streaming support, excellent VS Code webview integration
- **Alternatives considered**: Plotly (larger bundle), Altair (better for static plots)

### AI Integration: GitHub Copilot Chat API
- **Reasons**: Already available in enterprise, no additional installations, supports Claude Sonnet
- **Fallback options**: Direct API calls, local LLMs for offline use

### Backend: Python with FastAPI
- **Reasons**: Native support for automotive file formats, scientific computing libraries, async capabilities

## Success Metrics
- Parse and display 1GB+ MDF files within 5 seconds
- Support collaborative plotting with <500ms latency
- Generate analysis code from natural language with 90%+ accuracy
- Reduce requirement validation time from hours to minutes
- Zero additional tool installations required

## Security & Compliance
- All data processing happens locally
- No measurement data sent to external services
- AI commands only send metadata (signal names, not values)
- Support for fully offline operation with local LLMs

## Future Expansion Paths
- Support for additional file formats (TDMS, MAT, CSV)
- Integration with calibration tools (INCA, CANape)
- Real-time data streaming support
- Multi-file comparison views
- Team collaboration via Live Share
- Domain expansion (powertrain, ADAS, chassis dynamics)

## Development Guidelines
- Use TypeScript for extension code
- Follow VS Code extension best practices
- Implement proper error handling for large files
- Cache parsed data for performance
- Use streaming for memory efficiency
- Provide clear user feedback during operations
- Maintain separation between UI and analysis logic

## Testing Requirements
- Unit tests for signal parsing and filtering
- Integration tests for AI commands
- Performance tests with large files (1GB+)
- Validation of requirement checking accuracy
- Cross-platform compatibility (Windows/Linux/Mac)
- AI provider fallback testing

## Delivery Timeline
- Week 1-2: Core file handling and basic plotting
- Week 3-4: Collaborative AI features
- Week 5-6: Advanced analysis and reporting
- Week 7-8: Testing and refinement
- Week 9-10: Documentation and deployment