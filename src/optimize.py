#!/usr/bin/env python3
"""
optimize.py - Parameter optimization for RH verification

This script helps find optimal parameters (c, kappa, R0) that:
1. Maximize the safety margin (must be > 20-30%)
2. Minimize log T0 (threshold height)

The main trade-off: higher margin requires higher T0.

Usage:
    python src/optimize.py                # Run full optimization
    python src/optimize.py --analyze      # Analyze current parameters
    python src/optimize.py --grid-search  # Find optimal via grid search
    python src/optimize.py --test c k R0  # Test specific parameters
    
Example:
    python src/optimize.py --test 0.35 0.8 0.10
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

# Sub-Weyl exponents for different methods
SUB_WEYL_EXPONENTS = {
    'current': 27/164,    # Classical bound (default)
    'huxley': 32/205,     # Huxley 1972  
    'bourgain': 13/84,    # Bourgain 2017
    'hypothetical': 1/8   # For testing
}

@dataclass
class Result:
    c: float
    kappa: float
    R0: float
    C_thin: float
    margin_percent: float
    log_T0: float
    T0: float
    status: str

def compute_metrics(c, kappa, R0, sub_weyl_exp=27/164, C_right=0.569961, T=1e12):
    """Compute all metrics for given parameters."""
    h = c / np.log(T)
    delta = kappa / np.log(T)
    
    alpha = sub_weyl_exp + R0
    C_thin = (8.0 / R0) * alpha
    
    # Realistic model for average |g_R0|
    scale = alpha * np.log(T)
    # Factor decreases with wider strip (more averaging)
    avg_factor = 0.5 * (1 - 0.2 * kappa)  
    avg_proxy = scale * avg_factor * delta
    
    rhs = C_thin * h * delta * np.log(T)
    margin = rhs - avg_proxy
    margin_percent = (margin / rhs) * 100
    
    log_T0 = (2.0 * c / np.pi) * (C_right + kappa * C_thin)
    T0 = np.exp(log_T0)
    
    status = "OK" if margin_percent > 20 else "FAIL"
    
    return Result(c, kappa, R0, C_thin, margin_percent, log_T0, T0, status)

def analyze_current():
    """Analyze the current default parameters."""
    print("\n" + "="*70)
    print("ANALYSIS OF CURRENT PARAMETERS")
    print("="*70)
    
    # Test both old and new parameters
    configs = [
        ("Paper default", 0.25, 2.0, 0.125),
        ("Optimized", 0.35, 0.8, 0.10),
    ]
    
    print(f"\n{'Configuration':<20} {'c':<6} {'kappa':<6} {'R0':<6} {'Margin %':<10} {'log T0':<8} {'Status':<8}")
    print("-"*70)
    
    for name, c, kappa, R0 in configs:
        r = compute_metrics(c, kappa, R0)
        print(f"{name:<20} {c:<6.2f} {kappa:<6.1f} {R0:<6.3f} "
              f"{r.margin_percent:<10.1f} {r.log_T0:<8.2f} {r.status:<8}")

def grid_search(min_margin=25.0, show_plot=True):
    """Find optimal parameters via grid search."""
    print("\n" + "="*70)
    print(f"GRID SEARCH (minimum margin = {min_margin}%)")
    print("="*70)
    
    # Parameter ranges
    c_values = np.linspace(0.20, 0.45, 20)
    kappa_values = np.linspace(0.3, 1.5, 20)
    R0_values = [0.08, 0.10, 0.125, 0.15]
    
    best = None
    best_log_T0 = float('inf')
    all_valid = []
    
    for R0 in R0_values:
        for c in c_values:
            for kappa in kappa_values:
                r = compute_metrics(c, kappa, R0)
                
                if r.margin_percent >= min_margin:
                    all_valid.append(r)
                    if r.log_T0 < best_log_T0:
                        best = r
                        best_log_T0 = r.log_T0
    
    if best:
        print(f"\nBest parameters found:")
        print(f"  c = {best.c:.3f}")
        print(f"  kappa = {best.kappa:.3f}")  
        print(f"  R0 = {best.R0:.3f}")
        print(f"  Margin = {best.margin_percent:.1f}%")
        print(f"  log T0 = {best.log_T0:.2f}")
        print(f"  T0 = {best.T0:.2e}")
        
        # Show top 5
        print(f"\nTop 5 configurations:")
        all_valid.sort(key=lambda r: r.log_T0)
        print(f"{'c':<6} {'kappa':<6} {'R0':<6} {'Margin %':<10} {'log T0':<8}")
        print("-"*40)
        for r in all_valid[:5]:
            print(f"{r.c:<6.2f} {r.kappa:<6.2f} {r.R0:<6.3f} "
                  f"{r.margin_percent:<10.1f} {r.log_T0:<8.2f}")
    else:
        print(f"\nNo valid parameters found with margin >= {min_margin}%")
    
    if show_plot and all_valid:
        plot_optimization_results(all_valid)

def test_parameters(c, kappa, R0):
    """Test specific parameter combination."""
    print("\n" + "="*70)
    print("TESTING SPECIFIC PARAMETERS")
    print("="*70)
    
    r = compute_metrics(c, kappa, R0)
    
    print(f"\nParameters:")
    print(f"  c = {c}")
    print(f"  kappa = {kappa}")
    print(f"  R0 = {R0}")
    
    print(f"\nResults:")
    print(f"  C_thin* = {r.C_thin:.4f}")
    print(f"  Margin = {r.margin_percent:.1f}%")
    print(f"  log T0 = {r.log_T0:.4f}")
    print(f"  T0 = {r.T0:.2e}")
    print(f"  Status: {r.status}")
    
    # Compare with default
    default = compute_metrics(0.25, 2.0, 0.125)
    print(f"\nComparison with paper default:")
    print(f"  Margin: {default.margin_percent:.1f}% -> {r.margin_percent:.1f}%")
    print(f"  log T0: {default.log_T0:.2f} -> {r.log_T0:.2f}")

def plot_optimization_results(results):
    """Visualize optimization results."""
    if not results:
        return
        
    margins = [r.margin_percent for r in results]
    log_T0s = [r.log_T0 for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.scatter(margins, log_T0s, alpha=0.6)
    plt.xlabel('Margin %')
    plt.ylabel('log T0')
    plt.title('Trade-off: Safety Margin vs Threshold Height')
    plt.grid(True, alpha=0.3)
    
    # Highlight best
    best = min(results, key=lambda r: r.log_T0)
    plt.scatter([best.margin_percent], [best.log_T0], 
               color='red', s=100, marker='*', label='Optimal')
    
    plt.legend()
    plt.tight_layout()
    plt.savefig('data/optimization_tradeoff.png', dpi=150)
    print(f"\nPlot saved to: data/optimization_tradeoff.png")

def main():
    parser = argparse.ArgumentParser(
        description="Optimize parameters for RH verification"
    )
    
    parser.add_argument("--analyze", action='store_true',
                       help="Analyze current parameters")
    parser.add_argument("--grid-search", action='store_true',
                       help="Run grid search optimization")
    parser.add_argument("--test", nargs=3, type=float,
                       metavar=('c', 'kappa', 'R0'),
                       help="Test specific parameters")
    parser.add_argument("--min-margin", type=float, default=25.0,
                       help="Minimum acceptable margin %% (default: 25)")
    parser.add_argument("--no-plot", action='store_true',
                       help="Skip plotting")
    
    args = parser.parse_args()
    
    # Default: run all analyses
    if not any([args.analyze, args.grid_search, args.test]):
        args.analyze = True
        args.grid_search = True
    
    if args.analyze:
        analyze_current()
    
    if args.grid_search:
        grid_search(args.min_margin, show_plot=not args.no_plot)
    
    if args.test:
        test_parameters(*args.test)
    
    print("\nNote: Run measure_Cthin_star.py to verify actual margin with parameters")

if __name__ == "__main__":
    main()
