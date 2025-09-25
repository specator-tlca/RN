#!/usr/bin/env python3
"""
View results from RH verification scripts.
Reads latest data files and displays key results.
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import numpy as np

def find_latest_file(pattern):
    """Find the most recent file matching pattern in data directory."""
    files = list(Path("data").glob(pattern))
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)

def load_json(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

def display_c_right_from_logs():
    """Extract C_right results from latest log file."""
    latest_log = None
    
    # Search in logs directory (both normal and optimized)
    logs_dir = Path("logs")
    if logs_dir.exists():
        files = list(logs_dir.glob("*compute_C_right_*.txt"))
        if files:
            latest_log = max(files, key=lambda p: p.stat().st_mtime)
    
    if latest_log:
        print("\n=== C_right Computation ===")
        print(f"From: {latest_log.name}")
        
        with open(latest_log, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "[C_right]" in line or "partial sum" in line or "C_right in" in line:
                    print(line.rstrip())
    else:
        print("\n=== C_right Computation ===")
        print("No compute_C_right log files found")

def display_c_thin_results():
    """Display C_thin* measurement results."""
    csv_file = Path("data/C_thin_hat_demo.csv")
    
    print("\n=== C_thin* Measurements ===")
    
    if csv_file.exists():
        print(f"From: {csv_file.name}")
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            data = list(reader)
            
            if data:
                # Show first and last few rows
                print(f"\nData points: {len(data)}")
                print("First entries:")
                print(f"{', '.join(headers)}")
                for row in data[:3]:
                    print(f"{', '.join(row)}")
                
                if len(data) > 6:
                    print("...")
                    print("Last entries:")
                    for row in data[-3:]:
                        print(f"{', '.join(row)}")
    else:
        print("No C_thin_hat_demo.csv found")
    
    # Also check latest log for summary
    logs_dir = Path("logs")
    if logs_dir.exists():
        files = list(logs_dir.glob("*measure_Cthin_star_*.txt"))
        if files:
            latest_log = max(files, key=lambda p: p.stat().st_mtime)
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                print("\nSummary from log:")
                for line in lines:
                    if "margin" in line or "bound_rhs" in line:
                        print(line.rstrip())

def display_threshold_results():
    """Display T0 threshold results."""
    print("\n=== T0 Threshold ===")
    
    # Check latest log
    logs_dir = Path("logs")
    if logs_dir.exists():
        files = list(logs_dir.glob("*threshold_T0_*.txt"))
        if files:
            latest_log = max(files, key=lambda p: p.stat().st_mtime)
            print(f"From: {latest_log.name}")
            
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "[T0]" in line or "T0" in line:
                        print(line.rstrip())
    else:
        print("No threshold_T0 log files found")

def display_validation_results():
    """Display horizontal validation results."""
    print("\n=== Horizontal Validation ===")
    
    # Check latest log
    logs_dir = Path("logs")
    if logs_dir.exists():
        files = list(logs_dir.glob("*validate_horizontals_*.txt"))
        if files:
            latest_log = max(files, key=lambda p: p.stat().st_mtime)
            print(f"From: {latest_log.name}")
            
            with open(latest_log, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if "[horiz]" in line:
                        print(line.rstrip())
    else:
        print("No validate_horizontals log files found")

def main():
    """Display all available results."""
    print("="*60)
    print("RH Verification Results Viewer")
    print(f"Timestamp: {datetime.now()}")
    print("="*60)
    
    # Check if data and logs directories exist
    if not Path("data").exists() and not Path("logs").exists():
        print("\nNo data or logs directories found.")
        print("Run 'python run_all.py' first to generate results.")
        return
    
    # Display results from each component
    display_c_right_from_logs()
    display_c_thin_results()
    display_threshold_results()
    display_validation_results()
    
    print("\n" + "="*60)
    print("End of Results Summary")
    print("="*60)

if __name__ == "__main__":
    main()
