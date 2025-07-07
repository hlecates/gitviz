#!/usr/bin/env python3
"""
Test runner for GitViz
"""

import subprocess
import sys
import os


def run_tests():
    """Run all tests"""
    print("Running GitViz tests...")
    print("=" * 50)
    
    # Run integration tests
    print("Running integration tests...")
    try:
        result = subprocess.run([
            sys.executable, "tests/test_integration.py"
        ], check=True)
        print("✓ Integration tests passed")
    except subprocess.CalledProcessError as e:
        print(f"✗ Integration tests failed: {e}")
        return False
    
    # Run unit tests if pytest is available
    print("\nRunning unit tests...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/test_engines.py", "-v"
        ], check=True)
        print("✓ Unit tests passed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠ Unit tests skipped (pytest not available)")
        print("   Install with: pip install pytest")
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 