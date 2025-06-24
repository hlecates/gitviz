#!/usr/bin/env python3
"""
Quick test script that doesn't require package installation.
Run this to verify Gitviz works before running pytest.
"""

import os
import sys
import subprocess

# Add the current directory to Python path so we can import gitviz
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from gitviz.core import GitViz, GitRepository, GitCommit
        print("✓ Core modules imported successfully")
        
        from gitviz.cli import main, create_parser
        print("✓ CLI modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_git_available():
    """Test that git is available."""
    print("\nTesting Git availability...")
    
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
        print(f"✓ Git is available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("✗ Git is not available or not in PATH")
        return False

def test_engines():
    """Test rendering engine availability."""
    print("\nTesting rendering engines...")
    
    # Test Graphviz
    try:
        import graphviz
        print("✓ Graphviz is available")
        graphviz_available = True
    except ImportError:
        print("⚠ Graphviz is not available (install with: pip install graphviz)")
        graphviz_available = False
    
    # Test PyVis
    try:
        import pyvis
        print("✓ PyVis is available")
        pyvis_available = True
    except ImportError:
        print("⚠ PyVis is not available (install with: pip install pyvis)")
        pyvis_available = False
    
    if not graphviz_available and not pyvis_available:
        print("✗ No rendering engines available!")
        return False
    
    return True

def test_basic_functionality():
    """Test basic GitViz functionality."""
    print("\nTesting basic functionality...")
    
    try:
        from gitviz.core import GitViz
        
        gitviz = GitViz()
        available_engines = gitviz.get_available_engines()
        print(f"✓ Available engines: {available_engines}")
        
        if not available_engines:
            print("⚠ No rendering engines available for full testing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error testing basic functionality: {e}")
        return False

def test_with_current_repo():
    """Test with current repository if it's a git repo."""
    print("\nTesting with current repository...")
    
    try:
        from gitviz.core import GitRepository
        
        # Check if current directory is a git repo
        try:
            repo = GitRepository(".")
            commits = repo.get_commits(max_commits=5)
            print(f"✓ Found {len(commits)} commits in current repository")
            
            if commits:
                print(f"  Latest: {commits[0].short_sha} - {commits[0].message[:50]}...")
            
            return True
        except RuntimeError:
            print("⚠ Current directory is not a Git repository")
            return True  # This is OK, not an error
    except Exception as e:
        print(f"✗ Error testing with repository: {e}")
        return False

def main():
    """Run all quick tests."""
    print("🔧 Gitviz Quick Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Git Availability", test_git_available), 
        ("Rendering Engines", test_engines),
        ("Basic Functionality", test_basic_functionality),
        ("Repository Test", test_with_current_repo),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 40)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All quick tests passed!")
        print("\nNext steps:")
        print("1. Install the package: pip install -e .")
        print("2. Install engines: pip install graphviz pyvis")
        print("3. Run full tests: pytest tests/")
        print("4. Try manual test: python test_gitviz_manual.py")
    else:
        print("⚠ Some tests failed. Check the output above.")
        print("\nCommon fixes:")
        print("- Install Git if not available")
        print("- Install rendering engines: pip install graphviz pyvis")
        print("- Check file structure matches the expected layout")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)