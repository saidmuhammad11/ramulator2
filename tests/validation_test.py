#!/usr/bin/env python3
import subprocess
import sys
import re

ANSI_ESCAPE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

TEST_CASES = [
    {
        "name": "Baseline DDR4 case",
        "cmd": ["./ramulator2", "-f", "example_config.yaml"],
        "cwd": "..",
        "expected": {
            "total_num_read_requests": 6,
            "row_hits_0": 2,
        },
    },
    {
        "name": "BlockHammer DDR5 case",
        "cmd": ["./ramulator2", "-f", "example_config_bh.yaml"],
        "cwd": "..",
        "expected": {
            "total_num_read_requests": 7079,
            "controller_num_row_conflicts": 6908,
            "bliss_blacklist_count": 20975,
        },
    },
    {
        "name": "PRAC DDR5 case",
        "cmd": ["./ramulator2", "-f", "example_config_prac.yaml"],
        "cwd": "..",
        "expected": {
            "total_num_read_requests": 8495,
            "controller_num_row_conflicts": 8393,
            "prac_num_recovery": 21,
        },
    },
]

def run_case(case):
    try:
        result = subprocess.run(
            case["cmd"],
            cwd=case["cwd"],
            capture_output=True,
            text=True,
            check=True
        )
        raw_output = result.stdout + "\n" + result.stderr
        clean_output = ANSI_ESCAPE.sub("", raw_output)
        return clean_output

    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {case['name']} crashed during execution.")
        print(e.stderr)
        return None
    except FileNotFoundError:
        print(f"[FAIL] {case['name']} could not find the ramulator2 executable.")
        return None

def parse_metrics(output, expected_metrics):
    metrics = {}

    for metric_name in expected_metrics:
        match = re.search(rf'{re.escape(metric_name)}:\s*(\d+)', output)
        if match:
            metrics[metric_name] = int(match.group(1))

    return metrics

def validate_case(case):
    print(f"\n=== Running test case: {case['name']} ===")
    print(f"Command: {' '.join(case['cmd'])}")

    output = run_case(case)
    if output is None:
        print(f"[CASE FAIL] {case['name']}")
        return False

    actual = parse_metrics(output, case["expected"])
    expected = case["expected"]

    passed = True

    for metric_name, expected_value in expected.items():
        if metric_name not in actual:
            print(f"[FAIL] Could not parse metric: {metric_name}")
            passed = False
            continue

        actual_value = actual[metric_name]
        if actual_value == expected_value:
            print(f"[PASS] {metric_name}: expected {expected_value}, got {actual_value}")
        else:
            print(f"[FAIL] {metric_name}: expected {expected_value}, got {actual_value}")
            passed = False

    if passed:
        print(f"[CASE PASS] {case['name']}")
    else:
        print(f"[CASE FAIL] {case['name']}")

    return passed

def main():
    print("--- Starting Ramulator 2 Validation Suite ---")

    overall_pass = True
    total_cases = len(TEST_CASES)
    passed_cases = 0

    for case in TEST_CASES:
        case_pass = validate_case(case)
        if case_pass:
            passed_cases += 1
        else:
            overall_pass = False

    print("\n=== Final Validation Summary ===")
    print(f"Cases passed: {passed_cases}/{total_cases}")

    if overall_pass:
        print("[SUCCESS] All validation cases passed.")
        sys.exit(0)
    else:
        print("[FAILURE] One or more validation cases failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()