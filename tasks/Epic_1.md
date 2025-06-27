# Epic 1: Core Infrastructure & File Handling

## Overview
Establish the foundational infrastructure for the VS Code extension, including file detection, Python backend service, and basic extension setup.

## User Stories

### 1.1 Extension Setup and Configuration
**As a** developer  
**I want to** set up the VS Code extension project structure  
**So that** I have a solid foundation for building features

**Acceptance Criteria:**
- TypeScript project with proper VS Code extension structure
- Extension manifest (package.json) with proper metadata
- Basic activation events configured
- Extension commands registered
- Configuration schema defined

### 1.2 File Detection and Association
**As an** automotive engineer  
**I want to** see MDF/BLF files with custom icons in VS Code  
**So that** I can easily identify measurement files

**Acceptance Criteria:**
- Register file associations for .mdf, .mf4, .blf, .asc files
- Custom icons displayed in file explorer
- File detection works in workspace and folder views
- Quick file info available on hover

### 1.3 File Metadata Preview
**As an** engineer  
**I want to** see file metadata without opening the file  
**So that** I can quickly assess file contents

**Acceptance Criteria:**
- Display file size, duration, signal count on hover
- Show recording date and measurement system info
- Handle large files without performance impact
- Error handling for corrupted files

### 1.4 Python Backend Service Setup
**As a** developer  
**I want to** establish a Python FastAPI backend  
**So that** I can process automotive file formats

**Acceptance Criteria:**
- FastAPI server with proper project structure
- Auto-start with extension activation
- Health check endpoint
- Proper error handling and logging
- Cross-platform compatibility (Windows/Linux/Mac)

### 1.5 File Parsing Service
**As a** system component  
**I want to** parse MDF/BLF files efficiently  
**So that** I can provide data to the frontend

**Acceptance Criteria:**
- Integrate asammdf for MDF file parsing
- Integrate python-can for BLF file parsing
- REST endpoints: `/files`, `/files/{id}/info`
- Support for 1GB+ files with chunking
- Memory-efficient parsing

### 1.6 Data Service Endpoints
**As a** frontend component  
**I want to** retrieve signal data via REST API  
**So that** I can display and analyze measurements

**Acceptance Criteria:**
- `/signals` endpoint returns available signals
- `/data` endpoint with time range and signal selection
- Efficient data serialization (JSON/MessagePack)
- Pagination support for large datasets
- Response time <500ms for typical queries

## Technical Requirements

### Extension Structure
```
src/
├── extension.ts          # Main entry point
├── fileHandler.ts        # File detection logic
├── pythonService.ts      # Backend communication
├── config/
│   └── settings.ts       # Configuration management
└── utils/
    └── logger.ts         # Logging utilities
```

### Python Backend Structure
```
python/
├── server.py             # FastAPI application
├── parsers/
│   ├── mdf_parser.py     # MDF file handling
│   └── blf_parser.py     # BLF file handling
├── models/
│   └── data_models.py    # Pydantic models
└── utils/
    └── chunking.py       # Data chunking logic
```

### Key Dependencies
- **Extension**: `vscode`, `axios`, `typescript`
- **Backend**: `fastapi`, `asammdf`, `python-can`, `pydantic`

## Testing Requirements
- Unit tests for file detection logic
- Integration tests for REST endpoints
- Performance tests with 1GB+ files
- Cross-platform compatibility tests
- Extension activation tests

## Definition of Done
- [ ] All user stories completed and tested
- [ ] Code review completed
- [ ] Unit test coverage >80%
- [ ] Integration tests passing
- [ ] Performance benchmarks met (1GB file <5s)
- [ ] Documentation updated
- [ ] No critical security vulnerabilities

## Estimated Effort
- **Total Points**: 21
- **Duration**: 1 week
- **Dependencies**: None (first epic)

## Risks
- Python environment setup complexity on different platforms
- Memory usage with very large files
- Backend process management across platforms
- File system permissions on different OS