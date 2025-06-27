# Automotive Measurement Analysis VS Code Extension

An AI-powered VS Code extension for analyzing automotive measurement data (MDF/BLF files) with collaborative plotting and requirement validation, specifically designed for steering system engineers.

## Features

### Epic 1: Core Infrastructure & File Handling ✅
- **File Detection**: Automatic detection of `.mdf`, `.mf4`, `.blf`, `.asc` files with custom icons
- **File Metadata**: Hover preview showing file size, duration, signal count, and recording date
- **Multi-Backend Architecture**: 🐳 Docker, ⚡ UV, 🐍 Python backends with intelligent auto-selection
- **REST API**: Endpoints for file info, signal listing, and data retrieval
- **Memory Efficient**: Data chunking for handling 1GB+ files

### Planned Features (Epics 2-6)
- **Epic 2**: Signal management and Bokeh visualization
- **Epic 3**: AI integration with natural language commands
- **Epic 4**: Advanced analysis (filtering, FFT, anomaly detection)
- **Epic 5**: Requirements validation and reporting
- **Epic 6**: Steering-specific templates and workflows

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   VS Code       │    │   Multi-Backend │    │   Measurement   │
│   Extension     │◄──►│   Manager       │◄──►│   Files         │
│   (TypeScript)  │    │   (Auto-Select) │    │   (MDF/BLF)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
        │   🐳 Docker  │ │   ⚡ UV      │ │ 🐍 Python  │
        │   Backend    │ │   Backend   │ │  Backend   │
        │ (Reliable)   │ │ (Fast)      │ │ (Compat)   │
        └──────────────┘ └─────────────┘ └────────────┘
```

### Backend Options
- **🐳 Docker Backend**: Containerized, most reliable, zero Python setup
- **⚡ UV Backend**: Ultra-fast Python package manager, rapid installation  
- **🐍 Python Backend**: Traditional approach, maximum compatibility
- **🤖 Auto-Selection**: Automatically chooses the best available backend

## Installation

### Prerequisites
- VS Code 1.85.0 or later
- **Optional**: Docker Desktop (recommended for best experience)
- **Optional**: Python 3.11+ (for traditional backend)

### Quick Setup

**Linux/macOS**:
```bash
git clone <repository-url>
cd mesaic
chmod +x install.sh
./install.sh
```

**Windows**:
```cmd
git clone <repository-url>
cd mesaic
install.bat
```

This automatically:
- Installs Node.js dependencies
- Compiles the extension  
- Packages and installs it in VS Code
- Sets up the optimal backend for your system

### Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mesaic
   ```

2. **Install and compile**
   ```bash
   npm install
   npm run compile
   npx vsce package --no-dependencies
   code --install-extension automotive-analysis-0.1.0.vsix
   ```

3. **Restart VS Code** - The extension will auto-select the best backend

## Usage

### Basic Workflow

1. **Open a measurement file**
   - Navigate to an `.mdf`, `.mf4`, `.blf`, or `.asc` file in VS Code
   - Hover over the file to see metadata preview
   - Right-click and select "Open in Analysis View"

2. **Backend management** (automatic)
   - Extension tries Docker → UV → Python automatically
   - Use "Switch Backend Type" to manually select
   - Check "Show Backend Status" for current state

3. **View file information**
   - File metadata panel shows size, duration, signal count
   - Available signals are listed with units and sample rates

4. **Browse signals**
   - Use "Show Available Signals" command
   - Search and filter signals by name
   - Click signals to add them to plots (Epic 2)

### Commands

Access via `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac):

- **Start Backend** - Start the optimal backend
- **Stop Backend** - Stop the current backend
- **Switch Backend Type** - Choose Docker/UV/Python manually
- **Show Backend Status** - Check current backend info
- **Troubleshooting Guide** - Built-in help and solutions

### Configuration

The extension can be configured through VS Code settings:

```json
{
  "automotiveAnalysis.backendType": "auto",
  "automotiveAnalysis.backendPort": 8000,
  "automotiveAnalysis.autoStartBackend": true,
  "automotiveAnalysis.maxFileSize": 1073741824,
  "automotiveAnalysis.dockerImage": "automotive-analysis-backend"
}
```

## Development

### Project Structure
```
mesaic/
├── src/                    # TypeScript extension code
│   ├── extension.ts        # Main entry point
│   ├── backendManager.ts   # Multi-backend orchestration
│   ├── dockerService.ts    # Docker backend service
│   ├── uvService.ts        # UV backend service
│   ├── pythonService.ts    # Traditional Python backend
│   ├── fileHandler.ts      # File detection and metadata
│   └── utils/
│       └── logger.ts       # Logging utilities
├── python/                 # FastAPI backend
│   ├── server.py           # Main server
│   ├── parsers/            # File parsers
│   ├── models/             # Data models
│   └── utils/              # Utilities
├── Dockerfile             # Docker backend image
├── pyproject.toml         # UV/modern Python config
├── scripts/               # Build and deployment scripts
├── install.sh/.bat        # Installation scripts
└── package.json           # Extension manifest
```

### Development Commands

```bash
# Compile TypeScript
npm run compile

# Watch for changes
npm run watch

# Run tests
npm test

# Build Docker image
docker build -t automotive-analysis-backend .

# Start Python backend manually
cd python
python server.py
```

### API Endpoints

The backend provides these REST endpoints (all backends):

- `GET /health` - Health check
- `POST /files/info` - Get file metadata
- `POST /signals` - Get available signals
- `POST /data` - Get signal data for time range

### Testing

```bash
# Run Python tests
cd python
pytest

# Run extension tests
npm test
```

## Performance

### Targets
- **File Parsing**: 1GB+ MDF files within 5 seconds
- **API Response**: <500ms for typical queries
- **Memory Usage**: Efficient chunking for large datasets
- **Cross-Platform**: Windows, macOS, Linux support

### Backend Performance
- **🐳 Docker**: Most reliable, consistent performance across platforms
- **⚡ UV**: Fastest installation, modern Python package management
- **🐍 Python**: Traditional approach, maximum compatibility

## Supported File Formats

### MDF/MF4 Files
- **Format**: MDF3 and MDF4 measurement data files
- **Parser**: `asammdf` library
- **Features**: Full signal extraction, metadata, time series data

### BLF/ASC Files
- **Format**: CAN bus log files (Binary Logging Format, ASCII)
- **Parser**: `python-can` library
- **Features**: CAN message extraction, ID-based signal grouping

## Troubleshooting

### Quick Help
Use the built-in troubleshooting guide:
1. Press `Ctrl+Shift+P`
2. Run "Automotive Analysis: Troubleshooting Guide"
3. Follow the step-by-step instructions

### Backend-Specific Issues

**Docker Backend**:
- Install Docker Desktop
- Ensure Docker daemon is running
- Check Docker is in PATH

**UV Backend**:
- UV auto-installs when needed
- Manual install: `curl -LsSf https://astral.sh/uv/install.sh | sh`

**Python Backend**:
- Use Python 3.11 or 3.12
- Run: `python setup.py` for manual dependency installation

### Common Issues

1. **Backend won't start**
   - Use "Switch Backend Type" to try different options
   - Check "Show Backend Status" for error details
   - Run "Troubleshooting Guide" for specific solutions

2. **Port conflicts**
   - Change `automotiveAnalysis.backendPort` in settings
   - Kill existing processes: `lsof -ti:8000 | xargs kill`

3. **File parsing errors**
   - Ensure file is not corrupted
   - Check file permissions
   - Verify file format is supported

## Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**: Follow the coding standards
4. **Add tests**: Ensure your changes are tested
5. **Submit a pull request**: Describe your changes clearly

## License

This project is licensed under the MIT License.

---

**Made with ❤️ for automotive engineers**

*Now with intelligent multi-backend support for the best possible user experience!* 