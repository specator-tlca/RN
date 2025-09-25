#!/usr/bin/env python3
"""
Run RH verification with different precision levels.
"""

import sys
from run_all import run_script_with_logging, ensure_directories

def run_precision_test(level="medium"):
    """Run tests with different precision levels."""
    
    ensure_directories()
    
    configs = {
        "quick": {
            "P": "10000",
            "desc": "Quick test (low precision)"
        },
        "medium": {
            "P": "1000000", 
            "desc": "Medium precision (default)"
        },
        "high": {
            "P": "10000000",
            "desc": "High precision (slower)"
        },
        "ultra": {
            "P": "100000000",
            "desc": "Ultra high precision (very slow)"
        }
    }
    
    if level not in configs:
        print(f"Unknown precision level: {level}")
        print(f"Available: {', '.join(configs.keys())}")
        return
    
    config = configs[level]
    print(f"\nRunning {config['desc']}")
    print(f"P = {config['P']}")
    print("="*60)
    
    # Run compute_C_right with specified precision
    run_script_with_logging(
        "compute_C_right", 
        ["--P", config["P"]], 
        log_prefix=f"{level}_"
    )
    
    # Run other scripts (they don't take P parameter)
    for script in ["measure_Cthin_star", "threshold_T0", "validate_horizontals"]:
        run_script_with_logging(script, [], log_prefix=f"{level}_")

if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "medium"
    run_precision_test(level)
