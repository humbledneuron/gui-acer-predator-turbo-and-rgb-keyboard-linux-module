#!/usr/bin/env python3
"""
Profile Manager Widget - Manage RGB lighting profiles
Features profile cards, save/load/delete functionality, and visual previews
"""

import json
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox, QScrollArea,
    QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter, QFont

class ProfileCard(QFrame):
    """Individual profile card widget"""
    
    clicked = pyqtSignal(str)  # profile name
    delete_requested = pyqtSignal(str)  # profile name
    
    def __init__(self, profile_name: str, profile_data: dict):
        super().__init__()
        self.profile_name = profile_name
        self.profile_data = profile_data
        
        self.setObjectName("ProfileCard")
        self.setFixedSize(200, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.init_ui()
        self.create_preview()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Header with name and delete button
        header_layout = QHBoxLayout()
        
        self.name_label = QLabel(self.profile_name)
        self.name_label.setObjectName("SubHeaderLabel")
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setPointSize(10)
        font.setBold(True)
        self.name_label.setFont(font)
        
        self.delete_button = QPushButton("×")
        self.delete_button.setObjectName("DangerButton")
        self.delete_button.setFixedSize(20, 20)
        self.delete_button.setToolTip("Delete Profile")
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.profile_name))
        
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.delete_button)
        
        # Preview area
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(180, 60)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: #1A1A1A;
            }
        """)
        
        # Info label
        mode_name = self.get_mode_name(self.profile_data.get('mode', 0))
        brightness = self.profile_data.get('brightness', 100)
        self.info_label = QLabel(f"{mode_name} • {brightness}%")
        self.info_label.setObjectName("InfoLabel")
        font = self.info_label.font()
        font.setPointSize(8)
        self.info_label.setFont(font)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.preview_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignCenter)
    
    def get_mode_name(self, mode_id):
        """Get mode name from ID"""
        mode_names = {
            0: "Static",
            1: "Breath",
            2: "Neon",
            3: "Wave",
            4: "Shifting",
            5: "Zoom"
        }
        return mode_names.get(mode_id, "Unknown")
    
    def create_preview(self):
        """Create a visual preview of the profile"""
        pixmap = QPixmap(180, 60)
        pixmap.fill(QColor(26, 26, 26))  # Background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get profile color
        color_data = self.profile_data.get('color', (50, 255, 50))
        color = QColor(color_data[0], color_data[1], color_data[2])
        
        # Apply brightness
        brightness = self.profile_data.get('brightness', 100)
        if brightness < 100:
            factor = brightness / 100.0
            color = QColor(
                int(color.red() * factor),
                int(color.green() * factor),
                int(color.blue() * factor)
            )
        
        # Draw 4 zones
        zone_width = 40
        zone_height = 50
        margin = 5
        
        for zone in range(4):
            x = margin + zone * (zone_width + margin)
            y = 5
            
            # Zone color (for static mode, could be different per zone)
            zone_color = color
            
            # Draw zone
            painter.setBrush(zone_color)
            painter.setPen(QColor(64, 64, 64))
            painter.drawRoundedRect(x, y, zone_width, zone_height, 4, 4)
            
            # Add mode-specific effects
            mode = self.profile_data.get('mode', 0)
            if mode == 1:  # Breathing - add pulsing effect
                painter.setBrush(QColor(zone_color.red(), zone_color.green(), zone_color.blue(), 128))
                painter.drawRoundedRect(x + 5, y + 5, zone_width - 10, zone_height - 10, 2, 2)
            elif mode == 3:  # Wave - add gradient
                painter.setBrush(QColor(zone_color.red() // 2, zone_color.green() // 2, zone_color.blue() // 2))
                painter.drawRoundedRect(x + zone * 3, y, zone_width - zone * 3, zone_height, 4, 4)
        
        painter.end()
        self.preview_label.setPixmap(pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse click"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Don't emit clicked if delete button was clicked
            if not self.delete_button.geometry().contains(event.position().toPoint()):
                self.clicked.emit(self.profile_name)

class ProfileManagerWidget(QWidget):
    """Main profile manager widget"""
    
    profile_selected = pyqtSignal(str)  # profile name
    profile_saved = pyqtSignal(str)     # profile name
    profile_deleted = pyqtSignal(str)   # profile name
    
    def __init__(self):
        super().__init__()
        self.config_dir = Path.home() / ".config" / "predator" / "saved profiles"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.profile_cards = []
        
        self.init_ui()
        self.refresh_profiles()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Header with controls
        header_layout = QHBoxLayout()
        
        self.save_button = QPushButton("💾 Save")
        self.save_button.setToolTip("Save current settings as new profile")
        self.save_button.clicked.connect(self.save_new_profile)
        
        self.refresh_button = QPushButton("🔄")
        self.refresh_button.setFixedSize(30, 30)
        self.refresh_button.setToolTip("Refresh profiles")
        self.refresh_button.clicked.connect(self.refresh_profiles)
        
        header_layout.addWidget(self.save_button)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_button)
        
        # Scroll area for profile cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Container for profile cards
        self.profiles_container = QWidget()
        self.profiles_layout = QVBoxLayout(self.profiles_container)
        self.profiles_layout.setSpacing(8)
        self.profiles_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll_area.setWidget(self.profiles_container)
        
        # No profiles message
        self.no_profiles_label = QLabel("No saved profiles\nCreate one by clicking Save")
        self.no_profiles_label.setObjectName("InfoLabel")
        self.no_profiles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_profiles_label.setWordWrap(True)
        
        layout.addLayout(header_layout)
        layout.addWidget(scroll_area)
        layout.addWidget(self.no_profiles_label)
    
    def refresh_profiles(self):
        """Refresh the profile list"""
        # Clear existing cards
        for card in self.profile_cards:
            card.deleteLater()
        self.profile_cards.clear()
        
        # Clear layout
        while self.profiles_layout.count():
            child = self.profiles_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Load profiles from disk
        profile_files = list(self.config_dir.glob("*.json"))
        
        if not profile_files:
            self.no_profiles_label.show()
            return
        else:
            self.no_profiles_label.hide()
        
        # Create cards for each profile
        for profile_file in sorted(profile_files):
            try:
                with open(profile_file, 'r') as f:
                    profile_data = json.load(f)
                
                profile_name = profile_file.stem
                card = ProfileCard(profile_name, profile_data)
                card.clicked.connect(self.profile_selected.emit)
                card.delete_requested.connect(self.delete_profile)
                
                self.profile_cards.append(card)
                self.profiles_layout.addWidget(card)
                
            except Exception as e:
                print(f"Error loading profile {profile_file}: {e}")
        
        # Add stretch to push cards to top
        self.profiles_layout.addStretch()
    
    def save_new_profile(self):
        """Save a new profile"""
        name, ok = QInputDialog.getText(
            self, 
            "Save Profile", 
            "Enter profile name:",
            text="My Profile"
        )
        
        if ok and name.strip():
            # Clean the name
            clean_name = "".join(c for c in name.strip() if c.isalnum() or c in (' ', '-', '_'))
            if not clean_name:
                QMessageBox.warning(self, "Invalid Name", "Please enter a valid profile name.")
                return
            
            # Check if profile already exists
            profile_path = self.config_dir / f"{clean_name}.json"
            if profile_path.exists():
                reply = QMessageBox.question(
                    self, 
                    "Profile Exists", 
                    f"Profile '{clean_name}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            self.profile_saved.emit(clean_name)
            self.refresh_profiles()
    
    def delete_profile(self, profile_name):
        """Delete a profile"""
        reply = QMessageBox.question(
            self,
            "Delete Profile",
            f"Are you sure you want to delete profile '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.profile_deleted.emit(profile_name)
            self.refresh_profiles()
    
    def add_default_profiles(self):
        """Add some default profiles"""
        default_profiles = [
            {
                "name": "Acer Green",
                "data": {
                    "mode": 1,  # Breathing
                    "brightness": 100,
                    "speed": 5,
                    "color": (131, 184, 26),  # #83B81A
                    "direction": 1,
                    "zone": 1
                }
            },
            {
                "name": "Gaming Red",
                "data": {
                    "mode": 4,  # Shifting
                    "brightness": 90,
                    "speed": 7,
                    "color": (255, 0, 0),
                    "direction": 1,
                    "zone": 1
                }
            },
            {
                "name": "Cool Blue",
                "data": {
                    "mode": 3,  # Wave
                    "brightness": 80,
                    "speed": 4,
                    "color": (0, 100, 255),
                    "direction": 2,
                    "zone": 1
                }
            },
            {
                "name": "Rainbow",
                "data": {
                    "mode": 2,  # Neon
                    "brightness": 100,
                    "speed": 6,
                    "color": (255, 255, 255),
                    "direction": 1,
                    "zone": 1
                }
            }
        ]
        
        for profile in default_profiles:
            profile_path = self.config_dir / f"{profile['name']}.json"
            if not profile_path.exists():
                try:
                    with open(profile_path, 'w') as f:
                        json.dump(profile['data'], f, indent=2)
                except Exception as e:
                    print(f"Error creating default profile {profile['name']}: {e}")
        
        self.refresh_profiles()
    
    def import_profile(self, file_path):
        """Import profile from file"""
        try:
            with open(file_path, 'r') as f:
                profile_data = json.load(f)
            
            # Get name from file or ask user
            suggested_name = Path(file_path).stem
            name, ok = QInputDialog.getText(
                self,
                "Import Profile",
                "Enter name for imported profile:",
                text=suggested_name
            )
            
            if ok and name.strip():
                clean_name = "".join(c for c in name.strip() if c.isalnum() or c in (' ', '-', '_'))
                profile_path = self.config_dir / f"{clean_name}.json"
                
                with open(profile_path, 'w') as f:
                    json.dump(profile_data, f, indent=2)
                
                self.refresh_profiles()
                QMessageBox.information(self, "Success", f"Profile '{clean_name}' imported successfully!")
                
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import profile: {e}")
    
    def export_profile(self, profile_name, file_path):
        """Export profile to file"""
        try:
            source_path = self.config_dir / f"{profile_name}.json"
            
            with open(source_path, 'r') as src:
                profile_data = json.load(src)
            
            with open(file_path, 'w') as dst:
                json.dump(profile_data, dst, indent=2)
            
            QMessageBox.information(self, "Success", f"Profile '{profile_name}' exported successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export profile: {e}")

class QuickProfilesWidget(QWidget):
    """Quick access profile buttons"""
    
    profile_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize quick profiles"""
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        label = QLabel("Quick Access")
        label.setObjectName("InfoLabel")
        
        # Quick profile buttons
        profiles = ["Acer Green", "Gaming", "Rainbow", "Off"]
        
        for profile in profiles:
            button = QPushButton(profile)
            button.setFixedHeight(30)
            if profile == "Off":
                button.setObjectName("DangerButton")
            else:
                button.setObjectName("SecondaryButton")
            
            button.clicked.connect(lambda checked, p=profile: self.profile_selected.emit(p))
            layout.addWidget(button)
        
        layout.addStretch()
        layout.addWidget(label)