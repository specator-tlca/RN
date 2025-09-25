#!/usr/bin/env python3
"""
Run all RH (Riemann Hypothesis) verification scripts with logging.
Saves outputs to both console and log files.
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

def ensure_directories():
    """Create data and logs directories if they don't exist."""
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)

def run_script_with_logging(script_name, args=None, log_prefix=""):
    """Run a Python script and log output to file and console."""
    if args is None:
        args = []
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/{log_prefix}{script_name}_{timestamp}.txt"
    
    cmd = [sys.executable, f"src/{script_name}.py"] + args
    
    print(f"\n{'='*60}")
    print(f"Running: {script_name}.py {' '.join(args)}")
    print(f"Log: {log_filename}")
    print(f"{'='*60}")
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        # Write header
        log_file.write(f"Script: {script_name}.py\n")
        log_file.write(f"Arguments: {' '.join(args)}\n")
        log_file.write(f"Started: {datetime.now()}\n")
        log_file.write(f"{'='*60}\n\n")
        
        # Run script
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Stream output to console and file
        for line in process.stdout:
            print(line.rstrip())
            log_file.write(line)
        
        process.wait()
        
        # Write footer
        log_file.write(f"\n{'='*60}\n")
        log_file.write(f"Finished: {datetime.now()}\n")
        log_file.write(f"Return code: {process.returncode}\n")
        
    return process.returncode

def main():
    """Run all RH verification scripts in sequence."""
    
    print("RH (Riemann Hypothesis) Verification Suite")
    print(f"Started at: {datetime.now()}")
    
    ensure_directories()
    
    # Define scripts and their arguments
    # Using optimized parameters: c=0.35, kappa=0.8, R0=0.10
    scripts = [
        ("compute_C_right", ["--P", "1000000"]),  # Larger P for better precision
        ("measure_Cthin_star", ["--c", "0.35", "--kappa", "0.8", "--R0", "0.10"]),
        ("threshold_T0", ["--c", "0.35", "--kappa", "0.8", "--R0", "0.10"]),
        ("validate_horizontals", ["--c", "0.35", "--kappa", "0.8"]),
    ]
    
    results = []
    
    for script_name, args in scripts:
        return_code = run_script_with_logging(script_name, args)
        results.append((script_name, return_code))
        
        if return_code != 0:
            print(f"\nWARNING: {script_name} returned non-zero code: {return_code}")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    for script_name, return_code in results:
        status = "OK" if return_code == 0 else f"FAILED ({return_code})"
        print(f"{script_name:<30} {status}")
    
    print(f"\nAll logs saved to: logs/")
    print(f"All data saved to: data/")
    print(f"Completed at: {datetime.now()}")
    
    # Create summary file
    summary_file = f"logs/run_all_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RH Verification Run Summary\n")
        f.write(f"Date: {datetime.now()}\n\n")
        for script_name, return_code in results:
            f.write(f"{script_name}: {'SUCCESS' if return_code == 0 else 'FAILED'}\n")

if __name__ == "__main__":
    main()
