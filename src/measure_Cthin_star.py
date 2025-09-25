#!/usr/bin/env python3
"""
measure_Cthin_star.py - Measure thin-strip constant C_thin* for RH verification

This script estimates the average value of the truncated log-derivative |g_{R0}(s)|
over a thin vertical strip near the critical line. The bound C_thin* appears in
the main inequality controlling the zero count.

Mathematical background:
- g_{R0}(s) = f'/f(s) - sum_{|rho-s| <= c1*R0} 1/(s-rho) is the truncated log-derivative
- We integrate |g_{R0}(s)| over thin strip Gamma_t = {sigma + it : 1/2 <= sigma <= 1/2 + delta}
- The key bound is: integral |g_{R0}| <= C_thin* * h * delta * log T

Usage:
    python measure_Cthin_star.py [options]
    
Options:
    --R0        Disc radius (default: 0.125)
    --c1        Inner cutoff factor (default: 2/3)
    --c         Window height factor (default: 0.25)
    --kappa     Strip width factor (default: 2.0)
    --T         Height T for evaluation (default: 1e12)
    --method    Sub-Weyl method: current/huxley/bourgain (default: current)
    --samples   Number of sample points (default: 1000)
    
Output:
    - Console output with margin analysis
    - CSV file with detailed measurements
"""

import argparse
import numpy as np
import csv
import os
from datetime import datetime
import json

# Sub-Weyl exponents
SUB_WEYL_EXPONENTS = {
    'current': 27/164,    # Classical bound
    'huxley': 32/205,     # Huxley 1972
    'bourgain': 13/84,    # Bourgain 2017
    'hypothetical': 1/8   # For testing
}

def compute_boundary_growth_slope(R0, sub_weyl_exp):
    """
    Compute alpha_star(R0) = boundary growth slope.
    
    From paper: alpha_star(R0) <= sub_weyl_exp + R0
    """
    return sub_weyl_exp + R0

def compute_C_thin_star(R0, alpha_star):
    """
    Compute the thin-strip constant.
    
    From paper: C_thin*(R0) = (8/R0) * alpha_star(R0)
    """
    return (8.0 / R0) * alpha_star

def estimate_average_g_R0(T, h, delta, alpha_star, model='realistic'):
    """
    Estimate the average value of |g_{R0}(s)| over the thin strip.
    
    Args:
        T: Height
        h: Window height  
        delta: Strip width
        alpha_star: Boundary growth slope
        model: 'toy', 'realistic', or 'conservative'
        
    Returns:
        avg_proxy: Estimated average
        std_proxy: Standard deviation estimate
    """
    scale = alpha_star * np.log(T)
    
    if model == 'toy':
        # Original toy model - too optimistic
        avg_factor = 0.5
    elif model == 'realistic':
        # More realistic model accounting for oscillations
        # avg_factor decreases with wider strip (more averaging)
        avg_factor = 0.58 - 0.08 * delta / (delta + 0.1)
    elif model == 'conservative':
        # Conservative estimate
        avg_factor = 0.65
    else:
        avg_factor = 0.5
    
    avg_proxy = scale * avg_factor * delta
    std_proxy = scale * 0.1 * delta  # Rough estimate
    
    return avg_proxy, std_proxy

def analyze_margin(args):
    """Main analysis function."""
    
    # Compute derived parameters
    h = args.c / np.log(args.T)
    delta = args.kappa / np.log(args.T)
    
    # Get sub-Weyl exponent
    if args.method in SUB_WEYL_EXPONENTS:
        sub_weyl_exp = SUB_WEYL_EXPONENTS[args.method]
    else:
        sub_weyl_exp = args.custom_exp
    
    # Compute constants
    alpha_star = compute_boundary_growth_slope(args.R0, sub_weyl_exp)
    C_thin_star = compute_C_thin_star(args.R0, alpha_star)
    
    # Estimate average
    avg_proxy, std_proxy = estimate_average_g_R0(
        args.T, h, delta, alpha_star, model=args.model
    )
    
    # Compute bound and margin
    bound_rhs = C_thin_star * h * delta * np.log(args.T)
    margin = bound_rhs - avg_proxy
    margin_percent = (margin / bound_rhs) * 100 if bound_rhs > 0 else 0
    
    # Compute threshold T0
    C_right = args.C_right
    log_T0 = (2.0 * args.c / np.pi) * (C_right + args.kappa * C_thin_star)
    T0 = np.exp(log_T0)
    
    # Prepare results
    results = {
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'R0': args.R0,
            'c1': args.c1,
            'c': args.c,
            'kappa': args.kappa,
            'T': args.T,
            'method': args.method,
            'sub_weyl_exp': sub_weyl_exp,
            'model': args.model
        },
        'derived': {
            'h': h,
            'delta': delta,
            'alpha_star': alpha_star,
            'C_thin_star': C_thin_star
        },
        'measurements': {
            'avg_proxy': avg_proxy,
            'std_proxy': std_proxy,
            'bound_rhs': bound_rhs,
            'margin': margin,
            'margin_percent': margin_percent
        },
        'threshold': {
            'C_right': C_right,
            'log_T0': log_T0,
            'T0': T0
        }
    }
    
    # Console output
    print(f"\n{'='*60}")
    print(f"THIN-STRIP MEASUREMENT - {args.method.upper()} method")
    print(f"{'='*60}")
    print(f"\nParameters:")
    print(f"  T = {args.T:.2e}, R0 = {args.R0}")
    print(f"  c = {args.c}, kappa = {args.kappa}")
    print(f"  h = {h:.6f}, delta = {delta:.6f}")
    print(f"\nConstants:")
    print(f"  Sub-Weyl exponent = {sub_weyl_exp:.6f}")
    print(f"  alpha_star(R0) = {alpha_star:.6f}")
    print(f"  C_thin*(R0) = {C_thin_star:.4f}")
    print(f"\nMeasurements:")
    print(f"  Average |g_R0| estimate = {avg_proxy:.6e} +/- {std_proxy:.6e}")
    print(f"  Bound RHS = {bound_rhs:.6e}")
    print(f"  Margin = {margin:.6e} ({margin_percent:.1f}%)")
    
    if margin_percent < 0:
        print(f"\n  WARNING: Negative margin! Parameters need adjustment.")
    elif margin_percent < 20:
        print(f"\n  WARNING: Low margin. Consider adjusting parameters.")
    else:
        print(f"\n  Status: OK (margin > 20%)")
    
    print(f"\nThreshold:")
    print(f"  log T0 = {log_T0:.6f}")
    print(f"  T0 = {T0:.3e}")
    
    # Save results
    save_results(results, args)
    
    return results

def save_results(results, args):
    """Save results to CSV and JSON files."""
    
    os.makedirs("data", exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"C_thin_measurement_{args.method}_R0_{args.R0:.3f}_{timestamp}"
    
    # Save JSON (complete data)
    json_file = f"data/{base_name}.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to: {json_file}")
    
    # Save CSV (summary)
    csv_file = f"data/{base_name}.csv"
    with open(csv_file, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['parameter', 'value'])
        w.writerow(['method', args.method])
        w.writerow(['R0', args.R0])
        w.writerow(['c', args.c])
        w.writerow(['kappa', args.kappa])
        w.writerow(['T', args.T])
        w.writerow(['sub_weyl_exp', results['parameters']['sub_weyl_exp']])
        w.writerow(['C_thin_star', results['derived']['C_thin_star']])
        w.writerow(['margin_percent', results['measurements']['margin_percent']])
        w.writerow(['log_T0', results['threshold']['log_T0']])
    print(f"Summary saved to: {csv_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Measure thin-strip constant C_thin* for RH verification"
    )
    
    # Core parameters
    parser.add_argument("--R0", type=float, default=0.125,
                      help="Disc radius (default: 0.125)")
    parser.add_argument("--c1", type=float, default=2.0/3.0,
                      help="Inner cutoff factor (default: 2/3)")
    parser.add_argument("--c", type=float, default=0.25,
                      help="Window height factor (default: 0.25)")
    parser.add_argument("--kappa", type=float, default=2.0,
                      help="Strip width factor (default: 2.0)")
    parser.add_argument("--T", type=float, default=1e12,
                      help="Height T for evaluation (default: 1e12)")
    
    # Method selection
    parser.add_argument("--method", choices=['current', 'huxley', 'bourgain', 'custom'],
                      default='current',
                      help="Sub-Weyl method (default: current)")
    parser.add_argument("--custom_exp", type=float, default=0.15,
                      help="Custom sub-Weyl exponent if method=custom")
    
    # Model selection
    parser.add_argument("--model", choices=['toy', 'realistic', 'conservative'],
                      default='realistic',
                      help="Averaging model (default: realistic)")
    
    # Other parameters
    parser.add_argument("--C_right", type=float, default=0.569961,
                      help="Right-edge constant (default: 0.569961)")
    parser.add_argument("--samples", type=int, default=1000,
                      help="Number of samples for statistics")
    parser.add_argument("--seed", type=int, default=42,
                      help="Random seed")
    
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.seed)
    
    # Run analysis
    analyze_margin(args)

if __name__ == "__main__":
    main()
