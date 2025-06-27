# Epic 6: Steering System Templates

## Overview
Provide domain-specific analysis templates and pre-configured workflows for steering system validation, making it easy for engineers to perform standard steering tests.

## User Stories

### 6.1 Steering Signal Auto-Configuration
**As a** steering engineer  
**I want to** automatically configure standard steering signals  
**So that** I can quickly start analysis without manual setup

**Acceptance Criteria:**
- Auto-detect steering-related signals
- Group signals by function (Input/Assist/Vehicle)
- Apply standard units and scaling
- Create default plot layouts
- Save/load signal configurations

### 6.2 On-Center Feel Analysis Template
**As a** steering engineer  
**I want to** analyze on-center steering feel  
**So that** I can validate steering precision and feedback

**Acceptance Criteria:**
- Low-speed steering analysis (0-5 deg)
- Torque vs angle hysteresis plots
- Friction torque calculation
- Dead-zone detection
- Compliance report generation

### 6.3 Parking Maneuver Validation
**As a** validation engineer  
**I want to** validate parking maneuver performance  
**So that** I can ensure system meets requirements

**Acceptance Criteria:**
- Detect parking maneuver sequences
- Maximum torque analysis
- Current consumption monitoring
- Temperature rise calculation
- Pass/fail criteria checking

### 6.4 Active Return Compliance
**As a** controls engineer  
**I want to** verify active return functionality  
**So that** I can ensure proper wheel centering

**Acceptance Criteria:**
- Return-to-center rate analysis
- Overshoot/undershoot detection
- Speed-dependent validation
- Active return torque profiles
- Compliance visualization

### 6.5 NVH Analysis Tools
**As an** NVH engineer  
**I want to** analyze noise and vibration in steering  
**So that** I can identify and resolve NVH issues

**Acceptance Criteria:**
- FFT analysis on torque signals
- Vibration frequency identification
- Torque ripple analysis
- Speed-order analysis
- NVH metric calculation

### 6.6 Steering Test Sequences
**As a** test engineer  
**I want to** run standard steering test sequences  
**So that** I can validate complete system behavior

**Acceptance Criteria:**
- Sine sweep test analysis
- Step input response
- Frequency response plots
- Bode diagram generation
- Test report templates

### 6.7 Steering Calibration Support
**As a** calibration engineer  
**I want to** analyze calibration parameter effects  
**So that** I can optimize steering feel

**Acceptance Criteria:**
- Parameter variation detection
- A/B comparison plots
- Sensitivity analysis
- Calibration change tracking
- Optimal parameter suggestions

### 6.8 Quick Analysis Workflows
**As a** steering engineer  
**I want to** access common analysis workflows  
**So that** I can perform routine checks efficiently

**Acceptance Criteria:**
- One-click workflow execution
- Customizable workflow chains
- Progress tracking
- Batch file processing
- Results summary dashboard

## Technical Requirements

### Steering Analysis Module
```python
class SteeringAnalyzer:
    def __init__(self, signals: Dict[str, np.ndarray]):
        self.categorize_signals()
    
    def on_center_analysis(self, speed_range: Tuple[float, float]) -> OnCenterResult
    def parking_maneuver_detection(self) -> List[ParkingManeuver]
    def active_return_analysis(self) -> ActiveReturnResult
    def nvh_analysis(self, frequency_range: Tuple[float, float]) -> NVHResult

@dataclass
class OnCenterResult:
    hysteresis_area: float
    friction_torque: float
    dead_zone: float
    linearity_score: float
    plots: List[PlotConfiguration]
```

### Template Definitions
```yaml
templates:
  on_center_feel:
    name: "On-Center Feel Analysis"
    required_signals:
      - category: "steering_angle"
      - category: "driver_torque"
      - category: "vehicle_speed"
    analysis_steps:
      - filter_low_speed
      - calculate_hysteresis
      - detect_dead_zone
      - generate_report
    
  parking_validation:
    name: "Parking Maneuver Validation"
    required_signals:
      - category: "steering_angle"
      - category: "assist_torque"
      - category: "motor_current"
      - category: "motor_temperature"
```

### Workflow Engine
```typescript
interface WorkflowStep {
    name: string;
    execute(context: AnalysisContext): StepResult;
    canExecute(context: AnalysisContext): boolean;
}

class SteeringWorkflow {
    steps: WorkflowStep[];
    
    async execute(signals: SignalData): Promise<WorkflowResult> {
        for (const step of this.steps) {
            if (step.canExecute(context)) {
                const result = await step.execute(context);
                context.addResult(result);
            }
        }
    }
}
```

### Pre-configured Requirements
```python
STEERING_REQUIREMENTS = {
    "on_center": {
        "max_friction_torque": 0.5,  # Nm
        "max_dead_zone": 0.5,  # degrees
        "min_linearity": 0.95
    },
    "parking": {
        "max_assist_torque": 8.0,  # Nm
        "max_current": 80,  # A
        "max_temperature_rise": 40  # °C
    },
    "active_return": {
        "return_rate_range": (30, 60),  # deg/s
        "max_overshoot": 2.0  # degrees
    }
}
```

## Testing Requirements
- Template execution tests
- Signal categorization accuracy
- Analysis algorithm validation
- Workflow engine tests
- Performance with various datasets
- Template compatibility tests
- Report accuracy verification

## Dependencies
- Epic 4 (Analysis capabilities)
- Epic 5 (Reporting infrastructure)
- Steering domain knowledge

## Definition of Done
- [ ] All steering templates implemented
- [ ] Auto-detection working reliably
- [ ] Analysis algorithms validated
- [ ] Workflow engine functional
- [ ] Pre-configured requirements included
- [ ] Documentation with examples
- [ ] Performance optimized

## Estimated Effort
- **Total Points**: 40
- **Duration**: 2 weeks
- **Dependencies**: Epics 4, 5

## Risks
- Domain expertise requirements
- Algorithm complexity for some analyses
- Template maintenance burden
- Signal naming variation handling
- Performance with complex workflows
- Calibration parameter detection accuracy