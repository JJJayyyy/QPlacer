# QPlacer Analysis Scripts

## Setup

### Environment Setup

```bash
conda create -n qplacer_eval python=3.9
conda activate qplacer_eval
pip install -r requirements.txt
```


## Files

### 1. `device_characterization.py`
**Purpose**: Characterize quantum device layouts and analyze frequency collisions

**Functionality**:
- Loads placement results from `results/` directory
- Analyzes collision patterns for different placement strategies
- Computes metrics: edge collisions, qubit adjacency, hotspot areas
- Outputs: `device_data.pkl`

**Usage**:
```bash
python device_characterization.py
```

### 2. `circuit_simulation.py`
**Purpose**: Simulate quantum circuit execution on characterized devices

**Functionality**:
- Loads device characterization data from `device_data.pkl`
- Simulates quantum circuits on different device layouts
- Computes success rates considering crosstalk and decoherence
- Outputs: `simulation_result/result_{classic,qplacer,human}.pkl`

**Usage**:
```bash
python circuit_simulation.py
```

## Workflow

```
Placement Results → device_characterization.py → device_data.pkl
                                                         ↓
                                        circuit_simulation.py → simulation_result/
```

## Dependencies

### device_characterization.py
```
numpy==1.26.4
shapely==1.8.5.post1
matplotlib==3.6.0
qiskit-metal==0.1.2
networkx==2.8.7
geopandas==0.14.4
```

### circuit_simulation.py
```
numpy==1.26.4
qiskit==0.39.5
qiskit-terra==0.22.4
scipy==1.13.1
networkx==2.8.7
```

## Configuration

### device_characterization.py
- `TOPOLOGY`: Device topology to analyze
- `PLACEMENT_LIST`: Placement strategies to compare
- `OUTPUT_FILE`: Output data file

### circuit_simulation.py
- `TOPOLOGY`: Device topology
- `CIRCUITS`: Quantum circuits to simulate
- `NUM_MAPPING`: Number of qubit mappings to test
- `RESULT_DIR`: Output directory for results

## Example: Grid-25 Topology

An evaluation example using **grid-25** (5×5 grid topology) is provided in:
- Benchmarks: `../benchmarks/Qplace_benchmark/grid-25_*/`
- Results: `../results/grid-25/`

Three placement strategies are compared:
- **`wp_wf_03`**: QPlacer frequency-aware placement
- **`classical`**: Traditional wirelength-based placement
- **`default`**: Human-designed placement
