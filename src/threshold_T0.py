#!/usr/bin/env python3
"""
threshold_T0.py - Compute threshold height T0 for RH verification

This script calculates the critical threshold T0 above which the short-window
certificate guarantees all zeros lie on the critical line.

Mathematical background:
- The key inequality: |ΔJ_L - π·ΔI(T;h)| ≤ (c/log T) × (C_right + κ·C_thin*) + o(1)
- If the RHS < π/2, then ΔI must equal the true zero count
- This gives: log T0 = (2c/π) × (C_right + κ·C_thin*)

Usage:
    python threshold_T0.py [options]
    
Options:
    --c         Window height factor (default: 0.25)
    --kappa     Strip width factor (default: 2.0)
    --R0        Disc radius (default: 0.125)
    --C_right   Right-edge constant (default: 0.569961)
    --C_thin    Thin-strip constant (default: auto-compute)
    --method    Sub-Weyl method for C_thin (default: current)
    --optimize  Find optimal parameters
    
Output:
    - Console output with T0 value
    - JSON file with detailed analysis
    - Optional: parameter optimization results
"""

import argparse
import json
import math
import numpy as np
import os
from datetime import datetime

# Import sub-Weyl exponents
SUB_WEYL_EXPONENTS = {
    'current': 27/164,
    'huxley': 32/205,
    'bourgain': 13/84,
    'hypothetical': 1/8
}

def compute_C_thin_star(R0, sub_weyl_exp):
    """Compute C_thin* = (8/R0) × (sub_weyl_exp + R0)."""
    alpha_star = sub_weyl_exp + R0
    return (8.0 / R0) * alpha_star

def compute_log_T0(c, kappa, C_right, C_thin):
    """Compute log T0 from the threshold formula."""
    return (2.0 * c / math.pi) * (C_right + kappa * C_thin)

def compute_threshold(args):
    """Compute threshold with given parameters."""
    
    # Get sub-Weyl exponent
    if args.method in SUB_WEYL_EXPONENTS:
        sub_weyl_exp = SUB_WEYL_EXPONENTS[args.method]
    else:
        sub_weyl_exp = args.custom_exp
    
    # Compute C_thin if not provided
    if args.C_thin is None:
        C_thin = compute_C_thin_star(args.R0, sub_weyl_exp)
    else:
        C_thin = args.C_thin
    
    # Compute threshold
    log_T0 = compute_log_T0(args.c, args.kappa, args.C_right, C_thin)
    T0 = math.exp(log_T0)
    
    # Additional derived quantities
    h_at_T0 = args.c / log_T0
    delta_at_T0 = args.kappa / log_T0
    bound_at_T0 = (args.c / log_T0) * (args.C_right + args.kappa * C_thin)
    
    results = {
        'parameters': {
            'c': args.c,
            'kappa': args.kappa,
            'R0': args.R0,
            'C_right': args.C_right,
            'C_thin': C_thin,
            'method': args.method,
            'sub_weyl_exp': sub_weyl_exp
        },
        'threshold': {
            'log_T0': log_T0,
            'T0': T0,
            'T0_scientific': f"{T0:.3e}"
        },
        'at_threshold': {
            'h': h_at_T0,
            'delta': delta_at_T0,
            'bound': bound_at_T0,
            'bound_over_pi': bound_at_T0 / math.pi
        }
    }
    
    # Console output
    print(f"\nTHRESHOLD COMPUTATION")
    print("="*60)
    print(f"\nParameters:")
    print(f"  c = {args.c}, kappa = {args.kappa}, R0 = {args.R0}")
    print(f"  Method: {args.method} (exponent = {sub_weyl_exp:.6f})")
    print(f"\nConstants:")
    print(f"  C_right = {args.C_right:.6f}")
    print(f"  C_thin* = {C_thin:.6f}")
    print(f"\nThreshold:")
    print(f"  log T0 = {log_T0:.6f}")
    print(f"  T0     = {T0:.3e}")
    print(f"\nAt threshold height T0:")
    print(f"  Window height h = {h_at_T0:.6f}")
    print(f"  Strip width delta = {delta_at_T0:.6f}")
    print(f"  Bound value = {bound_at_T0:.6f}")
    print(f"  Bound/pi = {bound_at_T0/math.pi:.4f} (must be < 0.5)")
    
    return results

def optimize_parameters(C_right=0.569961, min_margin=0.25):
    """
    Find optimal parameters (c, κ, R0) that minimize log T0
    subject to margin constraint.
    """
    print("\nPARAMETER OPTIMIZATION")
    print("="*60)
    print(f"Constraint: margin ≥ {min_margin*100:.0f}%")
    
    best_results = {}
    
    for method_name, sub_weyl_exp in SUB_WEYL_EXPONENTS.items():
        best_log_T0 = float('inf')
        best_params = None
        
        # Grid search
        c_values = np.linspace(0.15, 0.40, 20)
        kappa_values = np.linspace(0.5, 3.0, 20)
        R0_values = np.linspace(0.05, 0.20, 20)
        
        for c in c_values:
            for kappa in kappa_values:
                for R0 in R0_values:
                    # Compute metrics
                    C_thin = compute_C_thin_star(R0, sub_weyl_exp)
                    log_T0 = compute_log_T0(c, kappa, C_right, C_thin)
                    
                    # Estimate margin (simplified model)
                    h = c / 30  # Approximate log(1e12) ≈ 30
                    delta = kappa / 30
                    alpha = sub_weyl_exp + R0
                    avg_factor = 0.58 - 0.08 * delta / (delta + 0.1)
                    margin_est = 1 - avg_factor
                    
                    # Check constraint and update best
                    if margin_est >= min_margin and log_T0 < best_log_T0:
                        best_log_T0 = log_T0
                        best_params = (c, kappa, R0)
        
        if best_params:
            best_results[method_name] = {
                'c': best_params[0],
                'kappa': best_params[1],
                'R0': best_params[2],
                'log_T0': best_log_T0,
                'T0': math.exp(best_log_T0)
            }
    
    # Display results
    print(f"\nOptimal parameters by method:")
    print(f"{'Method':<15} {'c':<8} {'κ':<8} {'R0':<8} {'log T0':<10} {'T0':<12}")
    print("-"*70)
    
    for method, params in best_results.items():
        print(f"{method:<15} {params['c']:<8.3f} {params['kappa']:<8.2f} "
              f"{params['R0']:<8.3f} {params['log_T0']:<10.4f} {params['T0']:<12.2e}")
    
    return best_results

def compare_parameter_sets():
    """Compare different parameter sets from the literature."""
    print("\nCOMPARISON OF PARAMETER SETS")
    print("="*60)
    
    parameter_sets = [
        ("Paper default", 0.25, 2.0, 0.125, 'current'),
        ("Conservative", 0.30, 2.5, 0.10, 'current'),
        ("Aggressive", 0.20, 1.5, 0.15, 'current'),
        ("Optimal (30% margin)", 0.25, 1.0, 0.125, 'current'),
        ("With Bourgain", 0.25, 2.0, 0.125, 'bourgain'),
    ]
    
    C_right = 0.569961
    
    print(f"{'Configuration':<25} {'c':<6} {'κ':<6} {'R0':<6} {'Method':<10} {'log T0':<10} {'T0':<12}")
    print("-"*85)
    
    results = []
    for name, c, kappa, R0, method in parameter_sets:
        sub_weyl = SUB_WEYL_EXPONENTS[method]
        C_thin = compute_C_thin_star(R0, sub_weyl)
        log_T0 = compute_log_T0(c, kappa, C_right, C_thin)
        T0 = math.exp(log_T0)
        
        print(f"{name:<25} {c:<6.2f} {kappa:<6.1f} {R0:<6.3f} "
              f"{method:<10} {log_T0:<10.4f} {T0:<12.2e}")
        
        results.append({
            'name': name,
            'parameters': {'c': c, 'kappa': kappa, 'R0': R0},
            'method': method,
            'log_T0': log_T0,
            'T0': T0
        })
    
    return results

def save_results(results, args):
    """Save results to file."""
    os.makedirs("data", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/threshold_T0_{args.method}_{timestamp}.json"
    
    output_data = {
        'timestamp': datetime.now().isoformat(),
        'computation': results,
        'command_line_args': vars(args)
    }
    
    with open(filename, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Compute threshold T0 for RH verification"
    )
    
    # Parameters
    parser.add_argument("--c", type=float, default=0.25,
                       help="Window height factor (default: 0.25)")
    parser.add_argument("--kappa", type=float, default=2.0,
                       help="Strip width factor (default: 2.0)")
    parser.add_argument("--R0", type=float, default=0.125,
                       help="Disc radius (default: 0.125)")
    parser.add_argument("--C_right", type=float, default=0.569961,
                       help="Right-edge constant (default: 0.569961)")
    parser.add_argument("--C_thin", type=float, default=None,
                       help="Thin-strip constant (default: auto-compute)")
    
    # Method selection
    parser.add_argument("--method", choices=['current', 'huxley', 'bourgain', 'custom'],
                       default='current',
                       help="Sub-Weyl method (default: current)")
    parser.add_argument("--custom_exp", type=float, default=0.15,
                       help="Custom sub-Weyl exponent if method=custom")
    
    # Additional options
    parser.add_argument("--optimize", action='store_true',
                       help="Find optimal parameters")
    parser.add_argument("--compare", action='store_true',
                       help="Compare different parameter sets")
    parser.add_argument("--min_margin", type=float, default=0.25,
                       help="Minimum margin for optimization (default: 0.25)")
    
    args = parser.parse_args()
    
    # Main computation
    results = compute_threshold(args)
    
    # Additional analyses
    if args.compare:
        comparison = compare_parameter_sets()
        results['comparison'] = comparison
    
    if args.optimize:
        optimization = optimize_parameters(args.C_right, args.min_margin)
        results['optimization'] = optimization
    
    # Save results
    save_results(results, args)
    
    # Final message
    T_star = 2.4e12
    if results['threshold']['T0'] < T_star:
        ratio = T_star / results['threshold']['T0']
        print(f"\n[SUCCESS] T0 = {results['threshold']['T0']:.2e} << T* = {T_star:.2e}")
        print(f"  Safety factor: {ratio:.2e}")
    else:
        print(f"\n[WARNING] T0 = {results['threshold']['T0']:.2e} >= T* = {T_star:.2e}")
        print(f"  Parameters need adjustment!")

if __name__ == "__main__":
    main()
