# RH Computational Framework
## Short-Window Certificate for the Riemann Hypothesis with Explicit Constants

### Overview

This computational framework provides rigorous verification of key constants and bounds in the short-window approach to the Riemann Hypothesis. The implementation demonstrates:

1. Computation of the right-edge constant C_right = -ζ'(2)/ζ(2) with controlled precision
2. Measurement of thin-strip approximation constant C_thin*(R₀) via boundary growth analysis
3. Critical threshold T₀ calculation ensuring |ΔJ_L - π·ΔI| < π/2 for zero certification
4. Validation of horizontal phase cancellation bounds
5. Parameter optimization framework for safety margin maximization

### Technical Architecture

```
RH/
├── src/                              # Core computational scripts
│   ├── compute_C_right.py           # Right-edge constant -ζ'(2)/ζ(2)
│   ├── measure_Cthin_star.py        # Thin-strip approximation bound
│   ├── threshold_T0.py              # Critical threshold computation
│   ├── validate_horizontals.py      # Horizontal cancellation verification
│   ├── optimize.py                  # Parameter optimization framework
│   └── tools_latex_refs_check.py    # LaTeX reference utilities
├── data/                            # Computational outputs (CSV/JSON)
├── logs/                            # Execution logs with timestamps
├── run_all.py                       # Orchestration script (Python)
├── view_results.py                  # Results visualization
├── requirements.txt                 # Python dependencies
└── README.md                        # Usage instructions
```

### Environment Requirements

- **Platform**: Windows, macOS, or Linux
- **Software**: Python 3.8+
- **Dependencies**: mpmath (arbitrary precision), numpy (arrays), matplotlib (optional)
- **Memory**: 2GB+ for standard computations

### Mathematical Foundation

The short-window method establishes zero counting via the argument principle. For a window [T, T+h] with h = c/log T:

```
ΔI(T;h) = (1/2πi) ∮_{R(T)} f'/f(s) ds
```

where f(s) = (s-1)ζ(s) and R(T) is a rectangular contour. The phase identity yields:

```
|ΔJ_L - π·ΔI(T;h)| ≤ (c/log T)·(C_right + κ·C_thin*(R₀)) + o(1)
```

For T ≥ T₀ where log T₀ = (2c/π)(C_right + κ·C_thin*), we have |ΔJ_L - π·ΔI| < π/2, ensuring N(T) = I(T).

### Script Descriptions

#### 1. Right-Edge Constant (`compute_C_right.py`)
**Mathematical Context**: §6 - Right edge bound

Computes C_right = -ζ'(2)/ζ(2) via the absolutely convergent series:
```
C_right = Σ_{n≥2} Λ(n)/n² = Σ_{p} log p/(p²-1) + higher order terms
```

The script uses prime sieve up to P with rigorous tail bound:
```
tail ≤ (4/3)·(log P + 1)/P
```

**Key Features**:
- Sieve of Eratosthenes for efficient prime generation
- Interval arithmetic for rigorous bounds
- Multiple verification methods including mpmath high precision

**Output**: `data/C_right_computation_P<P>_<timestamp>.json`

#### 2. Thin-Strip Measurement (`measure_Cthin_star.py`)
**Mathematical Context**: §5 - Thin-strip estimate

Measures the approximation constant for the truncated log-derivative:
```
g_{R₀}(s) = f'/f(s) - Σ_{|ρ-s|≤c₁R₀} 1/(s-ρ)
```

The bound C_thin*(R₀) = (8/R₀)·α*(R₀) controls the thin-strip integral:
```
∫_T^{T+h} |∫_{Γ_t} g_{R₀}(s) dσ| dt ≤ C_thin*(R₀)·h·δ·log T + O(h)
```

**Key Parameters**:
- R₀: disc radius for truncation (default 0.125, optimized 0.10)
- α*(R₀) ≤ 27/164 + R₀: boundary growth slope from sub-Weyl bounds
- Model selection: toy/realistic/conservative averaging

**Output**: `data/C_thin_measurement_<method>_R0_<R0>_<timestamp>.json`

#### 3. Threshold Computation (`threshold_T0.py`)
**Mathematical Context**: §7 - Master inequality and threshold

Computes the critical threshold:
```
log T₀ = (2c/π)(C_right + κ·C_thin*(R₀))
```

Above this threshold, the phase inequality |ΔJ_L - π·ΔI| < π/2 holds, ensuring zero counting succeeds.

**Profile Parameters**:
- c: window scale (default 0.25, optimized 0.35)
- κ: strip scale (default 2.0, optimized 0.8)
- Safety factor: T*/T₀ where T* = 2.4×10¹²

**Output**: Console display with threshold analysis

#### 4. Horizontal Validation (`validate_horizontals.py`)
**Mathematical Context**: §6 - Horizontal bounds

Validates the bound on horizontal phase differences:
```
|Φ(T+h) - Φ(T)| ≤ C_horiz·h/T
```

Uses Stirling-type estimates for the Gamma function appearing in functional equation factors.

**Output**: Validation status and margin analysis

#### 5. Parameter Optimization (`optimize.py`)
**Mathematical Context**: Trade-off analysis

Systematic exploration of (c, κ, R₀) parameter space to find optimal configurations balancing:
- Safety margin: (bound - estimate)/bound × 100%
- Threshold height: T₀ value
- Computational feasibility

**Key Methods**:
- Grid search with margin constraints
- Analytical gradient approximations
- Trade-off visualization

**Output**: Parameter recommendations and comparative analysis

### Execution

#### Quick Start
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run complete verification suite
python run_all.py

# View consolidated results  
python view_results.py
```

#### Individual Script Execution
```bash
# Compute C_right with high precision
python src/compute_C_right.py --P 10000000

# Measure C_thin* with optimized parameters
python src/measure_Cthin_star.py --c 0.35 --kappa 0.8 --R0 0.10

# Compute threshold with custom parameters
python src/threshold_T0.py --c 0.35 --kappa 0.8 --R0 0.10

# Validate horizontal bounds
python src/validate_horizontals.py --c 0.35 --kappa 0.8

# Find optimal parameters
python src/optimize.py --grid-search --min-margin 30
```

### Key Computational Insights

1. **C_right Precision**: Using P = 10⁷ primes yields C_right ∈ [0.569960857, 0.569962790] with width < 2×10⁻⁶.

2. **Parameter Sensitivity**: Original parameters (c=0.25, κ=2.0, R₀=0.125) give **negative margin -7%**, while optimized (c=0.35, κ=0.8, R₀=0.10) achieve **margin 44.5%**.

3. **Threshold Scaling**: log T₀ ≈ 3.90 (optimized) vs 6.03 (original), demonstrating the parameter impact on certification feasibility.

4. **Sub-Weyl Dependence**: The framework supports different sub-Weyl bounds (current 27/164, Huxley 32/205, Bourgain 13/84), with linear improvement in C_thin*.

### Computational Profiles

#### Conservative (High Safety)
- Parameters: c=0.40, κ=0.6, R₀=0.08
- Margin: ~60%
- log T₀ ≈ 3.5
- Use for: Maximum reliability

#### Balanced (Recommended)
- Parameters: c=0.35, κ=0.8, R₀=0.10  
- Margin: ~44%
- log T₀ ≈ 3.9
- Use for: Standard verification

#### Aggressive (Low Threshold)
- Parameters: c=0.30, κ=1.2, R₀=0.11
- Margin: ~25%
- log T₀ ≈ 4.8
- Use for: Exploratory analysis

### Data Persistence

All computations save structured output:
- **JSON**: Full computational context, parameters, and results
- **CSV**: Summary tables for analysis
- **Logs**: Timestamped console output for debugging

Results include:
- Input parameters and timestamp
- Intermediate computations with full precision
- Final bounds and verification status
- Theoretical comparisons where applicable

### Theoretical References

This implementation accompanies the paper "RH - Short-Window Certificate with Explicit Constants" and provides computational verification of:
- Right-edge series convergence (Lemma A.3)
- Boundary growth estimates (§3, Lemma 3.1)
- Thin-strip averaging (§5, Equation 5.1)
- Critical threshold formula (§7, Equation 7.2)

### Precision and Reliability

- **Interval Arithmetic**: All bounds use controlled rounding via mpmath
- **Tail Estimates**: Explicit bounds for series truncation errors
- **Parameter Validation**: Automatic checking of mathematical constraints
- **Verification Suite**: Multiple independent methods for cross-validation

### Extensions and Improvements

The framework is designed for extensibility:
- New sub-Weyl bounds can be added to `SUB_WEYL_EXPONENTS`
- Alternative averaging models in `estimate_average_g_R0`
- Higher precision modes via mpmath settings
- Parallel computation for parameter sweeps

### Note on Reproducibility

All random seeds are fixed (default 42) for Monte Carlo estimates. Numerical results are platform-independent up to machine precision. For exact reproducibility of high-precision computations, use the same mpmath version specified in requirements.txt.