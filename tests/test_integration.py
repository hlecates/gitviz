#!/usr/bin/env python3
"""
Integration tests for GitViz CLI
"""

import subprocess
import os
import tempfile
import shutil
import sys


def test_cli_list_engines():
    """Test that CLI can list engines"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "gitviz.cli", "--list-engines"
        ], capture_output=True, text=True, check=True)
        
        output = result.stdout
        assert "Available rendering engines:" in output
        assert "ascii" in output
        print("✓ CLI list engines test passed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ CLI list engines test failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")


def test_cli_ascii_engine():
    """Test CLI with ASCII engine"""
    temp_dir = tempfile.mkdtemp()
    try:
        output_path = os.path.join(temp_dir, "cli_test_ascii")
        
        result = subprocess.run([
            sys.executable, "-m", "gitviz.cli",
            "--engine", "ascii",
            "--format", "txt",
            "--output", output_path,
            "--max-commits", "3"
        ], capture_output=True, text=True, check=True)
        
        # Check that output file was created
        expected_file = output_path + '.txt'
        assert os.path.exists(expected_file), f"Expected file {expected_file} was not created"
        
        # Check file content
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Git Repository Visualization (ASCII)" in content
        
        print("✓ CLI ASCII engine test passed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ CLI ASCII engine test failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cli_matplotlib_engine():
    """Test CLI with Matplotlib engine"""
    temp_dir = tempfile.mkdtemp()
    try:
        output_path = os.path.join(temp_dir, "cli_test_matplotlib")
        
        result = subprocess.run([
            sys.executable, "-m", "gitviz.cli",
            "--engine", "matplotlib",
            "--format", "png",
            "--output", output_path,
            "--max-commits", "3"
        ], capture_output=True, text=True, check=True)
        
        # Check that output file was created
        expected_file = output_path + '.png'
        assert os.path.exists(expected_file), f"Expected file {expected_file} was not created"
        
        # Check file size
        assert os.path.getsize(expected_file) > 0, "Generated PNG file is empty"
        
        print("✓ CLI Matplotlib engine test passed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ CLI Matplotlib engine test failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cli_auto_engine_selection():
    """Test CLI auto engine selection"""
    temp_dir = tempfile.mkdtemp()
    try:
        # Test auto-selection for different formats
        test_cases = [
            ("txt", "ascii"),
            ("png", "matplotlib"),
        ]
        
        for format_type, expected_engine in test_cases:
            output_path = os.path.join(temp_dir, f"cli_auto_{format_type}")
            
            result = subprocess.run([
                sys.executable, "-m", "gitviz.cli",
                "--engine", "auto",
                "--format", format_type,
                "--output", output_path,
                "--max-commits", "2"
            ], capture_output=True, text=True, check=True)
            
            # Check that output was generated
            output_files = [f for f in os.listdir(temp_dir) if f.startswith(f"cli_auto_{format_type}")]
            assert len(output_files) > 0, f"No output files generated for {format_type}"
        
        print("✓ CLI auto engine selection test passed")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ CLI auto engine selection test failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cli_validation():
    """Test CLI argument validation"""
    # Test invalid engine
    try:
        result = subprocess.run([
            sys.executable, "-m", "gitviz.cli",
            "--engine", "nonexistent_engine",
            "--output", "test"
        ], capture_output=True, text=True)
        
        assert result.returncode != 0, "Should fail with invalid engine"
        print("✓ CLI validation test passed")
        
    except Exception as e:
        print(f"✗ CLI validation test failed: {e}")


if __name__ == "__main__":
    print("Running GitViz CLI integration tests...")
    print("=" * 50)
    
    test_cli_list_engines()
    test_cli_ascii_engine()
    test_cli_matplotlib_engine()
    test_cli_auto_engine_selection()
    test_cli_validation()
    
    print("=" * 50)
    print("Integration tests completed!") 