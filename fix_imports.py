#!/usr/bin/env python3
"""
Fix circular import issues in PII Scanner
"""

import os
from pathlib import Path

def fix_circular_imports():
    """Fix the circular import issue"""
    print("🔧 Fixing circular import issues...")
    
    # 1. Fix utils/__init__.py (this is the main problem)
    utils_init = Path("src/pii_scanner/utils/__init__.py")
    
    print(f"📝 Fixing {utils_init}...")
    
    # The utils/__init__.py should be simple, not import from core
    correct_utils_init = '''# src/pii_scanner/utils/__init__.py
"""
Utility modules for PII Scanner
"""

# Only import utilities, not core modules to avoid circular imports
from .config import get_config
from .logger import get_logger, setup_logging

__all__ = [
    'get_config',
    'get_logger', 
    'setup_logging'
]
'''
    
    with open(utils_init, 'w') as f:
        f.write(correct_utils_init)
    
    print("✅ Fixed utils/__init__.py")
    
    # 2. Fix main __init__.py to be correct
    main_init = Path("src/pii_scanner/__init__.py")
    
    print(f"📝 Fixing {main_init}...")
    
    correct_main_init = '''# src/pii_scanner/__init__.py
"""
PII Scanner Package
Simple, modular PII detection and anonymization using Microsoft Presidio
"""

# Import utilities first (no circular dependency)
from .utils.config import get_config
from .utils.logger import get_logger, setup_logging

# Import core components
from .core.scanner import PIIScanner, get_scanner, scan_text, anonymize_text
from .core.models import PIIMatch, ScanResult, ScanOptions, EntityType, ConfidenceLevel, FileInfo
from .core.anonymizer import PIIAnonymizer

# Import file handlers
from .file_handlers.factory import FileHandlerFactory

# Import exceptions
from .exceptions import (
    PIIScannerError, 
    ScannerError, 
    FileHandlerError, 
    UnsupportedFileTypeError,
    ValidationError,
    InitializationError
)

__version__ = "1.0.0"

__all__ = [
    # Core functionality
    "PIIScanner",
    "get_scanner", 
    "scan_text",
    "anonymize_text",
    
    # Models
    "PIIMatch",
    "ScanResult", 
    "ScanOptions",
    "EntityType",
    "ConfidenceLevel",
    "FileInfo",
    
    # Components
    "PIIAnonymizer",
    "FileHandlerFactory",
    
    # Utilities
    "get_config",
    "get_logger",
    "setup_logging",
    
    # Exceptions
    "PIIScannerError",
    "ScannerError", 
    "FileHandlerError",
    "UnsupportedFileTypeError",
    "ValidationError",
    "InitializationError"
]

# Initialize logging when package is imported (safe now)
try:
    setup_logging()
except Exception:
    # If logging setup fails, continue anyway
    pass
'''
    
    with open(main_init, 'w') as f:
        f.write(correct_main_init)
    
    print("✅ Fixed main __init__.py")
    
    # 3. Make sure all other __init__.py files are correct
    core_init = Path("src/pii_scanner/core/__init__.py")
    if not core_init.exists() or core_init.stat().st_size == 0:
        with open(core_init, 'w') as f:
            f.write('# Core PII scanner components\n')
        print("✅ Fixed core/__init__.py")
    
    file_handlers_init = Path("src/pii_scanner/file_handlers/__init__.py")
    if file_handlers_init.exists():
        # Check if it has wrong content
        with open(file_handlers_init, 'r') as f:
            content = f.read()
        
        if 'from .base import BaseFileHandler' not in content:
            correct_file_handlers_init = '''# src/pii_scanner/file_handlers/__init__.py
"""
File handlers for different file types
"""

from .base import BaseFileHandler
from .text_handler import TextFileHandler
from .csv_handler import CSVFileHandler
from .json_handler import JSONFileHandler
from .factory import FileHandlerFactory

__all__ = [
    'BaseFileHandler',
    'TextFileHandler', 
    'CSVFileHandler',
    'JSONFileHandler',
    'FileHandlerFactory'
]
'''
            with open(file_handlers_init, 'w') as f:
                f.write(correct_file_handlers_init)
            print("✅ Fixed file_handlers/__init__.py")

def test_fix():
    """Test if the circular import fix worked"""
    print("\n🧪 Testing the fix...")
    
    import sys
    sys.path.insert(0, str(Path.cwd() / "src"))
    
    try:
        # Test step by step
        print("  Testing utils import...")
        from pii_scanner.utils import get_config
        print("  ✅ utils import OK")
        
        print("  Testing core models...")
        from pii_scanner.core.models import ScanOptions
        print("  ✅ core models OK")
        
        print("  Testing main package...")
        from pii_scanner import ScanOptions, PIIScanner, scan_text
        print("  ✅ main package OK")
        
        print("  Testing functionality...")
        result = scan_text("Email: test@example.com")
        print(f"  ✅ functionality OK - found {result.total_entities} entities")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_runners():
    """Create simple, working runners"""
    print("\n🚀 Creating simple runners...")
    
    # Simple Streamlit runner
    streamlit_content = '''#!/usr/bin/env python3
import sys, os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
os.chdir(project_root)

print("🧪 Testing imports...")
try:
    from pii_scanner import ScanOptions
    print("✅ Import test passed")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

print("🚀 Starting Streamlit...")
import streamlit.web.cli as stcli
sys.argv = ["streamlit", "run", "apps/streamlit/app.py", "--server.port=8501", "--server.address=localhost"]
stcli.main()
'''
    
    with open("run_streamlit_fixed.py", 'w') as f:
        f.write(streamlit_content)
    print("✅ Created run_streamlit_fixed.py")
    
    # Simple API runner
    api_content = '''#!/usr/bin/env python3
import sys, os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "apps" / "api"))

print("🧪 Testing imports...")
try:
    from pii_scanner import ScanOptions
    print("✅ Import test passed")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

print("🚀 Starting API...")
os.chdir(project_root / "apps" / "api")
import uvicorn
from main import app
uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
'''
    
    with open("run_api_fixed.py", 'w') as f:
        f.write(api_content)
    print("✅ Created run_api_fixed.py")

def main():
    """Main fix function"""
    print("🔧 PII Scanner Circular Import Fix")
    print("=" * 50)
    
    # Fix the circular imports
    fix_circular_imports()
    
    # Test the fix
    if test_fix():
        print("\n🎉 CIRCULAR IMPORT FIX SUCCESSFUL!")
        
        # Create working runners
        create_simple_runners()
        
        print("\n🚀 Ready to run:")
        print("   python run_streamlit_fixed.py")
        print("   python run_api_fixed.py")
        
    else:
        print("\n❌ Fix didn't work. Let's try a different approach...")
        print("\nManual steps:")
        print("1. Delete src/pii_scanner/utils/__init__.py")
        print("2. Create new empty src/pii_scanner/utils/__init__.py")
        print("3. Run this script again")

if __name__ == "__main__":
    main()