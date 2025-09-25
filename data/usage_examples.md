# RH Verification Examples

## Basic Usage

### 1. Run all verifications with default parameters
```bash
python run_all.py
```

### 2. View results summary
```bash
python view_results.py
```

## Precision Levels

### Quick test (for development)
```bash
python run_precision_test.py quick
```

### Medium precision (recommended)
```bash
python run_precision_test.py medium
```

### High precision
```bash
python run_precision_test.py high
```

### Ultra high precision (may take hours)
```bash
python run_precision_test.py ultra
```

## Individual Script Examples

### Computing C_right with different prime bounds

```bash
# Quick computation
python src/compute_C_right.py --P 1000

# Standard computation  
python src/compute_C_right.py --P 1000000

# High precision
python src/compute_C_right.py --P 100000000
```

### Expected outputs

For P=1000000:
```
[C_right] P = 1000000
  partial sum      = 0.569960857
  tail upper bound = 1.668390e-05
  C_right in [ 0.569960857, 0.569977541 ]
```

## Analyzing Results

### Check convergence of C_right
Run with increasing P values and observe how the bounds tighten:

```bash
for P in 1000 10000 100000 1000000; do
    python src/compute_C_right.py --P $P
done
```

### Compare with theoretical value
The exact value is C_right = -ζ'(2)/ζ(2) ≈ 0.5699618...

## Batch Processing

### Run multiple configurations
```python
# save as batch_run.py
import subprocess

P_values = [10**i for i in range(3, 8)]  # 1000 to 10000000

for P in P_values:
    print(f"\nRunning with P={P}")
    subprocess.run(["python", "src/compute_C_right.py", "--P", str(P)])
```

## Data Analysis

### Load and analyze C_thin data
```python
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv('data/C_thin_hat_demo.csv')

# Plot
plt.figure(figsize=(10, 6))
plt.plot(df['j'], df['omega_j'], 'b-', label='omega_j')
plt.xlabel('j')
plt.ylabel('omega_j')
plt.title('C_thin approximation weights')
plt.legend()
plt.grid(True)
plt.show()
```

## Tips

1. **Memory usage**: For very large P (>10^8), monitor memory usage
2. **Computation time**: Roughly O(P) for prime generation
3. **Precision**: Error decreases as O(log(P)/P)
4. **Logging**: All outputs are saved to `logs/` with timestamps

## Troubleshooting

### Script runs too slowly
- Reduce P parameter
- Use `run_precision_test.py quick` for testing

### Out of memory
- Use smaller P values
- Close other applications
- Consider using a machine with more RAM

### Want to see intermediate progress
Modify scripts to add progress reporting:
```python
# In compute_C_right.py, add progress printing
if p % 100000 == 0:
    print(f"  Processing prime {p}...")
```
