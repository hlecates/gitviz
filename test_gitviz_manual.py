#!/usr/bin/env python3
"""
Manual test script for Gitviz - run this to quickly test functionality.
"""

import os
import sys
import tempfile
import subprocess
import shutil
from pathlib import Path

# Add the gitviz package to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from gitviz.core import GitViz, GitRepository
    from gitviz.cli import main
except ImportError as e:
    print(f"Error importing gitviz: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def create_test_repo(repo_path):
    """Create a test Git repository with sample commits."""
    print(f"Creating test repository at {repo_path}")
    
    os.makedirs(repo_path, exist_ok=True)
    original_cwd = os.getcwd()
    
    try:
        os.chdir(repo_path)
        
        # Initialize repository
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Create initial commit
        with open("README.md", "w") as f:
            f.write("# Test Repository\n\nThis is a test repository for Gitviz.\n")
        subprocess.run(["git", "add", "README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        
        # Create some files and commits
        files_and_messages = [
            ("src/main.py", "def main():\n    print('Hello, World!')\n", "Add main.py"),
            ("src/__init__.py", "", "Add __init__.py"),
            ("tests/test_main.py", "def test_main():\n    assert True\n", "Add tests"),
            ("setup.py", "from setuptools import setup\n", "Add setup.py"),
            ("requirements.txt", "pytest\nblack\n", "Add requirements"),
        ]
        
        for filepath, content, message in files_and_messages:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "w") as f:
                f.write(content)
            subprocess.run(["git", "add", filepath], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)
        
        # Create a feature branch
        subprocess.run(["git", "branch", "feature/new-feature"], check=True)
        subprocess.run(["git", "checkout", "feature/new-feature"], check=True)
        
        # Make commits on feature branch
        with open("src/feature.py", "w") as f:
            f.write("def new_feature():\n    return 'New feature!'\n")
        subprocess.run(["git", "add", "src/feature.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Implement new feature"], check=True)
        
        with open("src/feature.py", "w") as f:
            f.write("def new_feature():\n    return 'Improved feature!'\n")
        subprocess.run(["git", "add", "src/feature.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Improve new feature"], check=True)
        
        # Switch back to main and create another commit
        subprocess.run(["git", "checkout", "main"], check=True)
        with open("docs/README.md", "w") as f:
            f.write("# Documentation\n\nProject documentation.\n")
        subprocess.run(["git", "add", "docs/README.md"], check=True)
        subprocess.run(["git", "commit", "-m", "Add documentation"], check=True)
        
        # Merge the feature branch
        subprocess.run(["git", "merge", "feature/new-feature", "--no-ff", "-m", "Merge feature branch"], check=True)
        
        # Create a hotfix
        subprocess.run(["git", "branch", "hotfix/critical-fix"], check=True)
        subprocess.run(["git", "checkout", "hotfix/critical-fix"], check=True)
        
        with open("src/main.py", "w") as f:
            f.write("def main():\n    print('Hello, Fixed World!')\n")
        subprocess.run(["git", "add", "src/main.py"], check=True)
        subprocess.run(["git", "commit", "-m", "Critical hotfix"], check=True)
        
        subprocess.run(["git", "checkout", "main"], check=True)
        subprocess.run(["git", "merge", "hotfix/critical-fix", "--no-ff", "-m", "Merge hotfix"], check=True)
        
        print("✓ Test repository created successfully")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating test repository: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    finally:
        os.chdir(original_cwd)
    
    return True


def test_core_functionality(repo_path):
    """Test core GitViz functionality."""
    print("\n=== Testing Core Functionality ===")
    
    try:
        # Test GitRepository
        print("Testing GitRepository...")
        repo = GitRepository(repo_path)
        commits = repo.get_commits()
        print(f"✓ Found {len(commits)} commits")
        
        if commits:
            print(f"  Latest commit: {commits[0].short_sha} - {commits[0].message}")
            print(f"  Author: {commits[0].author}")
        
        # Test GitViz
        print("\nTesting GitViz...")
        gitviz = GitViz()
        available_engines = gitviz.get_available_engines()
        print(f"✓ Available engines: {available_engines}")
        
        if not available_engines:
            print("⚠ No rendering engines available - install graphviz or pyvis")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing core functionality: {e}")
        return False


def test_rendering_engines(repo_path, output_dir):
    """Test different rendering engines and formats."""
    print("\n=== Testing Rendering Engines ===")
    
    gitviz = GitViz()
    available_engines = gitviz.get_available_engines()
    
    if not available_engines:
        print("⚠ No rendering engines available")
        return False
    
    success_count = 0
    total_tests = 0
    
    # Test configurations
    test_configs = []
    
    if "graphviz" in available_engines:
        test_configs.extend([
            ("graphviz", "svg", "graphviz_output"),
            ("graphviz", "png", "graphviz_output"),
            ("graphviz", "pdf", "graphviz_output"),
            ("graphviz", "dot", "graphviz_output"),
        ])
    
    if "pyvis" in available_engines:
        test_configs.append(("pyvis", "html", "pyvis_output"))
    
    for engine, format_type, output_name in test_configs:
        total_tests += 1
        try:
            print(f"Testing {engine} engine with {format_type} format...")
            output_path = os.path.join(output_dir, f"{output_name}_{format_type}")
            
            gitviz.visualize(
                repo_path=repo_path,
                engine=engine,
                output_path=output_path,
                format_type=format_type,
                max_commits=20
            )
            
            # Check if output file was created
            expected_files = []
            if format_type == "html":
                expected_files.append(f"{output_path}.html")
            else:
                expected_files.append(f"{output_path}.{format_type}")
            
            files_created = []
            for expected_file in expected_files:
                if os.path.exists(expected_file):
                    files_created.append(expected_file)
                    size = os.path.getsize(expected_file)
                    print(f"  ✓ Created {os.path.basename(expected_file)} ({size} bytes)")
            
            if files_created:
                success_count += 1
            else:
                print(f"  ✗ No output files found")
                
        except Exception as e:
            print(f"  ✗ Error with {engine}/{format_type}: {e}")
    
    print(f"\n✓ Successfully tested {success_count}/{total_tests} configurations")
    return success_count > 0


def test_cli_interface(repo_path, output_dir):
    """Test CLI interface."""
    print("\n=== Testing CLI Interface ===")
    
    test_commands = [
        (["--list-engines"], "List engines"),
        (["--path", repo_path, "--output", os.path.join(output_dir, "cli_test")], "Basic CLI test"),
        (["--path", repo_path, "--max-commits", "5", "--output", os.path.join(output_dir, "cli_limited")], "Limited commits"),
    ]
    
    success_count = 0
    
    for args, description in test_commands:
        try:
            print(f"Testing: {description}")
            
            # Simulate command line arguments
            original_argv = sys.argv
            sys.argv = ["gitviz"] + args
            
            try:
                main()
                print(f"  ✓ {description} succeeded")
                success_count += 1
            except SystemExit as e:
                if e.code == 0:
                    print(f"  ✓ {description} succeeded (clean exit)")
                    success_count += 1
                else:
                    print(f"  ✗ {description} failed with exit code {e.code}")
            finally:
                sys.argv = original_argv
                
        except Exception as e:
            print(f"  ✗ {description} failed: {e}")
            sys.argv = original_argv
    
    print(f"✓ Successfully tested {success_count}/{len(test_commands)} CLI commands")
    return success_count > 0


def main_test():
    """Main test function."""
    print("🧪 Gitviz Manual Test Suite")
    print("=" * 50)
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = os.path.join(temp_dir, "test_repo")
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Test directory: {temp_dir}")
        
        # Check if git is available
        try:
            subprocess.run(["git", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("✗ Git is not available. Please install Git to run tests.")
            return False
        
        # Create test repository
        if not create_test_repo(repo_path):
            return False
        
        # Run tests
        tests_passed = 0
        total_tests = 3
        
        if test_core_functionality(repo_path):
            tests_passed += 1
        
        if test_rendering_engines(repo_path, output_dir):
            tests_passed += 1
        
        if test_cli_interface(repo_path, output_dir):
            tests_passed += 1
        
        # Summary
        print("\n" + "=" * 50)
        print(f"🏁 Test Summary: {tests_passed}/{total_tests} test groups passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Gitviz appears to be working correctly.")
            
            # List output files
            output_files = []
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    output_files.append(os.path.join(root, file))
            
            if output_files:
                print(f"\n📁 Generated {len(output_files)} output files:")
                for file in output_files:
                    rel_path = os.path.relpath(file, output_dir)
                    size = os.path.getsize(file)
                    print(f"  - {rel_path} ({size} bytes)")
                    
                print(f"\n💡 Tip: Check the output files in: {output_dir}")
        else:
            print("⚠ Some tests failed. Check the output above for details.")
        
        # Keep output directory for inspection
        if output_files:
            final_output_dir = os.path.join(os.getcwd(), "gitviz_test_output")
            if os.path.exists(final_output_dir):
                shutil.rmtree(final_output_dir)
            shutil.copytree(output_dir, final_output_dir)
            print(f"\n📋 Test outputs copied to: {final_output_dir}")
        
        return tests_passed == total_tests


if __name__ == "__main__":
    success = main_test()
    sys.exit(0 if success else 1)