# run_tests.py script in scripts/
"""
Test runner script
"""

import pytest
import sys
import os
from pathlib import Path

def main():
    """Run test suite"""
    
    # Add src to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))
    
    # Run tests with coverage if available
    args = [
        "tests/",
        "-v",
        "--tb=short",
    ]
    
    # Add coverage if pytest-cov is available
    try:
        import pytest_cov
        args.extend([
            "--cov=pii_scanner",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    except ImportError:
        print("pytest-cov not available, running without coverage")
    
    # Run tests
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())