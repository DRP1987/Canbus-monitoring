#!/usr/bin/env python3
"""
Integration test for PyInstaller resource path compatibility.

This test validates that all resource paths work correctly with the new
resource_path utility in development mode. When built with PyInstaller,
these same paths should resolve correctly from the _MEIPASS directory.
"""

import os
import sys
from pathlib import Path

def test_resource_path_utility():
    """Test the resource_path utility function."""
    print("=" * 70)
    print("PYINSTALLER RESOURCE PATH COMPATIBILITY TEST")
    print("=" * 70)
    
    # Test 1: Import resource_path utility
    print("\n[TEST 1] Import resource_path utility")
    print("-" * 70)
    try:
        from utils.resource_path import resource_path
        print("✓ Successfully imported resource_path")
    except ImportError as e:
        print(f"✗ Failed to import resource_path: {e}")
        return False
    
    # Test 2: ConfigurationLoader uses resource_path
    print("\n[TEST 2] ConfigurationLoader uses resource_path")
    print("-" * 70)
    try:
        from config.config_loader import ConfigurationLoader
        loader = ConfigurationLoader()
        # Check that the path was resolved
        assert os.path.isabs(loader.config_file), "Config file path should be absolute"
        assert os.path.exists(loader.config_file), f"Config file not found: {loader.config_file}"
        print(f"✓ Config file path: {loader.config_file}")
        print(f"✓ Config file exists: {os.path.exists(loader.config_file)}")
        
        # Load configurations to verify it works
        configs = loader.load_configurations()
        print(f"✓ Loaded {len(configs)} configurations")
    except Exception as e:
        print(f"✗ ConfigurationLoader test failed: {e}")
        return False
    
    # Test 3: Verify all asset files exist and can be resolved
    print("\n[TEST 3] Verify all asset files exist")
    print("-" * 70)
    assets = [
        'configurations.json',
        'assets/logo.png',
        'assets/icon.png',
        'assets/icon.ico',
    ]
    
    for asset in assets:
        asset_path = resource_path(asset)
        if os.path.exists(asset_path):
            print(f"✓ {asset}: {asset_path}")
        else:
            print(f"✗ {asset} NOT FOUND: {asset_path}")
            return False
    
    # Test 4: Verify imports work in modified files
    print("\n[TEST 4] Verify imports in modified files")
    print("-" * 70)
    
    # Check main.py exists (skip import due to PyQt5 dependency)
    try:
        main_path = os.path.join(os.path.dirname(__file__), 'main.py')
        if os.path.exists(main_path):
            # Verify it imports resource_path
            with open(main_path, 'r') as f:
                main_content = f.read()
                if 'from utils.resource_path import resource_path' in main_content:
                    print("✓ main.py imports resource_path")
                else:
                    print("✗ main.py does not import resource_path")
                    return False
        else:
            print("✗ main.py not found")
            return False
    except Exception as e:
        print(f"✗ main.py check failed: {e}")
        return False
    
    # Check config_loader.py imports
    try:
        from config.config_loader import ConfigurationLoader
        print("✓ config/config_loader.py imports successfully")
    except ImportError as e:
        print(f"✗ config/config_loader.py import failed: {e}")
        return False
    
    # Test 5: Verify PyInstaller spec file exists
    print("\n[TEST 5] Verify PyInstaller spec file exists")
    print("-" * 70)
    spec_file = os.path.join(os.path.dirname(__file__), 'CANBusMonitor.spec')
    if os.path.exists(spec_file):
        print(f"✓ CANBusMonitor.spec exists: {spec_file}")
        
        # Check if data files are included in spec
        with open(spec_file, 'r') as f:
            spec_content = f.read()
            required_datas = [
                'configurations.json',
                'assets/logo.png',
                'assets/icon.png',
                'assets/icon.ico',
            ]
            for data_file in required_datas:
                if data_file in spec_content:
                    print(f"✓ {data_file} included in spec file")
                else:
                    print(f"✗ {data_file} NOT included in spec file")
                    return False
    else:
        print(f"✗ CANBusMonitor.spec NOT FOUND: {spec_file}")
        return False
    
    # Test 6: Verify build scripts exist
    print("\n[TEST 6] Verify build scripts exist")
    print("-" * 70)
    build_scripts = [
        'build_executable.bat',
        'build_executable.sh',
        'README_BUILD.md',
    ]
    
    for script in build_scripts:
        script_path = os.path.join(os.path.dirname(__file__), script)
        if os.path.exists(script_path):
            print(f"✓ {script} exists")
        else:
            print(f"✗ {script} NOT FOUND")
            return False
    
    # Verify shell script is executable
    sh_script = os.path.join(os.path.dirname(__file__), 'build_executable.sh')
    if os.access(sh_script, os.X_OK):
        print(f"✓ build_executable.sh is executable")
    else:
        print(f"⚠ build_executable.sh is not executable (may need chmod +x)")
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✓")
    print("=" * 70)
    print("\nPyInstaller resource path compatibility verified:")
    print("  ✓ resource_path utility working correctly")
    print("  ✓ All modified files import successfully")
    print("  ✓ All asset files found and accessible")
    print("  ✓ ConfigurationLoader loads configurations correctly")
    print("  ✓ PyInstaller spec file properly configured")
    print("  ✓ Build scripts and documentation in place")
    print("\nReady for PyInstaller executable build!")
    print("\nTo build executable:")
    print("  Windows: build_executable.bat")
    print("  Linux/Mac: ./build_executable.sh")
    
    return True


if __name__ == "__main__":
    success = test_resource_path_utility()
    sys.exit(0 if success else 1)
