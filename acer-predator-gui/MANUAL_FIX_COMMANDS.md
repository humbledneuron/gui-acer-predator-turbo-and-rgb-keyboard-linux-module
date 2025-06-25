# 🔧 Manual Commands to Fix Qt6 GUI

## Step 1: Install Missing Qt6 Dependencies

Run these commands one by one:

```bash
# Update package list
sudo apt update

# Install the specific missing package
sudo apt install -y libxcb-cursor0 libxcb-cursor-dev

# Install comprehensive Qt6 support
sudo apt install -y \
    python3-pyqt6 \
    python3-pyqt6.qtwidgets \
    python3-pyqt6.qtcore \
    python3-pyqt6.qtgui \
    qt6-qpa-plugins \
    libqt6core6 \
    libqt6gui6 \
    libqt6widgets6 \
    qt6-base-dev
```

## Step 2: Test Qt6 Installation

```bash
# Test if Qt6 works now
python3 -c "from PyQt6.QtWidgets import QApplication; app = QApplication([]); print('Qt6 working!'); app.quit()"
```

## Step 3: Try Running the GUI

```bash
# Method 1: Normal launch
./run.sh

# Method 2: Force XCB backend
QT_QPA_PLATFORM=xcb ./run.sh

# Method 3: Try Wayland backend
QT_QPA_PLATFORM=wayland ./run.sh

# Method 4: Compatibility mode
QT_AUTO_SCREEN_SCALE_FACTOR=0 QT_SCALE_FACTOR=1 ./run.sh
```

## Alternative: Use System PyQt6 Instead of Pip

If pip version causes issues:

```bash
# Remove pip-installed PyQt6
pip3 uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip

# Use system PyQt6
sudo apt install -y --reinstall python3-pyqt6

# Try running again
./run.sh
```

## 🌐 IMMEDIATE SOLUTION: Web GUI

While fixing Qt6, you can use the web GUI right now:

```bash
python3 web_gui.py
```

This opens a beautiful web interface in your browser with:
- All RGB modes and controls
- Real-time color picker
- Live keyboard preview  
- Profile management
- Modern responsive design
- Zero dependency issues

## Debug Information

If GUI still doesn't work, collect debug info:

```bash
# Check Qt platform plugins
find /usr -name "*qt*platform*" 2>/dev/null

# Check environment
echo "Display: $DISPLAY"
echo "Session: $XDG_SESSION_TYPE" 
echo "Wayland: $WAYLAND_DISPLAY"

# Test minimal Qt
python3 -c "
import os
os.environ['QT_DEBUG_PLUGINS'] = '1'
from PyQt6.QtWidgets import QApplication
app = QApplication([])
print('Success!')
"
```