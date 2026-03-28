#!/usr/bin/env python3
import subprocess
import sys
import re

def main():
    print("--- Starting Ramulator 2 Validation Test ---")
    
    # 1. Define your Golden Numbers (from your report)
    EXPECTED_READS = 6
    EXPECTED_ROW_HITS = 2

    # 2. Run the simulator
    print("Running simulator with example_config.yaml...")
    try:
        # Run from the parent directory
        result = subprocess.run(
            ["./ramulator2", "-f", "example_config.yaml"],
            cwd="..", 
            capture_output=True, text=True, check=True
        )
        
        # COMBINE stdout and stderr
        raw_output = result.stdout + "\n" + result.stderr
        
        # Strip invisible ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', raw_output)

    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Simulator crashed! Error:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("[FAIL] Could not find ./ramulator2 executable. Run this from the tests/ folder.")
        sys.exit(1)

    # 3. Extract the actual numbers using Regular Expressions (UPDATED WITH UNDERSCORES)
    read_match = re.search(r'total_num_read_requests:\s*(\d+)', clean_output)
    row_hits_match = re.search(r'row_hits_0:\s*(\d+)', clean_output)

    if not read_match or not row_hits_match:
        print("[FAIL] Could not parse the statistics from the output.")
        print("\n--- DEBUG: Here is what Ramulator actually printed ---\n")
        print(clean_output[-1000:]) 
        sys.exit(1)

    actual_reads = int(read_match.group(1))
    actual_row_hits = int(row_hits_match.group(1))

    # 4. Compare and Output Pass/Fail
    passed = True
    print("\n--- Validation Results ---")
    
    if actual_reads == EXPECTED_READS:
        print(f"[PASS] Read Requests match: {actual_reads}")
    else:
        print(f"[FAIL] Read Requests mismatch! Expected {EXPECTED_READS}, got {actual_reads}")
        passed = False

    if actual_row_hits == EXPECTED_ROW_HITS:
        print(f"[PASS] Row Hits match: {actual_row_hits}")
    else:
        print(f"[FAIL] Row Hits mismatch! Expected {EXPECTED_ROW_HITS}, got {actual_row_hits}")
        passed = False

    # 5. Final Verdict
    if passed:
        print("\n[SUCCESS] Ramulator 2 is functioning correctly based on golden metrics.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Ramulator 2 validation failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()