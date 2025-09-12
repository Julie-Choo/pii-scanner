#!/usr/bin/env python3
"""
Streamlit application runner
"""

import sys
import os
import subprocess
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def main():
    """Run Streamlit application"""
    streamlit_app = project_root / "apps" / "streamlit" / "app.py"
    
    if not streamlit_app.exists():
        print(f"❌ Streamlit app not found at: {streamlit_app}")
        sys.exit(1)
    
    print("🚀 Starting PII Scanner Web Interface...")
    print("🌐 Open http://localhost:8501 in your browser")
    print("⏹️ Press Ctrl+C to stop")
    
    # Set environment variable for Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root / "src")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app), 
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], env=env, check=True)
    except KeyboardInterrupt:
        print("\n👋 Streamlit app stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        print("💡 Make sure you've run: pip install streamlit")
        sys.exit(1)

if __name__ == "__main__":
    main()