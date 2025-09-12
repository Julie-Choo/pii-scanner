#!/usr/bin/env python3
"""
Setup script for PII Scanner
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    print(f"✅ Python version {sys.version.split()[0]} is compatible")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up PII Scanner...")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("💡 Try: pip install --upgrade pip")
        sys.exit(1)
    
    # Install package in development mode
    if not run_command("pip install -e .", "Installing PII Scanner package"):
        sys.exit(1)
    
    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("⚠️ spaCy model download failed. You may need to install it manually.")
    
    # Create necessary directories
    os.makedirs("temp", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run Streamlit app: streamlit run apps/streamlit/app.py")
    print("2. Run API server: python apps/api/main.py")
    print("3. Run tests: python scripts/run_tests.py")

if __name__ == "__main__":
    main()