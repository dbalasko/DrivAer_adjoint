# DrivAer Adjoint Shape Optimization

Adjoint-based shape optimization of the DrivAer reference vehicle using OpenFOAM v2406.

## Overview

This case performs aerodynamic shape optimization of the DrivAer geometry using adjoint methods. The optimization aims to minimize drag while maintaining manufacturability constraints.

**OpenFOAM Version:** v2406

## Geometry

The DrivAer geometry files (STL) are not included in this repository due to file size constraints.

**Download geometry:** [Insert download link here]

Place the downloaded STL files in:
```
constant/triSurface/
```

## Case Setup
```bash
# Generate mesh
./Allrun.pre

# Run optimization
./Allrun
```

## Utility Scripts

The `scripts/` folder contains Python utilities for case setup and post-processing:

### 1. Generate XYZ Points
```bash
python scripts/genXYZ.py
```
Generates XYZ coordinate files for probe locations or sampling points.

### 2. Extract Forces
```bash
python scripts/extractForces.py
```
Extracts and processes force coefficients from simulation results.

### 3. Plot Convergence
```bash
python scripts/plotConvergence.py
```
Generates convergence plots for objective function and residuals.

### 4. Process Adjoint Results
```bash
python scripts/processAdjoint.py
```
Post-processes adjoint sensitivities and generates visualization data.

## Results

Results are stored in time directories. Key outputs:
- `postProcessing/` - Force coefficients and field data
- Adjoint sensitivity fields in time directories

## References

- DrivAer Reference Model: [TU Munich](https://www.epc.ed.tum.de/en/aer/research-groups/automotive/drivaer/)
- OpenFOAM Documentation: [www.openfoam.com](https://www.openfoam.com)
