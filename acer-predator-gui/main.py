#!/usr/bin/env python3
"""
Acer Predator RGB Keyboard GUI - Main Entry Point
Modern, sleek interface for controlling Acer RGB keyboards on Linux
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
from PyQt6.QtCore import Qt, QDir
from PyQt6.QtGui import QIcon, QFont

# Import our main window
from gui.main_window import MainWindow

def setup_application():
    """Set up the application with proper configuration"""
    app = QApplication(sys.argv)
    
    # Application metadata
    app.setApplicationName("Acer Predator RGB")
    app.setApplicationDisplayName("Acer Predator RGB Keyboard Control")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Acer RGB Community")
    app.setOrganizationDomain("github.com/JafarAkhondali")
    
    # Set application icon (when available)
    icon_path = current_dir / "assets" / "icons" / "app_icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Enable high DPI scaling
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    return app

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")
    
    try:
        import psutil
    except ImportError:
        missing_deps.append("psutil")
    
    if missing_deps:
        error_msg = f"Missing required dependencies: {', '.join(missing_deps)}\n\n"
        error_msg += "Please install them using:\n"
        error_msg += f"pip install {' '.join(missing_deps)}"
        
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "Missing Dependencies", error_msg)
        return False
    
    return True

def check_rgb_device():
    """Check if RGB device is available"""
    device_paths = [
        "/dev/acer-gkbbl-0",
        "/dev/acer-gkbbl-static-0"
    ]
    
    for path in device_paths:
        if os.path.exists(path):
            return True
    
    return False

def check_facer_rgb():
    """Check if facer_rgb.py is available"""
    # Check in parent directory (most likely location)
    parent_dir = current_dir.parent
    facer_rgb_path = parent_dir / "facer_rgb.py"
    
    if facer_rgb_path.exists():
        return str(facer_rgb_path)
    
    # Check in common locations
    common_paths = [
        "/usr/local/bin/facer_rgb.py",
        "/usr/bin/facer_rgb.py",
        "./facer_rgb.py",
        "../facer_rgb.py"
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    return None

def show_startup_warnings():
    """Show warnings about missing components"""
    warnings = []
    
    # Check RGB device
    if not check_rgb_device():
        warnings.append(
            "RGB keyboard device not found. Make sure the facer kernel module is loaded.\n"
            "You can still use the GUI to configure profiles."
        )
    
    # Check facer_rgb.py
    facer_path = check_facer_rgb()
    if not facer_path:
        warnings.append(
            "facer_rgb.py not found in expected locations.\n"
            "RGB control may not work properly."
        )
    
    return warnings

def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Acer Predator RGB Keyboard Control GUI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start the GUI normally
  python main.py --no-tray          # Start without system tray
  python main.py --debug            # Enable debug mode
  python main.py --profile "Gaming" # Load specific profile on startup
        """
    )
    
    parser.add_argument(
        "--no-tray", 
        action="store_true",
        help="Disable system tray integration"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug output"
    )
    
    parser.add_argument(
        "--profile",
        type=str,
        help="Load specific profile on startup"
    )
    
    parser.add_argument(
        "--facer-rgb-path",
        type=str,
        help="Specify custom path to facer_rgb.py"
    )
    
    parser.add_argument(
        "--minimized",
        action="store_true",
        help="Start minimized to system tray"
    )
    
    args = parser.parse_args()
    
    # Enable debug output if requested
    if args.debug:
        os.environ["QT_LOGGING_RULES"] = "qt.qpa.xcb.debug=true"
        print("Debug mode enabled")
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Set up the application
    app = setup_application()
    
    # Check for warnings
    warnings = show_startup_warnings()
    
    try:
        # Create main window
        window = MainWindow()
        
        # Apply startup options
        if args.facer_rgb_path:
            # TODO: Pass custom facer_rgb path to window
            print(f"Using custom facer_rgb.py path: {args.facer_rgb_path}")
        
        if args.profile:
            # TODO: Load specific profile on startup
            print(f"Loading startup profile: {args.profile}")
        
        # Show warnings if any
        if warnings and not args.minimized:
            warning_text = "\n\n".join(warnings)
            QMessageBox.warning(window, "Startup Warnings", warning_text)
        
        # Show or hide window based on startup options
        if args.minimized and window.system_tray:
            window.hide()
            if window.system_tray:
                window.system_tray.showMessage(
                    "Acer Predator RGB",
                    "Application started in background",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )
        else:
            window.show()
        
        # Handle system tray option
        if args.no_tray and window.system_tray:
            window.system_tray.hide()
        
        print("Acer Predator RGB GUI started successfully")
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        error_msg = f"Failed to start application: {e}"
        print(f"Error: {error_msg}", file=sys.stderr)
        
        # Show error dialog if possible
        try:
            QMessageBox.critical(None, "Startup Error", error_msg)
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())