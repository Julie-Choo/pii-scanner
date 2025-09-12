#!/usr/bin/env python3
"""
Analyze what you actually need vs what can be removed
"""

from pathlib import Path
import os

def get_size_mb(path):
    """Get size in MB"""
    if path.is_dir():
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except:
            pass
        return total / (1024 * 1024)
    else:
        try:
            return path.stat().st_size / (1024 * 1024)
        except:
            return 0

def analyze_project():
    """Analyze current project"""
    print("📊 PII Scanner Project Analysis")
    print("=" * 50)
    
    # Essential (MUST KEEP)
    essential = {
        'src/pii_scanner/': 'Core PII scanner package - REQUIRED',
        'run_api.py': 'Your working API server',
        'bulletproof_api.py': 'Alternative API server',
        'requirements.txt': 'Python dependencies list',
    }
    
    # Useful (RECOMMENDED KEEP)
    useful = {
        'apps/streamlit/': 'Web interface for PII scanner',
        'config/': 'Configuration files',
        'setup.py': 'Package installation script',
        'README.md': 'Project documentation',
    }
    
    # Can remove (SAFE TO DELETE)
    removable = {
        'tests/': 'Test files - not needed for running',
        'apps/api/': 'Original API structure - replaced by run_api.py',
        'scripts/': 'Setup scripts - already used',
        'docs/': 'Documentation files',
        'src/pii_scanner.egg-info/': 'Build artifacts',
    }
    
    # Cleanup files (DEFINITELY REMOVE)
    cleanup_files = [
        'fix_imports.py', 'fix_api_imports.py', 'emergency_fix.py',
        'test_import.py', 'diagnose.py', 'nuclear_fix.py',
        'run_streamlit_fixed.py', 'api_final.py', 'test_file_upload.py'
    ]
    
    print("\n🔥 ESSENTIAL (Must Keep):")
    essential_size = 0
    for item, description in essential.items():
        path = Path(item)
        if path.exists():
            size = get_size_mb(path)
            essential_size += size
            print(f"  ✅ {item:<25} {size:>6.1f}MB - {description}")
        else:
            print(f"  ❓ {item:<25} {'?':>6}MB - {description} (missing)")
    
    print(f"\n📦 USEFUL (Recommended Keep):")
    useful_size = 0
    for item, description in useful.items():
        path = Path(item)
        if path.exists():
            size = get_size_mb(path)
            useful_size += size
            print(f"  💡 {item:<25} {size:>6.1f}MB - {description}")
    
    print(f"\n🗑️  CAN REMOVE (Safe to delete):")
    removable_size = 0
    for item, description in removable.items():
        path = Path(item)
        if path.exists():
            size = get_size_mb(path)
            removable_size += size
            print(f"  ❌ {item:<25} {size:>6.1f}MB - {description}")
    
    print(f"\n🧹 CLEANUP FILES (Definitely remove):")
    cleanup_size = 0
    cleanup_count = 0
    for item in cleanup_files:
        path = Path(item)
        if path.exists():
            size = get_size_mb(path)
            cleanup_size += size
            cleanup_count += 1
            print(f"  🗑️  {item}")
    
    if cleanup_count > 0:
        print(f"  ... and {cleanup_count} more cleanup files ({cleanup_size:.1f}MB total)")
    
    # Summary
    total_current = essential_size + useful_size + removable_size + cleanup_size
    potential_savings = removable_size + cleanup_size
    
    print(f"\n📊 SUMMARY:")
    print(f"  Current total size: {total_current:.1f}MB")
    print(f"  Essential files:    {essential_size:.1f}MB")
    print(f"  Useful files:       {useful_size:.1f}MB")
    print(f"  Can remove:         {removable_size:.1f}MB")
    print(f"  Cleanup files:      {cleanup_size:.1f}MB")
    print(f"  Potential savings:  {potential_savings:.1f}MB ({potential_savings/total_current*100:.1f}%)")
    
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"  1. Keep essential files ({essential_size:.1f}MB) - Required for functionality")
    print(f"  2. Keep useful files ({useful_size:.1f}MB) - Recommended")
    print(f"  3. Remove unnecessary files ({potential_savings:.1f}MB) - Safe to delete")
    
    print(f"\n🚀 MINIMAL WORKING PROJECT:")
    minimal_size = essential_size + useful_size
    print(f"  Size after cleanup: {minimal_size:.1f}MB")
    print(f"  Contains: API server + Web interface + Core package")
    
    return {
        'essential': essential,
        'useful': useful,
        'removable': removable,
        'cleanup_files': cleanup_files,
        'potential_savings': potential_savings
    }

def main():
    """Main analysis"""
    analysis = analyze_project()
    
    print(f"\n🤔 What do you want to do?")
    print(f"  1. Quick cleanup (remove {analysis['potential_savings']:.1f}MB automatically)")
    print(f"  2. Interactive cleanup (choose what to keep)")
    print(f"  3. Just show me what I have (no changes)")
    
    choice = input(f"\nChoice [1/2/3]: ").strip()
    
    if choice == "1":
        print(f"\n⚡ Run: python quick_cleanup.py")
    elif choice == "2":
        print(f"\n🎛️  Run: python cleanup_project.py")
    else:
        print(f"\n👋 No changes made. Analysis complete!")
        
    print(f"\n📝 Your PII Scanner is working fine as-is!")
    print(f"🚀 API: python run_api.py")
    print(f"🌐 Web: streamlit run apps/streamlit/app.py")

if __name__ == "__main__":
    main()
    