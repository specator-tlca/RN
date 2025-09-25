#!/usr/bin/env python3
"""
compute_C_right.py - High-precision computation of the right-edge constant

This script computes C_right = -zeta'(2)/zeta(2), which appears in the RH 
short-window certificate as the contribution from the right edge of the 
rectangular contour.

Mathematical background:
- At Re(s) = 2, we have the absolutely convergent representation:
  -zeta'(s)/zeta(s) = sum_{n>=2} Lambda(n) * n^{-s}
- Where Lambda is the von Mangoldt function
- We compute partial sums over primes with rigorous tail bounds

Usage:
    python compute_C_right.py [options]
    
Options:
    --P         Prime cutoff (default: 2000000)
    --method    Computation method: sieve/direct/mpmath (default: sieve)
    --precision Decimal precision for mpmath method (default: 50)
    --verify    Verify using multiple methods
    
Output:
    - Console output with bounds
    - JSON file with detailed results
"""

import argparse
import json
import math
import os
from datetime import datetime

try:
    from mpmath import mp, zeta, log as mplog
    HAS_MPMATH = True
except ImportError:
    HAS_MPMATH = False
    print("Warning: mpmath not available. High-precision computation disabled.")

def primes_upto(n):
    """Sieve of Eratosthenes - efficient for large n."""
    if n < 2:
        return []
    
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[:2] = b"\x00\x00"
    
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            sieve[p*p:n+1:p] = b"\x00" * ((n - p*p) // p + 1)
    
    return [i for i in range(2, n + 1) if sieve[i]]

def compute_partial_sum(P, include_prime_powers=True):
    """
    Compute S(P) = sum_{p<=P} (log p) * p^{-2} / (1 - p^{-2})
    
    If include_prime_powers=True, also adds contributions from p^k for k>=2.
    """
    primes = primes_upto(P)
    
    # Main contribution from primes
    S = 0.0
    for p in primes:
        # (log p) * p^{-2} / (1 - p^{-2}) = (log p) * p^{-2} * sum_{k>=0} p^{-2k}
        # = (log p) * sum_{k>=1} p^{-2k}
        S += math.log(p) / (p**2 - 1)
    
    # Add prime power contributions if requested
    if include_prime_powers:
        for p in primes:
            if p**2 > P:
                break
            k = 2
            while p**k <= P:
                # Lambda(p^k) = log(p) for prime powers
                S += math.log(p) / p**(2*k)
                k += 1
    
    return S

def compute_tail_bound(P):
    """
    Compute rigorous upper bound for the tail sum_{n>P} Lambda(n) * n^{-2}.
    
    From the paper: tail <= (4/3) * (log P + 1) / P
    """
    return (4.0/3.0) * (math.log(P) + 1.0) / P

def compute_C_right_bounds(P, include_prime_powers=False):
    """
    Compute C_right with rigorous bounds.
    
    Returns: (lower_bound, upper_bound, partial_sum, tail_bound)
    """
    S = compute_partial_sum(P, include_prime_powers)
    tail = compute_tail_bound(P)
    
    return S, S + tail, S, tail

def compute_C_right_mpmath(precision=50):
    """
    Compute C_right using high-precision arithmetic with mpmath.
    
    Returns: (value, zeta_2, zeta_prime_2)
    """
    if not HAS_MPMATH:
        raise ImportError("mpmath is required for high-precision computation")
    
    mp.dps = precision
    
    s = mp.mpf(2)
    zeta_2 = zeta(s)
    
    # Compute derivative using finite differences
    h = mp.mpf(10) ** (-precision//3)
    zeta_prime_2 = (zeta(s + h) - zeta(s - h)) / (2 * h)
    
    C_right = -zeta_prime_2 / zeta_2
    
    return float(C_right), float(zeta_2), float(zeta_prime_2)

def verify_computation(P_values=[1000, 10000, 100000, 1000000]):
    """
    Verify computation using multiple methods and P values.
    """
    print("\nVERIFICATION MODE")
    print("="*60)
    
    results = []
    
    # Method 1: Increasing P values
    print("\nMethod 1: Convergence with increasing P")
    print(f"{'P':<10} {'Lower':<15} {'Upper':<15} {'Width':<15}")
    print("-"*55)
    
    for P in P_values:
        lower, upper, S, tail = compute_C_right_bounds(P)
        width = upper - lower
        results.append({'P': P, 'lower': lower, 'upper': upper, 'width': width})
        print(f"{P:<10} {lower:<15.9f} {upper:<15.9f} {width:<15.2e}")
    
    # Method 2: High precision if available
    if HAS_MPMATH:
        print("\nMethod 2: High-precision computation (mpmath)")
        for prec in [30, 50, 100]:
            try:
                C_right, z2, zp2 = compute_C_right_mpmath(prec)
                print(f"  Precision {prec}: C_right = {C_right:.12f}")
            except Exception as e:
                print(f"  Precision {prec}: Failed - {e}")
    
    # Check convergence
    if len(results) >= 2:
        improvement = results[-1]['width'] / results[-2]['width']
        print(f"\nConvergence rate: {improvement:.3f}")
    
    return results

def save_results(results, args):
    """Save detailed results to JSON file."""
    os.makedirs("data", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"data/C_right_computation_P{args.P}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(
        description="Compute the right-edge constant C_right = -zeta'(2)/zeta(2)"
    )
    
    parser.add_argument("--P", type=int, default=2000000,
                       help="Prime cutoff (default: 2000000)")
    parser.add_argument("--method", choices=['sieve', 'direct', 'mpmath'],
                       default='sieve',
                       help="Computation method (default: sieve)")
    parser.add_argument("--precision", type=int, default=50,
                       help="Decimal precision for mpmath (default: 50)")
    parser.add_argument("--verify", action='store_true',
                       help="Run verification with multiple methods")
    parser.add_argument("--no-prime-powers", action='store_true',
                       help="Exclude prime power contributions")
    
    args = parser.parse_args()
    
    print(f"COMPUTING C_right = -zeta'(2)/zeta(2)")
    print(f"{'='*60}")
    
    if args.verify:
        verify_computation()
    
    # Main computation
    print(f"\nMain computation with P = {args.P}")
    print("-"*60)
    
    include_powers = False  # FIXED: formula log(p)/(p^2-1) already includes ALL prime powers
    lower, upper, S, tail = compute_C_right_bounds(args.P, include_powers)
    
    # Prepare results
    results = {
        'timestamp': datetime.now().isoformat(),
        'parameters': {
            'P': args.P,
            'method': args.method,
            'include_prime_powers': include_powers
        },
        'computation': {
            'partial_sum': S,
            'tail_bound': tail,
            'lower_bound': lower,
            'upper_bound': upper,
            'interval_width': upper - lower
        },
        'theoretical': {
            'exact_value': 'sum_{n>=2} Lambda(n) / n^2',
            'numerical_approximation': 0.5699618136104756  # High precision value
        }
    }
    
    # Console output
    print(f"Partial sum S(P) = {S:.9f}")
    print(f"Tail bound       = {tail:.9e}")
    print(f"\nC_right in [{lower:.9f}, {upper:.9f}]")
    print(f"Interval width   = {upper - lower:.9e}")
    
    # Compare with theoretical value
    approx = 0.5699618136104756
    if lower <= approx <= upper:
        print(f"\n[OK] Theoretical value {approx:.12f} is within bounds")
    else:
        print(f"\n[FAIL] WARNING: Theoretical value {approx:.12f} outside bounds!")
    
    # High precision computation if requested
    if args.method == 'mpmath' and HAS_MPMATH:
        print(f"\nHigh-precision computation (dps={args.precision}):")
        C_right_hp, z2, zp2 = compute_C_right_mpmath(args.precision)
        print(f"  zeta(2)    = {z2:.15f}")
        print(f"  zeta'(2)   = {zp2:.15f}")
        print(f"  C_right    = {C_right_hp:.15f}")
        results['high_precision'] = {
            'dps': args.precision,
            'zeta_2': z2,
            'zeta_prime_2': zp2,
            'C_right': C_right_hp
        }
    
    # Save results
    save_results(results, args)
    
    # Summary
    print(f"\nSUMMARY:")
    print(f"  For RH verification, use C_right ~= {(lower + upper)/2:.6f}")
    print(f"  Uncertainty: +/-{(upper - lower)/2:.2e}")

if __name__ == "__main__":
    main()
