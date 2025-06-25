#!/usr/bin/env python3
"""
Main Window - Acer Predator RGB Keyboard GUI
Modern, sleek interface with Apple-inspired design
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QFrame, QLabel, QPushButton, QSystemTrayIcon, QMenu,
    QMenuBar, QStatusBar, QSplitter, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QIcon, QFont, QPixmap, QAction

# Import our components
from core.rgb_controller import RGBController
from gui.components.color_picker import ColorPickerWidget
from gui.components.keyboard_preview import KeyboardPreviewWidget
from gui.components.profile_manager import ProfileManagerWidget
from gui.components.control_panels import ControlPanelsWidget

class MainWindow(QMainWindow):
    """Main application window with modern UI"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize controller
        self.rgb_controller = None
        self.system_tray = None
        
        # Initialize UI
        self.init_ui()
        self.init_controller()
        self.init_system_tray()
        self.load_theme()
        
        # Set up timers
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # Update every 5 seconds
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Acer Predator RGB Keyboard Control")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Set window icon (placeholder)
        self.setWindowIcon(QIcon())
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main content area
        self.create_main_content(main_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
    def create_header(self, parent_layout):
        """Create the header panel"""
        header_frame = QFrame()
        header_frame.setObjectName("HeaderPanel")
        header_frame.setFixedHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(24, 16, 24, 16)
        
        # Logo and title
        title_layout = QVBoxLayout()
        
        app_title = QLabel("Acer Predator RGB")
        app_title.setObjectName("HeaderLabel")
        
        app_subtitle = QLabel("Keyboard Control Center")
        app_subtitle.setObjectName("InfoLabel")
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(app_subtitle)
        title_layout.addStretch()
        
        # Quick actions
        quick_actions = QHBoxLayout()
        
        self.power_button = QPushButton("⚡ Power")
        self.power_button.setFixedSize(100, 40)
        self.power_button.clicked.connect(self.toggle_power)
        
        self.profile_button = QPushButton("📁 Profiles")
        self.profile_button.setFixedSize(100, 40)
        self.profile_button.clicked.connect(self.open_profiles)
        
        quick_actions.addWidget(self.power_button)
        quick_actions.addWidget(self.profile_button)
        quick_actions.addStretch()
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(quick_actions)
        
        parent_layout.addWidget(header_frame)
    
    def create_main_content(self, parent_layout):
        """Create the main content area"""
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        
        # Left panel - Controls
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Preview and profiles
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([800, 600])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        
        parent_layout.addWidget(splitter)
    
    def create_left_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QFrame()
        panel.setObjectName("MainPanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Tab widget for different control sections
        tab_widget = QTabWidget()
        
        # RGB Controls Tab
        self.control_panels = ControlPanelsWidget()
        tab_widget.addTab(self.control_panels, "🌈 RGB Controls")
        
        # Color Picker Tab
        self.color_picker = ColorPickerWidget()
        tab_widget.addTab(self.color_picker, "🎨 Color Picker")
        
        # Advanced Tab
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout(advanced_widget)
        advanced_layout.addWidget(QLabel("Advanced features coming soon..."))
        advanced_layout.addStretch()
        tab_widget.addTab(advanced_widget, "⚙️ Advanced")
        
        layout.addWidget(tab_widget)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel with preview and profiles"""
        panel = QFrame()
        panel.setObjectName("SidePanel")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Keyboard Preview
        preview_label = QLabel("Keyboard Preview")
        preview_label.setObjectName("SubHeaderLabel")
        
        self.keyboard_preview = KeyboardPreviewWidget()
        
        # Profile Manager
        profile_label = QLabel("Profiles")
        profile_label.setObjectName("SubHeaderLabel")
        
        self.profile_manager = ProfileManagerWidget()
        
        layout.addWidget(preview_label)
        layout.addWidget(self.keyboard_preview, stretch=1)
        layout.addWidget(profile_label)
        layout.addWidget(self.profile_manager, stretch=1)
        
        return panel
    
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        import_action = QAction('Import Profile', self)
        import_action.triggered.connect(self.import_profile)
        file_menu.addAction(import_action)
        
        export_action = QAction('Export Profile', self)
        export_action.triggered.connect(self.export_profile)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        fullscreen_action = QAction('Toggle Fullscreen', self)
        fullscreen_action.setShortcut('F11')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Device status
        self.device_status = QLabel("Device: Checking...")
        self.status_bar.addPermanentWidget(self.device_status)
    
    def init_controller(self):
        """Initialize the RGB controller"""
        try:
            # Try to find facer_rgb.py in parent directory
            parent_dir = Path(__file__).parent.parent.parent.parent
            facer_rgb_path = parent_dir / "facer_rgb.py"
            
            if facer_rgb_path.exists():
                self.rgb_controller = RGBController(str(facer_rgb_path))
                self.connect_signals()
                self.update_device_status()
            else:
                self.show_error("facer_rgb.py not found", 
                              "Could not locate facer_rgb.py. Please ensure it's in the parent directory.")
        except Exception as e:
            self.show_error("Controller Error", f"Failed to initialize RGB controller: {e}")
    
    def connect_signals(self):
        """Connect signals between components"""
        if not self.rgb_controller:
            return
            
        # Connect color picker to preview
        self.color_picker.color_changed.connect(self.keyboard_preview.update_color)
        self.color_picker.color_changed.connect(self.apply_color)
        
        # Connect control panels
        self.control_panels.mode_changed.connect(self.apply_mode)
        self.control_panels.brightness_changed.connect(self.apply_brightness)
        self.control_panels.speed_changed.connect(self.apply_speed)
        
        # Connect profile manager
        self.profile_manager.profile_selected.connect(self.load_profile)
        self.profile_manager.profile_saved.connect(self.save_profile)
        self.profile_manager.profile_deleted.connect(self.delete_profile)
    
    def init_system_tray(self):
        """Initialize system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
            
        self.system_tray = QSystemTrayIcon(self)
        self.system_tray.setIcon(QIcon())  # Placeholder icon
        
        # Tray menu
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Show")
        show_action.triggered.connect(self.show)
        
        hide_action = tray_menu.addAction("Hide")
        hide_action.triggered.connect(self.hide)
        
        tray_menu.addSeparator()
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)
        
        self.system_tray.setContextMenu(tray_menu)
        self.system_tray.activated.connect(self.tray_activated)
        self.system_tray.show()
    
    def load_theme(self):
        """Load the application theme"""
        try:
            theme_path = Path(__file__).parent / "styles" / "acer_theme.qss"
            with open(theme_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Failed to load theme: {e}")
    
    # Slot methods
    def toggle_power(self):
        """Toggle RGB power"""
        if not self.rgb_controller:
            return
            
        current_state = self.rgb_controller.get_current_state()
        if current_state['brightness'] > 0:
            self.rgb_controller.turn_off()
            self.status_bar.showMessage("RGB turned off")
        else:
            self.rgb_controller.set_rgb_mode(current_state['mode'], brightness=100)
            self.status_bar.showMessage("RGB turned on")
    
    def open_profiles(self):
        """Open profiles tab"""
        # This could open a separate profile dialog in the future
        self.status_bar.showMessage("Profiles feature activated")
    
    def apply_color(self, color):
        """Apply color change to keyboard"""
        if not self.rgb_controller:
            return
            
        r, g, b = color.red(), color.green(), color.blue()
        current_state = self.rgb_controller.get_current_state()
        
        self.rgb_controller.set_rgb_mode(
            current_state['mode'],
            color=(r, g, b),
            brightness=current_state['brightness'],
            speed=current_state['speed']
        )
    
    def apply_mode(self, mode_id):
        """Apply RGB mode change"""
        if not self.rgb_controller:
            return
            
        current_state = self.rgb_controller.get_current_state()
        self.rgb_controller.set_rgb_mode(
            mode_id,
            color=current_state['color'],
            brightness=current_state['brightness'],
            speed=current_state['speed']
        )
        self.status_bar.showMessage(f"Mode changed to {mode_id}")
    
    def apply_brightness(self, brightness):
        """Apply brightness change"""
        if not self.rgb_controller:
            return
            
        current_state = self.rgb_controller.get_current_state()
        self.rgb_controller.set_rgb_mode(
            current_state['mode'],
            brightness=brightness
        )
    
    def apply_speed(self, speed):
        """Apply speed change"""
        if not self.rgb_controller:
            return
            
        current_state = self.rgb_controller.get_current_state()
        self.rgb_controller.set_rgb_mode(
            current_state['mode'],
            speed=speed
        )
    
    def load_profile(self, profile_name):
        """Load a profile"""
        if not self.rgb_controller:
            return
            
        if self.rgb_controller.load_profile(profile_name):
            self.status_bar.showMessage(f"Profile '{profile_name}' loaded")
            self.update_ui_from_controller()
        else:
            self.show_error("Profile Error", f"Failed to load profile '{profile_name}'")
    
    def save_profile(self, profile_name):
        """Save current settings as profile"""
        if not self.rgb_controller:
            return
            
        if self.rgb_controller.save_profile(profile_name):
            self.status_bar.showMessage(f"Profile '{profile_name}' saved")
            self.profile_manager.refresh_profiles()
        else:
            self.show_error("Profile Error", f"Failed to save profile '{profile_name}'")
    
    def delete_profile(self, profile_name):
        """Delete a profile"""
        if not self.rgb_controller:
            return
            
        if self.rgb_controller.delete_profile(profile_name):
            self.status_bar.showMessage(f"Profile '{profile_name}' deleted")
            self.profile_manager.refresh_profiles()
        else:
            self.show_error("Profile Error", f"Failed to delete profile '{profile_name}'")
    
    def update_ui_from_controller(self):
        """Update UI elements from controller state"""
        if not self.rgb_controller:
            return
            
        state = self.rgb_controller.get_current_state()
        
        # Update control panels
        self.control_panels.update_from_state(state)
        
        # Update color picker
        r, g, b = state['color']
        from PyQt6.QtGui import QColor
        self.color_picker.set_color(QColor(r, g, b))
        
        # Update preview
        self.keyboard_preview.update_from_state(state)
    
    def update_device_status(self):
        """Update device status in status bar"""
        if not self.rgb_controller:
            self.device_status.setText("Device: Not Connected")
            return
            
        if self.rgb_controller.is_device_available():
            self.device_status.setText("Device: Connected")
        else:
            self.device_status.setText("Device: Not Found")
    
    def update_status(self):
        """Update status periodically"""
        self.update_device_status()
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About Acer Predator RGB",
                         "Acer Predator RGB Keyboard Control\n\n"
                         "A modern GUI for controlling RGB lighting on Acer gaming keyboards.\n\n"
                         "Built with PyQt6 and love for the community.\n\n"
                         "Version 1.0.0")
    
    def import_profile(self):
        """Import profile from file"""
        self.status_bar.showMessage("Import feature coming soon...")
    
    def export_profile(self):
        """Export profile to file"""
        self.status_bar.showMessage("Export feature coming soon...")
    
    def tray_activated(self, reason):
        """Handle system tray activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()
    
    def show_error(self, title, message):
        """Show error dialog"""
        QMessageBox.critical(self, title, message)
    
    def closeEvent(self, event):
        """Handle close event"""
        if self.system_tray and self.system_tray.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Acer Predator RGB")
    app.setApplicationVersion("1.0.0")
    
    # Set application icon
    app.setWindowIcon(QIcon())
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()