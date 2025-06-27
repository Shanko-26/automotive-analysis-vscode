# Epic 2: Signal Management & Visualization

## Overview
Implement the signal explorer interface and interactive plotting capabilities using Bokeh, enabling users to browse signals and create time-series visualizations.

## User Stories

### 2.1 Signal Explorer TreeView
**As an** automotive engineer  
**I want to** browse available signals in a tree structure  
**So that** I can easily find and select signals for analysis

**Acceptance Criteria:**
- VS Code TreeView showing all available signals
- Hierarchical grouping by ECU/category
- Expand/collapse functionality
- Signal count indicators per group
- Refresh capability

### 2.2 Signal Search and Filter
**As a** user  
**I want to** search and filter signals by name or property  
**So that** I can quickly find specific measurements

**Acceptance Criteria:**
- Real-time search as you type
- Filter by signal name, unit, or description
- Regular expression support
- Clear filter button
- Search history

### 2.3 Signal Metadata Display
**As an** engineer  
**I want to** see detailed signal information  
**So that** I can understand data characteristics before plotting

**Acceptance Criteria:**
- Display unit, sample rate, min/max values
- Show signal data type and bit length
- ECU source information
- Total sample count
- Time range covered

### 2.4 Bokeh Plot Integration
**As a** developer  
**I want to** integrate Bokeh plotting in VS Code webview  
**So that** users can visualize data interactively

**Acceptance Criteria:**
- Bokeh server integration with Python backend
- Webview displaying Bokeh plots
- Proper resize handling
- Dark/light theme support
- WebSocket communication established

### 2.5 Interactive Time Series Plotting
**As a** user  
**I want to** create interactive time series plots  
**So that** I can analyze measurement data visually

**Acceptance Criteria:**
- Click signal in explorer to add to plot
- Pan and zoom with mouse/touch
- Hover tooltips showing exact values
- Time axis synchronization
- Responsive performance with 100k+ points

### 2.6 Multi-Signal Visualization
**As an** engineer  
**I want to** plot multiple signals together  
**So that** I can analyze correlations and relationships

**Acceptance Criteria:**
- Add multiple signals to same plot
- Y-axis management (shared/separate)
- Different colors per signal
- Legend with signal names
- Hide/show individual signals

### 2.7 Plot Export and Sharing
**As a** user  
**I want to** export plots as images  
**So that** I can include them in reports

**Acceptance Criteria:**
- Export as PNG/SVG
- Configurable resolution
- Include title and labels
- Copy to clipboard option
- Save plot configuration

### 2.8 Plot Session Management
**As a** developer  
**I want to** implement stateful plot sessions  
**So that** collaborative features can be added later

**Acceptance Criteria:**
- Unique session IDs
- Session state persistence
- Plot configuration storage
- Signal data caching
- Session cleanup on close

## Technical Requirements

### Extension Components
```typescript
// Signal Explorer Provider
class SignalTreeProvider implements vscode.TreeDataProvider<SignalItem> {
    signals: Map<string, Signal>;
    filter: string;
    groupBy: 'ecu' | 'category' | 'flat';
}

// Plot Webview Manager
class PlotWebviewProvider implements vscode.WebviewViewProvider {
    bokehServerUrl: string;
    sessionId: string;
    activePlot: BokehPlot;
}
```

### Python Plot Manager
```python
class PlotSession:
    id: str
    figure: bokeh.plotting.figure
    data_sources: Dict[str, ColumnDataSource]
    signals: Dict[str, np.ndarray]
    timestamps: np.ndarray
    config: PlotConfiguration
    
class PlotManager:
    sessions: Dict[str, PlotSession]
    def create_session() -> str
    def add_signal(session_id: str, signal_data: SignalData)
    def update_plot(session_id: str, config: PlotConfiguration)
    def export_plot(session_id: str, format: str) -> bytes
```

### REST Endpoints
- `POST /plot/session` - Create new plot session
- `POST /plot/{session_id}/signals` - Add signals to plot
- `GET /plot/{session_id}/state` - Get current plot state
- `PUT /plot/{session_id}/config` - Update plot configuration
- `GET /plot/{session_id}/export` - Export plot image

## Testing Requirements
- Signal tree navigation tests
- Search/filter functionality tests
- Plot rendering tests with various data sizes
- Multi-signal synchronization tests
- Export functionality tests
- Memory leak tests for sessions
- WebSocket stability tests

## Dependencies
- Epic 1 completion (backend service running)
- Bokeh server integration
- WebView API understanding

## Definition of Done
- [ ] All user stories completed
- [ ] Bokeh plots rendering in VS Code
- [ ] Signal explorer fully functional
- [ ] Export capabilities working
- [ ] Performance targets met (100k points smooth)
- [ ] Memory usage acceptable
- [ ] Cross-platform tested

## Estimated Effort
- **Total Points**: 34
- **Duration**: 1.5 weeks
- **Dependencies**: Epic 1

## Risks
- Bokeh server integration complexity
- WebView communication reliability
- Memory usage with multiple large plots
- Performance with high-frequency signals
- Theme compatibility issues