#!/usr/bin/env python3
"""
Control Panels Widget - Main RGB control interface
Features mode selection, brightness/speed controls, and zone management
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton, 
    QSlider, QSpinBox, QComboBox, QButtonGroup, QGridLayout, QGroupBox,
    QCheckBox, QTabWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QFont

class ModeSelector(QWidget):
    """RGB Mode selection widget"""
    
    mode_changed = pyqtSignal(int)  # mode ID
    
    def __init__(self):
        super().__init__()
        self.current_mode = 3  # Default to Wave
        self.mode_buttons = []
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("RGB Mode")
        title.setObjectName("SubHeaderLabel")
        
        # Mode buttons
        self.button_group = QButtonGroup(self)
        self.button_group.buttonClicked.connect(self.on_mode_selected)
        
        modes = [
            (0, "Static", "🎯", "Solid colors per zone"),
            (1, "Breath", "💨", "Breathing effect"),
            (2, "Neon", "🌈", "Rainbow cycling"),
            (3, "Wave", "🌊", "Wave animation"),
            (4, "Shifting", "↔️", "Color shifting"),
            (5, "Zoom", "🔍", "Zoom effect")
        ]
        
        grid_layout = QGridLayout()
        
        for i, (mode_id, name, icon, description) in enumerate(modes):
            button = QPushButton(f"{icon} {name}")
            button.setCheckable(True)
            button.setFixedHeight(50)
            button.setToolTip(description)
            
            # Special styling for different modes
            if mode_id == 0:  # Static
                button.setObjectName("SecondaryButton")
            elif mode_id in [2, 3]:  # Neon, Wave - animated modes
                button.setProperty("animated", True)
            
            self.button_group.addButton(button, mode_id)
            self.mode_buttons.append(button)
            
            row = i // 2
            col = i % 2
            grid_layout.addWidget(button, row, col)
        
        # Set default selection
        self.mode_buttons[3].setChecked(True)  # Wave mode
        
        layout.addWidget(title)
        layout.addLayout(grid_layout)
    
    def on_mode_selected(self, button):
        """Handle mode selection"""
        mode_id = self.button_group.id(button)
        self.current_mode = mode_id
        self.mode_changed.emit(mode_id)
    
    def set_mode(self, mode_id):
        """Set mode programmatically"""
        if 0 <= mode_id < len(self.mode_buttons):
            self.mode_buttons[mode_id].setChecked(True)
            self.current_mode = mode_id

class BrightnessControl(QWidget):
    """Brightness control slider"""
    
    brightness_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_brightness = 100
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Brightness")
        title.setObjectName("SubHeaderLabel")
        
        # Slider and spinbox layout
        control_layout = QHBoxLayout()
        
        # Brightness slider
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(100)
        self.brightness_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.brightness_slider.setTickInterval(25)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        
        # Brightness spinbox
        self.brightness_spinbox = QSpinBox()
        self.brightness_spinbox.setRange(0, 100)
        self.brightness_spinbox.setValue(100)
        self.brightness_spinbox.setSuffix("%")
        self.brightness_spinbox.valueChanged.connect(self.on_brightness_changed)
        
        # Power button
        self.power_button = QPushButton("⚡")
        self.power_button.setFixedSize(40, 40)
        self.power_button.setCheckable(True)
        self.power_button.setChecked(True)
        self.power_button.setToolTip("Toggle RGB Power")
        self.power_button.toggled.connect(self.on_power_toggled)
        
        # Quick brightness buttons
        quick_layout = QHBoxLayout()
        quick_buttons = [
            (25, "25%"),
            (50, "50%"),
            (75, "75%"),
            (100, "100%")
        ]
        
        for brightness, label in quick_buttons:
            button = QPushButton(label)
            button.setObjectName("SecondaryButton")
            button.setFixedHeight(30)
            button.clicked.connect(lambda checked, b=brightness: self.set_brightness(b))
            quick_layout.addWidget(button)
        
        control_layout.addWidget(self.brightness_slider, stretch=1)
        control_layout.addWidget(self.brightness_spinbox)
        control_layout.addWidget(self.power_button)
        
        layout.addWidget(title)
        layout.addLayout(control_layout)
        layout.addLayout(quick_layout)
    
    def on_brightness_changed(self, value):
        """Handle brightness change"""
        # Sync slider and spinbox
        if self.sender() == self.brightness_slider:
            self.brightness_spinbox.setValue(value)
        elif self.sender() == self.brightness_spinbox:
            self.brightness_slider.setValue(value)
        
        self.current_brightness = value
        self.brightness_changed.emit(value)
        
        # Update power button state
        self.power_button.setChecked(value > 0)
    
    def on_power_toggled(self, checked):
        """Handle power button toggle"""
        if checked:
            if self.current_brightness == 0:
                self.set_brightness(100)
        else:
            self.set_brightness(0)
    
    def set_brightness(self, brightness):
        """Set brightness programmatically"""
        self.brightness_slider.setValue(brightness)
        self.current_brightness = brightness

class SpeedControl(QWidget):
    """Animation speed control"""
    
    speed_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_speed = 5
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Animation Speed")
        title.setObjectName("SubHeaderLabel")
        
        # Speed slider
        control_layout = QHBoxLayout()
        
        slow_label = QLabel("Slow")
        slow_label.setObjectName("InfoLabel")
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 9)
        self.speed_slider.setValue(5)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(1)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        
        fast_label = QLabel("Fast")
        fast_label.setObjectName("InfoLabel")
        
        self.speed_value = QLabel("5")
        self.speed_value.setObjectName("SubHeaderLabel")
        self.speed_value.setFixedWidth(20)
        self.speed_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        control_layout.addWidget(slow_label)
        control_layout.addWidget(self.speed_slider, stretch=1)
        control_layout.addWidget(fast_label)
        control_layout.addWidget(self.speed_value)
        
        layout.addWidget(title)
        layout.addLayout(control_layout)
    
    def on_speed_changed(self, value):
        """Handle speed change"""
        self.current_speed = value
        self.speed_value.setText(str(value))
        self.speed_changed.emit(value)
    
    def set_speed(self, speed):
        """Set speed programmatically"""
        self.speed_slider.setValue(speed)
        self.current_speed = speed

class DirectionControl(QWidget):
    """Animation direction control"""
    
    direction_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_direction = 1
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Direction")
        title.setObjectName("SubHeaderLabel")
        
        # Direction buttons
        button_layout = QHBoxLayout()
        
        self.left_to_right_btn = QPushButton("→ Left to Right")
        self.left_to_right_btn.setCheckable(True)
        self.left_to_right_btn.setChecked(True)
        
        self.right_to_left_btn = QPushButton("← Right to Left")
        self.right_to_left_btn.setCheckable(True)
        
        # Button group for exclusive selection
        self.direction_group = QButtonGroup(self)
        self.direction_group.addButton(self.left_to_right_btn, 2)  # Left to right = 2
        self.direction_group.addButton(self.right_to_left_btn, 1)  # Right to left = 1
        self.direction_group.buttonClicked.connect(self.on_direction_changed)
        
        button_layout.addWidget(self.left_to_right_btn)
        button_layout.addWidget(self.right_to_left_btn)
        
        layout.addWidget(title)
        layout.addLayout(button_layout)
    
    def on_direction_changed(self, button):
        """Handle direction change"""
        direction = self.direction_group.id(button)
        self.current_direction = direction
        self.direction_changed.emit(direction)
    
    def set_direction(self, direction):
        """Set direction programmatically"""
        if direction == 1:
            self.right_to_left_btn.setChecked(True)
        else:
            self.left_to_right_btn.setChecked(True)
        self.current_direction = direction

class ZoneControl(QWidget):
    """Zone selection for static mode"""
    
    zone_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_zone = 1
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Zone Selection")
        title.setObjectName("SubHeaderLabel")
        
        # Zone buttons
        button_layout = QGridLayout()
        
        self.zone_group = QButtonGroup(self)
        self.zone_group.buttonClicked.connect(self.on_zone_changed)
        
        zone_colors = ["🔴", "🟢", "🔵", "🟡"]  # Visual indicators
        
        for i in range(4):
            zone_id = i + 1
            button = QPushButton(f"{zone_colors[i]} Zone {zone_id}")
            button.setCheckable(True)
            button.setFixedHeight(40)
            
            if zone_id == 1:
                button.setChecked(True)
            
            self.zone_group.addButton(button, zone_id)
            
            row = i // 2
            col = i % 2
            button_layout.addWidget(button, row, col)
        
        # All zones button
        all_zones_btn = QPushButton("🌈 All Zones")
        all_zones_btn.setObjectName("SecondaryButton")
        all_zones_btn.clicked.connect(self.select_all_zones)
        
        layout.addWidget(title)
        layout.addLayout(button_layout)
        layout.addWidget(all_zones_btn)
    
    def on_zone_changed(self, button):
        """Handle zone selection"""
        zone_id = self.zone_group.id(button)
        self.current_zone = zone_id
        self.zone_changed.emit(zone_id)
    
    def select_all_zones(self):
        """Apply to all zones"""
        for zone in range(1, 5):
            self.zone_changed.emit(zone)
    
    def set_zone(self, zone_id):
        """Set zone programmatically"""
        for button in self.zone_group.buttons():
            if self.zone_group.id(button) == zone_id:
                button.setChecked(True)
                break
        self.current_zone = zone_id

class AdvancedControls(QWidget):
    """Advanced RGB controls"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize advanced controls"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Auto-sync option
        sync_frame = QFrame()
        sync_frame.setObjectName("ColorPickerFrame")
        sync_layout = QVBoxLayout(sync_frame)
        
        sync_title = QLabel("Synchronization")
        sync_title.setObjectName("SubHeaderLabel")
        
        self.auto_apply_cb = QCheckBox("Auto-apply changes")
        self.auto_apply_cb.setChecked(True)
        self.auto_apply_cb.setToolTip("Apply changes immediately without clicking Apply")
        
        self.sync_zones_cb = QCheckBox("Sync all zones")
        self.sync_zones_cb.setToolTip("Apply color changes to all zones simultaneously")
        
        sync_layout.addWidget(sync_title)
        sync_layout.addWidget(self.auto_apply_cb)
        sync_layout.addWidget(self.sync_zones_cb)
        
        # Performance options
        perf_frame = QFrame()
        perf_frame.setObjectName("ColorPickerFrame")
        perf_layout = QVBoxLayout(perf_frame)
        
        perf_title = QLabel("Performance")
        perf_title.setObjectName("SubHeaderLabel")
        
        self.smooth_transitions_cb = QCheckBox("Smooth transitions")
        self.smooth_transitions_cb.setChecked(True)
        self.smooth_transitions_cb.setToolTip("Enable smooth color transitions")
        
        self.reduced_effects_cb = QCheckBox("Reduced effects")
        self.reduced_effects_cb.setToolTip("Reduce animation complexity for better performance")
        
        perf_layout.addWidget(perf_title)
        perf_layout.addWidget(self.smooth_transitions_cb)
        perf_layout.addWidget(self.reduced_effects_cb)
        
        # Reset button
        reset_button = QPushButton("🔄 Reset to Defaults")
        reset_button.setObjectName("SecondaryButton")
        reset_button.clicked.connect(self.reset_to_defaults)
        
        layout.addWidget(sync_frame)
        layout.addWidget(perf_frame)
        layout.addWidget(reset_button)
        layout.addStretch()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.auto_apply_cb.setChecked(True)
        self.sync_zones_cb.setChecked(False)
        self.smooth_transitions_cb.setChecked(True)
        self.reduced_effects_cb.setChecked(False)

class ControlPanelsWidget(QWidget):
    """Main control panels widget combining all controls"""
    
    # Signals
    mode_changed = pyqtSignal(int)
    brightness_changed = pyqtSignal(int)
    speed_changed = pyqtSignal(int)
    direction_changed = pyqtSignal(int)
    zone_changed = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_state = {
            'mode': 3,
            'brightness': 100,
            'speed': 5,
            'direction': 1,
            'zone': 1
        }
        
        self.init_ui()
        self.connect_signals()
        self.update_visibility()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Mode selector
        self.mode_selector = ModeSelector()
        
        # Basic controls frame
        basic_frame = QFrame()
        basic_frame.setObjectName("MainPanel")
        basic_layout = QVBoxLayout(basic_frame)
        basic_layout.setSpacing(12)
        
        # Brightness control
        self.brightness_control = BrightnessControl()
        
        # Speed control (for animated modes)
        self.speed_control = SpeedControl()
        
        # Direction control (for applicable modes)
        self.direction_control = DirectionControl()
        
        # Zone control (for static mode)
        self.zone_control = ZoneControl()
        
        basic_layout.addWidget(self.brightness_control)
        basic_layout.addWidget(self.speed_control)
        basic_layout.addWidget(self.direction_control)
        basic_layout.addWidget(self.zone_control)
        
        # Advanced controls
        self.advanced_controls = AdvancedControls()
        
        # Apply button
        self.apply_button = QPushButton("✨ Apply Changes")
        self.apply_button.setFixedHeight(50)
        self.apply_button.setObjectName("MainButton")
        
        layout.addWidget(self.mode_selector)
        layout.addWidget(basic_frame)
        layout.addWidget(self.advanced_controls)
        layout.addWidget(self.apply_button)
        layout.addStretch()
    
    def connect_signals(self):
        """Connect control signals"""
        self.mode_selector.mode_changed.connect(self.on_mode_changed)
        self.brightness_control.brightness_changed.connect(self.brightness_changed.emit)
        self.speed_control.speed_changed.connect(self.speed_changed.emit)
        self.direction_control.direction_changed.connect(self.direction_changed.emit)
        self.zone_control.zone_changed.connect(self.zone_changed.emit)
        
        # Connect mode change to visibility updates
        self.mode_selector.mode_changed.connect(self.update_visibility)
    
    def on_mode_changed(self, mode_id):
        """Handle mode change"""
        self.current_state['mode'] = mode_id
        self.update_visibility()
        self.mode_changed.emit(mode_id)
    
    def update_visibility(self):
        """Update control visibility based on current mode"""
        mode = self.current_state['mode']
        
        # Speed control visibility (animated modes only)
        animated_modes = [1, 2, 3, 4, 5]  # All except static
        self.speed_control.setVisible(mode in animated_modes)
        
        # Direction control visibility (wave and shifting only)
        direction_modes = [3, 4]  # Wave and Shifting
        self.direction_control.setVisible(mode in direction_modes)
        
        # Zone control visibility (static mode only)
        self.zone_control.setVisible(mode == 0)
    
    def update_from_state(self, state):
        """Update controls from external state"""
        self.current_state.update(state)
        
        # Update individual controls
        self.mode_selector.set_mode(state.get('mode', 3))
        self.brightness_control.set_brightness(state.get('brightness', 100))
        self.speed_control.set_speed(state.get('speed', 5))
        self.direction_control.set_direction(state.get('direction', 1))
        self.zone_control.set_zone(state.get('zone', 1))
        
        # Update visibility
        self.update_visibility()
    
    def get_current_state(self):
        """Get current control state"""
        return {
            'mode': self.mode_selector.current_mode,
            'brightness': self.brightness_control.current_brightness,
            'speed': self.speed_control.current_speed,
            'direction': self.direction_control.current_direction,
            'zone': self.zone_control.current_zone
        }