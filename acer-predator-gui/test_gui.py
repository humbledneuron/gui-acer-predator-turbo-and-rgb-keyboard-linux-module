#!/usr/bin/env python3
"""
Test script for Acer Predator RGB GUI
Quick test without full application startup
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test all imports"""
    print("Testing imports...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✓ PyQt6.QtWidgets")
    except ImportError as e:
        print(f"✗ PyQt6.QtWidgets: {e}")
        return False
    
    try:
        from core.rgb_controller import RGBController
        print("✓ core.rgb_controller")
    except ImportError as e:
        print(f"✗ core.rgb_controller: {e}")
        return False
    
    try:
        from gui.components.color_picker import ColorPickerWidget
        print("✓ gui.components.color_picker")
    except ImportError as e:
        print(f"✗ gui.components.color_picker: {e}")
        return False
    
    try:
        from gui.components.keyboard_preview import KeyboardPreviewWidget
        print("✓ gui.components.keyboard_preview")
    except ImportError as e:
        print(f"✗ gui.components.keyboard_preview: {e}")
        return False
    
    try:
        from gui.components.profile_manager import ProfileManagerWidget
        print("✓ gui.components.profile_manager")
    except ImportError as e:
        print(f"✗ gui.components.profile_manager: {e}")
        return False
    
    try:
        from gui.components.control_panels import ControlPanelsWidget
        print("✓ gui.components.control_panels")
    except ImportError as e:
        print(f"✗ gui.components.control_panels: {e}")
        return False
    
    try:
        from gui.main_window import MainWindow
        print("✓ gui.main_window")
    except ImportError as e:
        print(f"✗ gui.main_window: {e}")
        return False
    
    return True

def test_rgb_controller():
    """Test RGB controller functionality"""
    print("\nTesting RGB Controller...")
    
    try:
        from core.rgb_controller import RGBController
        
        # Test without actual facer_rgb.py (should handle gracefully)
        try:
            controller = RGBController()
            print("✗ RGBController should fail without facer_rgb.py")
            return False
        except FileNotFoundError:
            print("✓ RGBController correctly handles missing facer_rgb.py")
            return True
    except Exception as e:
        print(f"✗ RGBController test failed: {e}")
        return False

def test_device_check():
    """Test device availability check"""
    print("\nTesting device availability...")
    
    device_paths = ["/dev/acer-gkbbl-0", "/dev/acer-gkbbl-static-0"]
    found = False
    
    for path in device_paths:
        if os.path.exists(path):
            print(f"✓ Found device: {path}")
            found = True
        else:
            print(f"✗ Device not found: {path}")
    
    if not found:
        print("⚠️  No RGB devices found. Make sure facer kernel module is loaded.")
    
    return True

def test_facer_rgb_location():
    """Test facer_rgb.py location"""
    print("\nTesting facer_rgb.py location...")
    
    # Check parent directory
    parent_dir = current_dir.parent
    facer_rgb_path = parent_dir / "facer_rgb.py"
    
    if facer_rgb_path.exists():
        print(f"✓ Found facer_rgb.py: {facer_rgb_path}")
        return True
    else:
        print(f"✗ facer_rgb.py not found in: {facer_rgb_path}")
        
        # Check other common locations
        common_paths = [
            "./facer_rgb.py",
            "../facer_rgb.py",
            "../../facer_rgb.py"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                print(f"✓ Found facer_rgb.py: {path}")
                return True
        
        print("⚠️  facer_rgb.py not found in common locations")
        return False

def main():
    """Run all tests"""
    print("Acer Predator RGB GUI - Component Test")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test RGB controller
    if not test_rgb_controller():
        success = False
    
    # Test device availability
    if not test_device_check():
        success = False
    
    # Test facer_rgb.py location
    if not test_facer_rgb_location():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! GUI should work correctly.")
        print("\nYou can now run: ./run.sh")
    else:
        print("⚠️  Some tests failed. Check the issues above.")
        print("\nThe GUI may still work with limited functionality.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())