# RH Short-Window Certificate - Computational Framework

## Overview

This repository contains the computational tools for verifying the **Riemann Hypothesis Short-Window Certificate with Explicit Constants**. The code implements all numerical computations from the research paper, providing reproducible verification of key constants and bounds.

**Key components:**
- **C_right constant**: Computing -ζ'(2)/ζ(2) via convergent prime series
- **C_thin* measurement**: Thin-strip approximation constants with explicit bounds
- **T0 threshold**: Critical threshold for window certification  
- **Horizontal validation**: Phase difference bounds on horizontal segments

## Mathematical Context

The short-window method establishes that for T ≥ T₀:
```
|ΔJ_L - π·ΔI(T;h)| < π/2
```
where:
- Window height: h = c/log T
- Strip width: δ = κ/log T  
- Threshold: log T₀ = (2c/π)(C_right + κ·C_thin*)

This ensures zero counting via the argument principle succeeds window by window.

## Installation

### Prerequisites
- Python 3.8 or later
- Windows, macOS, or Linux
- Git (for cloning the repository)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/specator-tlca/RH.git
   cd RH
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate environment**
   - **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`
   - **Windows (CMD)**: `.\.venv\Scripts\activate.bat`  
   - **Linux/macOS**: `source .venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Quick Start - Run All Verifications

```bash
python run_all.py
```

This executes the complete verification suite with optimized parameters and displays a summary report.

### Individual Components

#### 1. Compute C_right = -ζ'(2)/ζ(2)
```bash
python src/compute_C_right.py --P 1000000

# High precision computation
python src/compute_C_right.py --P 10000000
```

**Options:**
- `--P`: Prime cutoff for truncated series (default: 2000000)

**Output:** Rigorous bounds [lower, upper] containing the true value

#### 2. Measure C_thin* approximation constant
```bash
# Default parameters (c=0.25, κ=2.0, R0=0.125) 
python src/measure_Cthin_star.py

# Optimized parameters (recommended)
python src/measure_Cthin_star.py --c 0.35 --kappa 0.8 --R0 0.10
```

**Options:**
- `--c`: Window scale parameter
- `--kappa`: Strip scale parameter  
- `--R0`: Disc radius for truncation

**Output:** C_thin* value, margin analysis, and parameter recommendations

#### 3. Compute T0 threshold
```bash
# Using default parameters
python src/threshold_T0.py

# Using optimized parameters
python src/threshold_T0.py --c 0.35 --kappa 0.8 --R0 0.10
```

**Output:** log T₀, T₀ value, and safety factor relative to T*

#### 4. Validate horizontal bounds
```bash
python src/validate_horizontals.py --c 0.35 --kappa 0.8
```

**Output:** Bound verification and margin relative to π/2

### Parameter Optimization

Find optimal trade-offs between safety margin and threshold height:

```bash
# Analyze current vs optimized parameters
python src/optimize.py --analyze

# Grid search with minimum margin constraint
python src/optimize.py --grid-search --min-margin 30

# Test specific parameter set
python src/optimize.py --test 0.35 0.8 0.10
```

### View Results

Display summary of latest computation results:

```bash
python view_results.py
```

## Output Structure

```
RH/
├── data/                    # Computational results
│   └── C_thin_hat_demo.csv  # Thin-strip measurements
├── logs/                    # Execution logs with timestamps
│   ├── compute_C_right_*.txt
│   ├── measure_Cthin_star_*.txt
│   ├── threshold_T0_*.txt
│   └── validate_horizontals_*.txt
└── src/                     # Source code
    ├── compute_C_right.py
    ├── measure_Cthin_star.py
    ├── threshold_T0.py
    ├── validate_horizontals.py
    └── optimize.py
```

## Examples

### Example 1: Complete verification with summary
```bash
$ python run_all.py

Running all scripts with optimized parameters...
============================================================
[1/4] Running compute_C_right.py...
[2/4] Running measure_Cthin_star.py...
[3/4] Running threshold_T0.py...
[4/4] Running validate_horizontals.py...

SUMMARY
============================================================
compute_C_right                OK
measure_Cthin_star             OK  
threshold_T0                   OK
validate_horizontals           OK

Key results:
- C_right in [0.569959993, 0.569979747]
- Margin: 44.5% (Status: OK)
- log T0 = 3.90, T0 = 4.94e+01
- Safety factor: 4.85e+10
```

### Example 2: High-precision C_right computation
```bash
$ python src/compute_C_right.py --P 10000000

Computing C_right = -ζ'(2)/ζ(2) via convergent prime series...
Using primes up to P = 10000000
Found 664579 primes

Results:
--------
S(P) = 0.5699608571221895
Tail bound: [1.932701e-06, 1.934634e-06]
C_right in [0.569960857, 0.569962790]
Interval width = 1.932701e-06

Verification:
[OK] Theoretical value 0.569961813610 is within bounds
```

### Example 3: Parameter analysis
```bash
$ python src/optimize.py --analyze

Parameter Analysis
==================
                Original    Optimized
Parameter       Value       Value
----------      --------    ---------
c               0.250       0.350
κ               2.000       0.800
R0              0.125       0.100

Results Comparison
==================
Metric          Original    Optimized
----------      --------    ---------
C_thin*         18.667      6.550
Margin          -7.0%       44.5%
log T0          6.03        3.90
T0              4.13e+02    4.94e+01
Status          FAIL        OK

RECOMMENDATION: Use optimized parameters for positive safety margin
```

## Key Mathematical Results

### Constants (Profile Parameters)
- c = 0.35 (window scale)
- κ = 0.8 (strip scale)  
- R₀ = 0.10 (disc radius)
- c₁ = 2/3 (inner cut)
- T* = 2.4 × 10¹²

### Computed Values
- C_right = -ζ'(2)/ζ(2) ≈ 0.569961813610
- C_thin*(1/8) ≤ 56/3 (theoretical)
- C_thin*(0.10) ≤ 6.550 (optimized)
- α*(R₀) ≤ 27/164 + R₀ (boundary growth slope)

### Threshold
- log T₀ ≈ 3.90 (optimized)
- T₀ ≈ 49.4
- Safety factor: T*/T₀ > 10¹⁰

## Technical Details

### Dependencies
- **mpmath**: Arbitrary precision arithmetic for rigorous bounds
- **numpy**: Numerical computations and array operations
- **matplotlib**: Visualization capabilities (future enhancement)

### Computational Methods
- **Interval arithmetic**: All bounds are rigorous with controlled rounding
- **Tail bounds**: Explicit estimates for series truncation errors
- **Parameter validation**: Automatic checking of mathematical constraints

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt` again

2. **PowerShell execution policy (Windows)**
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Memory issues for large P**
   - Start with smaller values (P = 100000)
   - Close other applications
   - Consider using a machine with more RAM

4. **Negative margin warning**
   - Use optimized parameters: `--c 0.35 --kappa 0.8 --R0 0.10`
   - Run `python src/optimize.py` to find suitable parameters

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Submit a pull request with description of changes

## Citation

If you use this code in your research, please cite:
```
RH - Short-Window Certificate with Explicit Constants
miruka, August 2025
GitHub: https://github.com/specator-tlca/RN
```

- [Documentation](link-to-docs)
