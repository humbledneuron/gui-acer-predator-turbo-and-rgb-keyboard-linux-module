#!/usr/bin/env python3
"""
Keyboard Preview Widget - Visual representation of RGB keyboard
Shows live preview of lighting effects and zones
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient

class KeyWidget(QFrame):
    """Individual key representation"""
    
    def __init__(self, x: int, y: int, width: int = 40, height: int = 40):
        super().__init__()
        self.zone_id = 1
        self.current_color = QColor(50, 255, 50)  # Default Acer green
        self.brightness = 100
        self.is_lit = True
        
        self.setFixedSize(width, height)
        self.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: rgb({self.current_color.red()}, {self.current_color.green()}, {self.current_color.blue()});
            }}
        """)
    
    def set_color(self, color: QColor, brightness: int = 100):
        """Set key color with brightness"""
        self.current_color = color
        self.brightness = brightness
        
        # Apply brightness
        if brightness < 100:
            factor = brightness / 100.0
            r = int(color.red() * factor)
            g = int(color.green() * factor)
            b = int(color.blue() * factor)
            adjusted_color = QColor(r, g, b)
        else:
            adjusted_color = color
        
        if brightness == 0:
            adjusted_color = QColor(30, 30, 30)  # Dark gray when off
        
        self.setStyleSheet(f"""
            QFrame {{
                border: 1px solid #404040;
                border-radius: 6px;
                background-color: rgb({adjusted_color.red()}, {adjusted_color.green()}, {adjusted_color.blue()});
            }}
        """)
    
    def set_zone(self, zone_id: int):
        """Set the zone this key belongs to"""
        self.zone_id = zone_id

class KeyboardPreviewWidget(QWidget):
    """Main keyboard preview widget showing 4-zone RGB layout"""
    
    # Signals
    zone_clicked = pyqtSignal(int)  # Emitted when a zone is clicked
    
    def __init__(self):
        super().__init__()
        
        # Animation properties
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_frame = 0
        
        # Current state
        self.current_mode = 3  # Wave mode default
        self.current_colors = [(50, 255, 50)] * 4  # 4 zones, default Acer green
        self.current_brightness = 100
        self.current_speed = 5
        self.current_direction = 1  # 1 = right to left, 2 = left to right
        
        # Keys storage
        self.keys = []
        self.zone_colors = [QColor(50, 255, 50)] * 4
        
        self.init_ui()
        self.create_keyboard_layout()
        self.start_animation()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setFixedSize(500, 200)
        self.setObjectName("KeyboardPreview")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Live Preview")
        title.setObjectName("SubHeaderLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Keyboard container
        self.keyboard_container = QFrame()
        self.keyboard_container.setObjectName("KeyboardContainer")
        self.keyboard_container.setFixedSize(460, 120)
        
        # Zone labels
        zone_layout = QHBoxLayout()
        for i in range(4):
            zone_label = QLabel(f"Zone {i+1}")
            zone_label.setObjectName("InfoLabel")
            zone_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            zone_layout.addWidget(zone_label)
        
        layout.addWidget(title)
        layout.addWidget(self.keyboard_container)
        layout.addLayout(zone_layout)
        layout.addStretch()
        
    def create_keyboard_layout(self):
        """Create the keyboard key layout"""
        # Clear existing keys
        for key in self.keys:
            key.deleteLater()
        self.keys.clear()
        
        # Create 4 zones with keys
        # Zone layout: [Zone 1][Zone 2][Zone 3][Zone 4]
        zone_width = 115  # Width per zone
        key_size = 12
        keys_per_zone = 8
        
        for zone in range(4):
            zone_x = zone * zone_width
            
            # Create keys for this zone
            for key_idx in range(keys_per_zone):
                x = zone_x + (key_idx % 4) * (key_size + 2) + 10
                y = 20 + (key_idx // 4) * (key_size + 2)
                
                key = KeyWidget(x, y, key_size, key_size)
                key.set_zone(zone + 1)
                key.set_color(self.zone_colors[zone], self.current_brightness)
                key.setParent(self.keyboard_container)
                key.move(x, y)
                key.show()
                
                self.keys.append(key)
        
        # Add some larger keys for visual appeal
        for zone in range(4):
            zone_x = zone * zone_width
            
            # Add a larger "spacebar-like" key at the bottom
            x = zone_x + 10
            y = 80
            
            key = KeyWidget(x, y, zone_width - 20, 15)
            key.set_zone(zone + 1)
            key.set_color(self.zone_colors[zone], self.current_brightness)
            key.setParent(self.keyboard_container)
            key.move(x, y)
            key.show()
            
            self.keys.append(key)
    
    def update_color(self, color: QColor):
        """Update preview with new color"""
        # For modes that support color, update all zones
        if self.current_mode in [0, 1, 4, 5]:  # Static, Breath, Shifting, Zoom
            for i in range(4):
                self.zone_colors[i] = color
            self.update_keys()
    
    def update_zone_color(self, zone: int, color: QColor):
        """Update specific zone color (for static mode)"""
        if 1 <= zone <= 4:
            self.zone_colors[zone - 1] = color
            self.update_keys()
    
    def update_brightness(self, brightness: int):
        """Update brightness"""
        self.current_brightness = brightness
        self.update_keys()
    
    def update_mode(self, mode: int):
        """Update RGB mode"""
        self.current_mode = mode
        self.update_animation_mode()
        self.update_keys()
    
    def update_speed(self, speed: int):
        """Update animation speed"""
        self.current_speed = speed
        self.update_animation_speed()
    
    def update_direction(self, direction: int):
        """Update animation direction"""
        self.current_direction = direction
    
    def update_from_state(self, state):
        """Update preview from controller state"""
        self.current_mode = state.get('mode', 3)
        self.current_brightness = state.get('brightness', 100)
        self.current_speed = state.get('speed', 5)
        self.current_direction = state.get('direction', 1)
        
        # Update colors
        color = state.get('color', (50, 255, 50))
        new_color = QColor(color[0], color[1], color[2])
        
        if self.current_mode == 0:  # Static mode - zone specific
            zone = state.get('zone', 1)
            self.update_zone_color(zone, new_color)
        else:  # Other modes - all zones
            self.update_color(new_color)
        
        self.update_mode(self.current_mode)
        self.update_speed(self.current_speed)
    
    def update_keys(self):
        """Update all key colors"""
        for key in self.keys:
            zone_idx = key.zone_id - 1
            if 0 <= zone_idx < 4:
                key.set_color(self.zone_colors[zone_idx], self.current_brightness)
    
    def start_animation(self):
        """Start the animation timer"""
        if self.current_mode in [1, 2, 3, 4, 5]:  # Animated modes
            self.animation_timer.start(100)  # 10 FPS
        else:
            self.animation_timer.stop()
    
    def update_animation_mode(self):
        """Update animation based on mode"""
        if self.current_mode in [1, 2, 3, 4, 5]:  # Animated modes
            self.start_animation()
        else:
            self.animation_timer.stop()
            self.update_keys()  # Update for static mode
    
    def update_animation_speed(self):
        """Update animation speed"""
        if self.animation_timer.isActive():
            # Adjust timer interval based on speed (1-9)
            # Speed 1 = slowest (200ms), Speed 9 = fastest (50ms)
            interval = max(50, 250 - (self.current_speed * 20))
            self.animation_timer.setInterval(interval)
    
    def update_animation(self):
        """Update animation frame"""
        self.animation_frame += 1
        
        if self.current_mode == 1:  # Breathing
            self.animate_breathing()
        elif self.current_mode == 2:  # Neon
            self.animate_neon()
        elif self.current_mode == 3:  # Wave
            self.animate_wave()
        elif self.current_mode == 4:  # Shifting
            self.animate_shifting()
        elif self.current_mode == 5:  # Zoom
            self.animate_zoom()
    
    def animate_breathing(self):
        """Breathing animation"""
        import math
        
        # Create breathing effect with sine wave
        brightness_factor = (math.sin(self.animation_frame * 0.1) + 1) / 2
        effective_brightness = int(self.current_brightness * brightness_factor)
        
        for key in self.keys:
            zone_idx = key.zone_id - 1
            if 0 <= zone_idx < 4:
                key.set_color(self.zone_colors[zone_idx], effective_brightness)
    
    def animate_neon(self):
        """Neon rainbow animation"""
        import math
        
        # Create rainbow effect
        for i, key in enumerate(self.keys):
            hue = (self.animation_frame * 2 + i * 10) % 360
            color = QColor()
            color.setHsv(hue, 255, 255)
            key.set_color(color, self.current_brightness)
    
    def animate_wave(self):
        """Wave animation"""
        import math
        
        # Create wave effect across zones
        for key in self.keys:
            zone_idx = key.zone_id - 1
            
            # Calculate wave position
            if self.current_direction == 1:  # Right to left
                wave_pos = (self.animation_frame - zone_idx * 10) % 100
            else:  # Left to right
                wave_pos = (self.animation_frame + zone_idx * 10) % 100
            
            # Create wave brightness
            brightness_factor = (math.sin(wave_pos * 0.1) + 1) / 2
            effective_brightness = int(self.current_brightness * brightness_factor)
            
            # Use rainbow colors for wave
            hue = (wave_pos * 3.6) % 360
            color = QColor()
            color.setHsv(int(hue), 255, 255)
            key.set_color(color, effective_brightness)
    
    def animate_shifting(self):
        """Color shifting animation"""
        import math
        
        # Shift through colors
        hue = (self.animation_frame * 2) % 360
        base_color = QColor()
        base_color.setHsv(hue, 255, 255)
        
        # Mix with original color
        original = self.zone_colors[0]  # Use first zone color as base
        
        for key in self.keys:
            # Create shifting effect
            shift_amount = math.sin(self.animation_frame * 0.05) * 0.5 + 0.5
            
            r = int(original.red() * (1 - shift_amount) + base_color.red() * shift_amount)
            g = int(original.green() * (1 - shift_amount) + base_color.green() * shift_amount)
            b = int(original.blue() * (1 - shift_amount) + base_color.blue() * shift_amount)
            
            mixed_color = QColor(r, g, b)
            key.set_color(mixed_color, self.current_brightness)
    
    def animate_zoom(self):
        """Zoom animation"""
        import math
        
        # Create pulsing zoom effect
        zoom_factor = (math.sin(self.animation_frame * 0.1) + 1) / 2
        
        # Create zoom effect with brightness and slight color shift
        for i, key in enumerate(self.keys):
            zone_idx = key.zone_id - 1
            base_color = self.zone_colors[zone_idx]
            
            # Apply zoom brightness
            effective_brightness = int(self.current_brightness * (0.3 + 0.7 * zoom_factor))
            
            # Slight color shift for zoom effect
            r = min(255, int(base_color.red() * (0.8 + 0.2 * zoom_factor)))
            g = min(255, int(base_color.green() * (0.8 + 0.2 * zoom_factor)))
            b = min(255, int(base_color.blue() * (0.8 + 0.2 * zoom_factor)))
            
            zoom_color = QColor(r, g, b)
            key.set_color(zoom_color, effective_brightness)
    
    def mousePressEvent(self, event):
        """Handle mouse clicks for zone selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Determine which zone was clicked
            x = event.position().x()
            zone_width = self.keyboard_container.width() / 4
            
            zone = int(x // zone_width) + 1
            if 1 <= zone <= 4:
                self.zone_clicked.emit(zone)