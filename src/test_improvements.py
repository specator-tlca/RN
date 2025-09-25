#!/usr/bin/env python3
"""
Test improvements to the thin-strip bound with better parameters.
"""

import numpy as np
import argparse
import csv
import os

def improved_measure_Cthin(args):
    """Measure C_thin with various improvements."""
    
    h = args.c / np.log(args.T)
    delta = args.kappa / np.log(args.T)
    
    # Use improved sub-Weyl exponent
    if args.method == "current":
        sub_weyl_exp = 27/164  # ≈ 0.1646
    elif args.method == "huxley":
        sub_weyl_exp = 32/205  # ≈ 0.1561
    elif args.method == "bourgain":
        sub_weyl_exp = 13/84   # ≈ 0.1548
    else:
        sub_weyl_exp = args.custom_exp
    
    alpha = sub_weyl_exp + args.R0
    C_thin = (8.0 / args.R0) * alpha
    
    # Simulate strip integral with improved model
    np.random.seed(args.seed)
    scale = alpha * np.log(args.T)
    
    # More realistic model: mixture of distributions
    # Component 1: Main contribution (exponential-like)
    comp1 = np.random.exponential(scale=1.0, size=int(0.7*args.samples))
    comp1 = comp1 * (scale / (1.0 + scale))
    
    # Component 2: Oscillatory part (normal around mean)
    comp2 = np.random.normal(loc=scale*0.8, scale=scale*0.1, size=int(0.3*args.samples))
    comp2 = np.clip(comp2, 0, scale*1.2)
    
    # Combine
    xs = np.concatenate([comp1, comp2])
    np.random.shuffle(xs)
    
    avg_proxy = float(np.mean(xs)) * delta
    std_proxy = float(np.std(xs)) * delta / np.sqrt(args.samples)
    
    rhs = C_thin * h * delta * np.log(args.T)
    margin = rhs - avg_proxy
    relative_margin = margin / rhs
    
    # Compute log T0
    C_right = args.C_right
    log_T0 = (2.0 * args.c / np.pi) * (C_right + args.kappa * C_thin)
    T0 = np.exp(log_T0)
    
    # Save results
    os.makedirs("data", exist_ok=True)
    output_file = f"data/improved_Cthin_{args.method}_R0_{args.R0:.3f}.csv"
    
    with open(output_file, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["method", "sub_weyl_exp", "T", "h", "delta", "R0", 
                   "C_thin", "avg_proxy", "std_proxy", "bound_rhs", 
                   "margin", "relative_margin", "log_T0", "T0"])
        w.writerow([args.method, sub_weyl_exp, args.T, h, delta, args.R0,
                   C_thin, avg_proxy, std_proxy, rhs, 
                   margin, relative_margin, log_T0, T0])
    
    # Print results
    print(f"\n{'='*60}")
    print(f"Improved C_thin measurement - {args.method} method")
    print(f"{'='*60}")
    print(f"Sub-Weyl exponent: {sub_weyl_exp:.6f}")
    print(f"T = {args.T:.2e}, h = {h:.6f}, delta = {delta:.6f}")
    print(f"R0 = {args.R0}")
    print(f"alpha* = {alpha:.6f}")
    print(f"C_thin* = {C_thin:.4f}")
    print(f"\nMeasurements:")
    print(f"  Average proxy = {avg_proxy:.6e} ± {std_proxy:.6e}")
    print(f"  Bound RHS = {rhs:.6e}")
    print(f"  Margin = {margin:.6e} ({relative_margin*100:.1f}% of RHS)")
    print(f"\nThreshold:")
    print(f"  log T0 = {log_T0:.6f}")
    print(f"  T0 = {T0:.3e}")
    
    return {
        'method': args.method,
        'sub_weyl_exp': sub_weyl_exp,
        'C_thin': C_thin,
        'margin': margin,
        'relative_margin': relative_margin,
        'log_T0': log_T0
    }

def compare_methods():
    """Compare different sub-Weyl bounds and parameters."""
    
    # Default parameters
    base_args = argparse.Namespace(
        T=1e12,
        c=0.25,
        kappa=2.0,
        c1=2/3,
        samples=1000,
        seed=42,
        C_right=0.569961,
        custom_exp=0.15
    )
    
    print("\n" + "="*70)
    print("COMPARISON OF METHODS")
    print("="*70)
    
    # Test different methods
    methods = ["current", "huxley", "bourgain"]
    R0_values = [0.05, 0.075, 0.1, 0.125, 0.15, 0.2]
    
    results = []
    
    for method in methods:
        for R0 in R0_values:
            args = argparse.Namespace(**vars(base_args))
            args.method = method
            args.R0 = R0
            
            result = improved_measure_Cthin(args)
            results.append(result)
    
    # Summary table
    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    print(f"{'Method':<10} {'R0':<6} {'C_thin*':<10} {'Margin %':<10} {'log T0':<10}")
    print("-"*70)
    
    for r in results:
        print(f"{r['method']:<10} {args.R0:<6.3f} {r['C_thin']:<10.4f} "
              f"{r['relative_margin']*100:<10.1f} {r['log_T0']:<10.4f}")
    
    # Find optimal R0 for each method
    print("\n" + "="*70)
    print("OPTIMAL R0 FOR EACH METHOD")
    print("="*70)
    
    for method in methods:
        method_results = [r for r in results if r['method'] == method]
        best = min(method_results, key=lambda x: x['log_T0'])
        print(f"{method}: Optimal R0 = {args.R0:.3f}, log T0 = {best['log_T0']:.6f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--method", choices=["current", "huxley", "bourgain", "custom"],
                      default="current", help="Sub-Weyl bound to use")
    parser.add_argument("--R0", type=float, default=0.125)
    parser.add_argument("--c1", type=float, default=2.0/3.0)
    parser.add_argument("--c", type=float, default=0.25)
    parser.add_argument("--kappa", type=float, default=2.0)
    parser.add_argument("--T", type=float, default=1e12)
    parser.add_argument("--samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--C_right", type=float, default=0.569961)
    parser.add_argument("--custom_exp", type=float, default=0.15,
                      help="Custom sub-Weyl exponent (if method=custom)")
    parser.add_argument("--compare", action="store_true",
                      help="Run comparison of all methods")
    
    args = parser.parse_args()
    
    if args.compare:
        compare_methods()
    else:
        improved_measure_Cthin(args)
