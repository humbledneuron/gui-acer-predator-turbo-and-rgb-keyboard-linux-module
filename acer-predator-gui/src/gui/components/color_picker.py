#!/usr/bin/env python3
"""
Color Picker Widget - Advanced color selection with HSV wheel and RGB sliders
Features preset colors and real-time preview
"""

import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, 
    QSlider, QSpinBox, QPushButton, QGridLayout, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QConicalGradient, QRadialGradient, QMouseEvent

class ColorWheel(QWidget):
    """HSV Color Wheel Widget"""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.setMouseTracking(True)
        
        # Color properties
        self.hue = 120  # Start with green
        self.saturation = 100
        self.value = 100
        self.radius = 90
        self.center = QPoint(100, 100)
        self.dragging = False
        
        self.update_color()
    
    def paintEvent(self, event):
        """Paint the color wheel"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw outer ring (hue)
        self.draw_hue_ring(painter)
        
        # Draw inner triangle (saturation/value)
        self.draw_saturation_triangle(painter)
        
        # Draw current selection indicators
        self.draw_indicators(painter)
    
    def draw_hue_ring(self, painter):
        """Draw the hue ring"""
        # Create conical gradient for hue
        gradient = QConicalGradient(self.center, 0)
        for i in range(360):
            color = QColor()
            color.setHsv(i, 255, 255)
            gradient.setColorAt(i / 360.0, color)
        
        # Draw ring
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(0, 0, 0, 0)))  # Transparent pen
        
        outer_rect = QRect(10, 10, 180, 180)
        inner_rect = QRect(40, 40, 120, 120)
        
        painter.drawEllipse(outer_rect)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationOut)
        painter.drawEllipse(inner_rect)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
    
    def draw_saturation_triangle(self, painter):
        """Draw the saturation/value triangle"""
        # Calculate triangle points
        angle_rad = math.radians(self.hue)
        top_x = self.center.x() + 60 * math.cos(angle_rad)
        top_y = self.center.y() + 60 * math.sin(angle_rad)
        
        angle_rad2 = math.radians(self.hue + 120)
        left_x = self.center.x() + 60 * math.cos(angle_rad2)
        left_y = self.center.y() + 60 * math.sin(angle_rad2)
        
        angle_rad3 = math.radians(self.hue + 240)
        right_x = self.center.x() + 60 * math.cos(angle_rad3)
        right_y = self.center.y() + 60 * math.sin(angle_rad3)
        
        # Draw gradient triangle (simplified - solid color for now)
        hue_color = QColor()
        hue_color.setHsv(int(self.hue), 255, 255)
        
        painter.setBrush(QBrush(hue_color))
        painter.setPen(QPen(QColor(64, 64, 64), 1))
        
        triangle = [QPoint(int(top_x), int(top_y)), 
                   QPoint(int(left_x), int(left_y)), 
                   QPoint(int(right_x), int(right_y))]
        painter.drawPolygon(triangle)
    
    def draw_indicators(self, painter):
        """Draw selection indicators"""
        # Hue indicator on ring
        hue_angle = math.radians(self.hue)
        hue_x = self.center.x() + 75 * math.cos(hue_angle)
        hue_y = self.center.y() + 75 * math.sin(hue_angle)
        
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        painter.setPen(QPen(Qt.GlobalColor.black, 2))
        painter.drawEllipse(int(hue_x - 4), int(hue_y - 4), 8, 8)
        
        # Saturation/Value indicator in triangle (center for now)
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(QPen(Qt.GlobalColor.white, 2))
        painter.drawEllipse(self.center.x() - 4, self.center.y() - 4, 8, 8)
    
    def mousePressEvent(self, event):
        """Handle mouse press for color selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.update_color_from_position(event.position().toPoint())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for color selection"""
        if self.dragging:
            self.update_color_from_position(event.position().toPoint())
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.dragging = False
    
    def update_color_from_position(self, pos):
        """Update color based on mouse position"""
        dx = pos.x() - self.center.x()
        dy = pos.y() - self.center.y()
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if in hue ring
        if 40 <= distance <= 90:
            angle = math.atan2(dy, dx)
            self.hue = (math.degrees(angle) + 360) % 360
            self.update_color()
        
        # Check if in saturation/value triangle (simplified)
        elif distance < 40:
            # Simple saturation/value mapping
            self.saturation = min(100, int(distance * 2.5))
            self.value = 100  # Keep value at max for now
            self.update_color()
    
    def update_color(self):
        """Update current color and emit signal"""
        self.current_color = QColor()
        self.current_color.setHsv(int(self.hue), int(self.saturation * 2.55), int(self.value * 2.55))
        self.color_changed.emit(self.current_color)
        self.update()
    
    def set_color(self, color):
        """Set color programmatically"""
        self.hue = color.hsvHue()
        self.saturation = color.hsvSaturation() / 2.55
        self.value = color.value() / 2.55
        self.current_color = color
        self.update()

class ColorSliders(QWidget):
    """RGB and HSV slider controls"""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.current_color = QColor(50, 255, 50)  # Acer green
        self.updating = False
        
        self.init_ui()
        self.connect_signals()
        self.update_sliders()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # RGB Sliders
        rgb_frame = QFrame()
        rgb_frame.setObjectName("ColorPickerFrame")
        rgb_layout = QVBoxLayout(rgb_frame)
        
        rgb_label = QLabel("RGB Values")
        rgb_label.setObjectName("SubHeaderLabel")
        rgb_layout.addWidget(rgb_label)
        
        # Red slider
        self.red_slider, self.red_spinbox = self.create_slider_pair("Red", 0, 255, 50)
        rgb_layout.addLayout(self.create_slider_layout("R", self.red_slider, self.red_spinbox))
        
        # Green slider
        self.green_slider, self.green_spinbox = self.create_slider_pair("Green", 0, 255, 255)
        rgb_layout.addLayout(self.create_slider_layout("G", self.green_slider, self.green_spinbox))
        
        # Blue slider
        self.blue_slider, self.blue_spinbox = self.create_slider_pair("Blue", 0, 255, 50)
        rgb_layout.addLayout(self.create_slider_layout("B", self.blue_slider, self.blue_spinbox))
        
        # HSV Sliders
        hsv_frame = QFrame()
        hsv_frame.setObjectName("ColorPickerFrame")
        hsv_layout = QVBoxLayout(hsv_frame)
        
        hsv_label = QLabel("HSV Values")
        hsv_label.setObjectName("SubHeaderLabel")
        hsv_layout.addWidget(hsv_label)
        
        # Hue slider
        self.hue_slider, self.hue_spinbox = self.create_slider_pair("Hue", 0, 360, 120)
        hsv_layout.addLayout(self.create_slider_layout("H", self.hue_slider, self.hue_spinbox))
        
        # Saturation slider
        self.sat_slider, self.sat_spinbox = self.create_slider_pair("Saturation", 0, 100, 100)
        hsv_layout.addLayout(self.create_slider_layout("S", self.sat_slider, self.sat_spinbox))
        
        # Value slider
        self.val_slider, self.val_spinbox = self.create_slider_pair("Value", 0, 100, 100)
        hsv_layout.addLayout(self.create_slider_layout("V", self.val_slider, self.val_spinbox))
        
        layout.addWidget(rgb_frame)
        layout.addWidget(hsv_frame)
        layout.addStretch()
    
    def create_slider_pair(self, name, min_val, max_val, initial):
        """Create a slider and spinbox pair"""
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(initial)
        
        spinbox = QSpinBox()
        spinbox.setRange(min_val, max_val)
        spinbox.setValue(initial)
        
        return slider, spinbox
    
    def create_slider_layout(self, label, slider, spinbox):
        """Create layout for slider with label and spinbox"""
        layout = QHBoxLayout()
        
        label_widget = QLabel(label)
        label_widget.setFixedWidth(20)
        
        layout.addWidget(label_widget)
        layout.addWidget(slider, stretch=1)
        layout.addWidget(spinbox)
        
        return layout
    
    def connect_signals(self):
        """Connect slider and spinbox signals"""
        # RGB sliders
        self.red_slider.valueChanged.connect(lambda v: self.red_spinbox.setValue(v))
        self.red_spinbox.valueChanged.connect(lambda v: self.red_slider.setValue(v))
        self.red_slider.valueChanged.connect(self.rgb_changed)
        
        self.green_slider.valueChanged.connect(lambda v: self.green_spinbox.setValue(v))
        self.green_spinbox.valueChanged.connect(lambda v: self.green_slider.setValue(v))
        self.green_slider.valueChanged.connect(self.rgb_changed)
        
        self.blue_slider.valueChanged.connect(lambda v: self.blue_spinbox.setValue(v))
        self.blue_spinbox.valueChanged.connect(lambda v: self.blue_slider.setValue(v))
        self.blue_slider.valueChanged.connect(self.rgb_changed)
        
        # HSV sliders
        self.hue_slider.valueChanged.connect(lambda v: self.hue_spinbox.setValue(v))
        self.hue_spinbox.valueChanged.connect(lambda v: self.hue_slider.setValue(v))
        self.hue_slider.valueChanged.connect(self.hsv_changed)
        
        self.sat_slider.valueChanged.connect(lambda v: self.sat_spinbox.setValue(v))
        self.sat_spinbox.valueChanged.connect(lambda v: self.sat_slider.setValue(v))
        self.sat_slider.valueChanged.connect(self.hsv_changed)
        
        self.val_slider.valueChanged.connect(lambda v: self.val_spinbox.setValue(v))
        self.val_spinbox.valueChanged.connect(lambda v: self.val_slider.setValue(v))
        self.val_slider.valueChanged.connect(self.hsv_changed)
    
    def rgb_changed(self):
        """Handle RGB slider changes"""
        if self.updating:
            return
            
        r = self.red_slider.value()
        g = self.green_slider.value()
        b = self.blue_slider.value()
        
        self.current_color = QColor(r, g, b)
        self.update_hsv_sliders()
        self.color_changed.emit(self.current_color)
    
    def hsv_changed(self):
        """Handle HSV slider changes"""
        if self.updating:
            return
            
        h = self.hue_slider.value()
        s = self.sat_slider.value()
        v = self.val_slider.value()
        
        self.current_color = QColor()
        self.current_color.setHsv(h, int(s * 2.55), int(v * 2.55))
        self.update_rgb_sliders()
        self.color_changed.emit(self.current_color)
    
    def update_sliders(self):
        """Update all sliders from current color"""
        self.updating = True
        
        # Update RGB sliders
        self.red_slider.setValue(self.current_color.red())
        self.green_slider.setValue(self.current_color.green())
        self.blue_slider.setValue(self.current_color.blue())
        
        # Update HSV sliders
        self.hue_slider.setValue(self.current_color.hsvHue())
        self.sat_slider.setValue(int(self.current_color.hsvSaturation() / 2.55))
        self.val_slider.setValue(int(self.current_color.value() / 2.55))
        
        self.updating = False
    
    def update_rgb_sliders(self):
        """Update RGB sliders only"""
        self.updating = True
        self.red_slider.setValue(self.current_color.red())
        self.green_slider.setValue(self.current_color.green())
        self.blue_slider.setValue(self.current_color.blue())
        self.updating = False
    
    def update_hsv_sliders(self):
        """Update HSV sliders only"""
        self.updating = True
        self.hue_slider.setValue(self.current_color.hsvHue())
        self.sat_slider.setValue(int(self.current_color.hsvSaturation() / 2.55))
        self.val_slider.setValue(int(self.current_color.value() / 2.55))
        self.updating = False
    
    def set_color(self, color):
        """Set color from external source"""
        self.current_color = color
        self.update_sliders()

class PresetColors(QWidget):
    """Preset color buttons"""
    
    color_selected = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize preset colors"""
        layout = QVBoxLayout(self)
        
        label = QLabel("Preset Colors")
        label.setObjectName("SubHeaderLabel")
        layout.addWidget(label)
        
        # Color grid
        grid = QGridLayout()
        
        # Define preset colors
        presets = [
            ("#83B81A", "Acer Green"),    # Acer brand color
            ("#FF0000", "Red"),
            ("#00FF00", "Green"),
            ("#0000FF", "Blue"),
            ("#FFFF00", "Yellow"),
            ("#FF00FF", "Magenta"),
            ("#00FFFF", "Cyan"),
            ("#FFFFFF", "White"),
            ("#FF8000", "Orange"),
            ("#8000FF", "Purple"),
            ("#FF0080", "Pink"),
            ("#80FF00", "Lime"),
            ("#0080FF", "Sky Blue"),
            ("#FF8080", "Light Red"),
            ("#80FF80", "Light Green"),
            ("#8080FF", "Light Blue"),
        ]
        
        self.color_buttons = []
        
        for i, (color_hex, name) in enumerate(presets):
            button = QPushButton()
            button.setFixedSize(40, 40)
            button.setToolTip(name)
            
            color = QColor(color_hex)
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex};
                    border: 2px solid #404040;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    border-color: #83B81A;
                }}
                QPushButton:pressed {{
                    border-color: #FFFFFF;
                }}
            """)
            
            button.clicked.connect(lambda checked, c=color: self.color_selected.emit(c))
            
            row = i // 4
            col = i % 4
            grid.addWidget(button, row, col)
            
            self.color_buttons.append(button)
        
        layout.addLayout(grid)
        layout.addStretch()

class ColorPickerWidget(QWidget):
    """Main color picker widget combining all components"""
    
    color_changed = pyqtSignal(QColor)
    
    def __init__(self):
        super().__init__()
        self.current_color = QColor(50, 255, 50)  # Acer green
        
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(16)
        
        # Left side - Color wheel
        left_layout = QVBoxLayout()
        
        wheel_label = QLabel("Color Wheel")
        wheel_label.setObjectName("SubHeaderLabel")
        wheel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.color_wheel = ColorWheel()
        
        left_layout.addWidget(wheel_label)
        left_layout.addWidget(self.color_wheel, alignment=Qt.AlignmentFlag.AlignCenter)
        left_layout.addStretch()
        
        # Right side - Sliders and presets
        right_layout = QVBoxLayout()
        
        self.color_sliders = ColorSliders()
        self.preset_colors = PresetColors()
        
        right_layout.addWidget(self.color_sliders)
        right_layout.addWidget(self.preset_colors)
        
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
    
    def connect_signals(self):
        """Connect signals between components"""
        self.color_wheel.color_changed.connect(self.wheel_color_changed)
        self.color_sliders.color_changed.connect(self.slider_color_changed)
        self.preset_colors.color_selected.connect(self.preset_color_selected)
    
    def wheel_color_changed(self, color):
        """Handle color wheel changes"""
        self.current_color = color
        self.color_sliders.set_color(color)
        self.color_changed.emit(color)
    
    def slider_color_changed(self, color):
        """Handle slider changes"""
        self.current_color = color
        self.color_wheel.set_color(color)
        self.color_changed.emit(color)
    
    def preset_color_selected(self, color):
        """Handle preset color selection"""
        self.current_color = color
        self.color_wheel.set_color(color)
        self.color_sliders.set_color(color)
        self.color_changed.emit(color)
    
    def set_color(self, color):
        """Set color from external source"""
        self.current_color = color
        self.color_wheel.set_color(color)
        self.color_sliders.set_color(color)
    
    def get_color(self):
        """Get current color"""
        return self.current_color