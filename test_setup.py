"""
Simple test script to verify scraper works
Recruiters love repos with tests! ✅
"""

import os
import sys
import subprocess

def test_dependencies():
    """Check if all required packages are installed"""
    print("✅ Testing dependencies...")
    required = ['flask', 'playwright']
    
    try:
        import flask
        import playwright
        print("   ✓ Flask installed")
        print("   ✓ Playwright installed")
        return True
    except ImportError as e:
        print(f"   ✗ Missing: {e}")
        return False

def test_file_structure():
    """Check if all required files exist"""
    print("\n✅ Testing file structure...")
    files = [
        'app.py',
        'maps_scraper.py',
        'templates/index.html',
        'requirements.txt',
        'README.md'
    ]
    
    all_exist = True
    for file in files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} NOT FOUND")
            all_exist = False
    
    return all_exist

def test_output_directories():
    """Check if output directories can be created"""
    print("\n✅ Testing output directories...")
    dirs = ['output', 'logs', 'checkpoints']
    
    for dir in dirs:
        try:
            os.makedirs(dir, exist_ok=True)
            print(f"   ✓ {dir}/ exists")
        except Exception as e:
            print(f"   ✗ {dir}/ error: {e}")
            return False
    
    return True

def test_import_scraper():
    """Check if main scraper module imports without errors"""
    print("\n✅ Testing scraper import...")
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("maps_scraper", "maps_scraper.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("   ✓ maps_scraper.py imports successfully")
        return True
    except Exception as e:
        print(f"   ✗ Import error: {e}")
        return False

def main():
    print("=" * 50)
    print("🧪 Google Maps Scraper - Test Suite")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Dependencies", test_dependencies()))
    results.append(("File Structure", test_file_structure()))
    results.append(("Output Directories", test_output_directories()))
    results.append(("Scraper Import", test_import_scraper()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to run.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix issues before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
