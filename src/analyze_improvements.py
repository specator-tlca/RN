#!/usr/bin/env python3
"""
Analyze improvements to the short-window RH certificate
by varying the sub-Weyl exponent and other parameters.
"""

import math
import matplotlib.pyplot as plt
import numpy as np

def compute_threshold(c, kappa, R0, sub_weyl_exp, C_right=0.569961):
    """Compute log T0 for given parameters."""
    alpha_star = sub_weyl_exp + R0
    C_thin_star = (8.0 / R0) * alpha_star
    log_T0 = (2.0 * c / math.pi) * (C_right + kappa * C_thin_star)
    return log_T0, C_thin_star

def analyze_improvements():
    """Analyze how different parameters affect the threshold."""
    
    # Current parameters
    c_default = 0.25
    kappa_default = 2.0
    R0_default = 0.125
    
    # Sub-Weyl exponents
    exponents = {
        "Current (27/164)": 27/164,
        "Huxley 1972 (32/205)": 32/205,
        "Bourgain 2017 (13/84)": 13/84,
        "Hypothetical (1/7)": 1/7,
        "Hypothetical (1/8)": 1/8,
        "Near-optimal (1/10)": 1/10
    }
    
    print("="*70)
    print("Impact of improved sub-Weyl exponents")
    print("="*70)
    print(f"Fixed: c={c_default}, kappa={kappa_default}, R0={R0_default}")
    print()
    print(f"{'Method':<25} {'Exponent':<10} {'C_thin*':<10} {'log T0':<10} {'T0':<15}")
    print("-"*70)
    
    results = []
    for name, exp in exponents.items():
        log_T0, C_thin = compute_threshold(c_default, kappa_default, R0_default, exp)
        T0 = math.exp(log_T0)
        results.append((exp, log_T0))
        print(f"{name:<25} {exp:<10.6f} {C_thin:<10.4f} {log_T0:<10.4f} {T0:<15.2e}")
    
    # Optimization over R0
    print("\n" + "="*70)
    print("Optimization over R0 (disc radius)")
    print("="*70)
    
    R0_values = np.linspace(0.05, 0.5, 100)
    best_R0 = {}
    
    for name, exp in [("Current", 27/164), ("Bourgain", 13/84)]:
        log_T0_values = []
        for R0 in R0_values:
            if R0 > 0:
                log_T0, _ = compute_threshold(c_default, kappa_default, R0, exp)
                log_T0_values.append(log_T0)
        
        min_idx = np.argmin(log_T0_values)
        best_R0[name] = (R0_values[min_idx], log_T0_values[min_idx])
        
        print(f"\n{name} (exp={exp:.6f}):")
        print(f"  Optimal R0 = {R0_values[min_idx]:.4f}")
        print(f"  Optimal log T0 = {log_T0_values[min_idx]:.4f}")
        print(f"  Improvement over R0=0.125: {log_T0_values[min_idx] - compute_threshold(c_default, kappa_default, 0.125, exp)[0]:.4f}")
    
    # Joint optimization over c and kappa
    print("\n" + "="*70)
    print("Joint optimization over c and kappa")
    print("="*70)
    
    # Grid search
    c_values = np.linspace(0.1, 0.5, 20)
    kappa_values = np.linspace(0.5, 4.0, 20)
    
    for name, exp in [("Current", 27/164)]:
        best_log_T0 = float('inf')
        best_params = None
        
        for c in c_values:
            for kappa in kappa_values:
                log_T0, _ = compute_threshold(c, kappa, 0.125, exp)
                if log_T0 < best_log_T0:
                    best_log_T0 = log_T0
                    best_params = (c, kappa)
        
        print(f"\n{name} method:")
        print(f"  Optimal (c, kappa) = {best_params}")
        print(f"  Optimal log T0 = {best_log_T0:.4f}")
        print(f"  Default log T0 = {compute_threshold(0.25, 2.0, 0.125, exp)[0]:.4f}")
    
    # Sensitivity analysis
    print("\n" + "="*70)
    print("Sensitivity analysis (how much each parameter affects log T0)")
    print("="*70)
    
    base_log_T0, _ = compute_threshold(c_default, kappa_default, R0_default, 27/164)
    
    # Vary each parameter by 10%
    params = [
        ("c", c_default * 1.1, kappa_default, R0_default, 27/164),
        ("kappa", c_default, kappa_default * 1.1, R0_default, 27/164),
        ("R0", c_default, kappa_default, R0_default * 1.1, 27/164),
        ("exponent", c_default, kappa_default, R0_default, 27/164 * 1.1)
    ]
    
    for name, c, k, r, e in params:
        new_log_T0, _ = compute_threshold(c, k, r, e)
        change = new_log_T0 - base_log_T0
        percent = (change / base_log_T0) * 100
        print(f"  10% increase in {name:<10} -> log T0 change: {change:+.4f} ({percent:+.2f}%)")
    
    return results

def plot_improvements():
    """Create visualization of improvements."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Plot 1: log T0 vs sub-Weyl exponent
    exps = np.linspace(0.05, 0.2, 100)
    log_T0s = []
    
    for exp in exps:
        log_T0, _ = compute_threshold(0.25, 2.0, 0.125, exp)
        log_T0s.append(log_T0)
    
    ax1.plot(exps, log_T0s, 'b-', linewidth=2)
    ax1.axvline(27/164, color='r', linestyle='--', label='Current (27/164)')
    ax1.axvline(13/84, color='g', linestyle='--', label='Bourgain (13/84)')
    ax1.axhline(6.03, color='k', linestyle=':', label='Current log T0')
    ax1.set_xlabel('Sub-Weyl exponent')
    ax1.set_ylabel('log T0')
    ax1.set_title('Threshold vs Sub-Weyl exponent')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: log T0 vs R0 for different exponents
    R0s = np.linspace(0.05, 0.5, 100)
    
    for name, exp, color in [("Current", 27/164, 'r'), 
                             ("Bourgain", 13/84, 'g'),
                             ("Hypothetical", 1/8, 'b')]:
        log_T0s = []
        for R0 in R0s:
            log_T0, _ = compute_threshold(0.25, 2.0, R0, exp)
            log_T0s.append(log_T0)
        ax2.plot(R0s, log_T0s, color=color, label=f'{name} ({exp:.4f})')
    
    ax2.axvline(0.125, color='k', linestyle=':', label='Current R0')
    ax2.set_xlabel('R0 (disc radius)')
    ax2.set_ylabel('log T0')
    ax2.set_title('Optimization over disc radius R0')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data/threshold_improvements.png', dpi=150)
    print("\nPlot saved to: data/threshold_improvements.png")

if __name__ == "__main__":
    analyze_improvements()
    plot_improvements()
