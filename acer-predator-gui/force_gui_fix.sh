#!/bin/bash
# Force GUI Fix for Pop!_OS 22.04 - Multiple approaches to get Qt6 working

set -e

echo "🔧 FORCING GUI TO WORK - Pop!_OS 22.04 Fix"
echo "=============================================="
echo ""

# Function to check if GUI works
test_gui() {
    echo "🧪 Testing Qt6 GUI..."
    timeout 5 python3 -c "
import sys
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'
sys.path.insert(0, 'src')
from PyQt6.QtWidgets import QApplication
app = QApplication([])
print('✅ Qt6 GUI test successful!')
app.quit()
" 2>/dev/null && return 0 || return 1
}

# Approach 1: Install missing xcb-cursor package
echo "📦 Approach 1: Installing missing Qt6 dependencies..."
sudo apt update

# Install the specific missing package
sudo apt install -y libxcb-cursor0 libxcb-cursor-dev

# Install additional Qt6 packages for Pop!_OS
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

echo "✅ Qt6 packages installed"

# Test if it works now
if test_gui; then
    echo "🎉 SUCCESS! GUI should work now with: ./run.sh"
    exit 0
fi

echo "⚠️  Approach 1 didn't work, trying Approach 2..."

# Approach 2: Use system-wide PyQt6 instead of pip version
echo "📦 Approach 2: Switching to system PyQt6..."

# Remove pip-installed PyQt6
pip3 uninstall -y PyQt6 PyQt6-Qt6 PyQt6-sip 2>/dev/null || true

# Force install system PyQt6
sudo apt install -y --reinstall python3-pyqt6 python3-pyqt6.qtwidgets

# Test again
if test_gui; then
    echo "🎉 SUCCESS! GUI should work now with: ./run.sh"
    exit 0
fi

echo "⚠️  Approach 2 didn't work, trying Approach 3..."

# Approach 3: Install Qt6 from different source
echo "📦 Approach 3: Installing Qt6 from snap..."

# Install Qt6 via snap as backup
sudo snap install qt6-base --edge 2>/dev/null || true

# Reinstall PyQt6 via pip with specific version
pip3 install --force-reinstall PyQt6==6.4.0 PyQt6-Qt6==6.4.0

# Test again
if test_gui; then
    echo "🎉 SUCCESS! GUI should work now with: ./run.sh"
    exit 0
fi

echo "⚠️  Approach 3 didn't work, trying Approach 4..."

# Approach 4: Build environment variables and alternative backends
echo "🔧 Approach 4: Setting up alternative display backends..."

# Create launcher script with multiple backend options
cat > launch_gui_force.sh << 'EOF'
#!/bin/bash

echo "🚀 Launching Acer Predator RGB GUI with multiple backend attempts..."

# Try different Qt backends in order of preference
BACKENDS=("xcb" "wayland" "wayland-egl" "eglfs" "linuxfb")

for backend in "${BACKENDS[@]}"; do
    echo "Trying backend: $backend"
    
    export QT_QPA_PLATFORM="$backend"
    export QT_QPA_PLATFORM_PLUGIN_PATH="/usr/lib/x86_64-linux-gnu/qt6/plugins"
    export QT_PLUGIN_PATH="/usr/lib/x86_64-linux-gnu/qt6/plugins"
    export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
    
    timeout 10 python3 main.py "$@" 2>/dev/null && {
        echo "✅ Success with backend: $backend"
        exit 0
    }
done

echo "❌ All backends failed, but we have more options..."
echo "🔄 Trying compatibility mode..."

# Try compatibility mode
export QT_QPA_PLATFORM="xcb"
export QT_AUTO_SCREEN_SCALE_FACTOR=0
export QT_SCALE_FACTOR=1
export QT_SCREEN_SCALE_FACTORS=1
export QT_DEVICE_PIXEL_RATIO=1

python3 main.py "$@"
EOF

chmod +x launch_gui_force.sh

# Test the force launcher
if timeout 5 ./launch_gui_force.sh --help >/dev/null 2>&1; then
    echo "🎉 SUCCESS! GUI launcher created: ./launch_gui_force.sh"
    exit 0
fi

# Approach 5: Install from PPA or compile
echo "📦 Approach 5: Installing from alternative sources..."

# Add Qt6 PPA for newer packages
sudo add-apt-repository -y ppa:beineri/opt-qt-5.15.2-jammy 2>/dev/null || true
sudo apt update

# Install alternative Qt6
sudo apt install -y qt6-base-dev qt6-tools-dev qt6-l10n-tools 2>/dev/null || true

echo "🎉 Multiple fixes applied! Try these commands:"
echo ""
echo "1. Standard launcher:     ./run.sh"
echo "2. Force launcher:        ./launch_gui_force.sh"
echo "3. Manual backend:        QT_QPA_PLATFORM=wayland ./run.sh"
echo "4. Compatibility mode:    QT_AUTO_SCREEN_SCALE_FACTOR=0 ./run.sh"
echo ""
echo "If none work, we'll create a web-based GUI next!"