#!/bin/bash
# Fix Qt dependencies for Acer Predator RGB GUI

echo "🔧 Fixing Qt dependencies for Acer Predator RGB GUI..."
echo ""

# Check if running on Pop!_OS/Ubuntu
if command -v apt &> /dev/null; then
    echo "📦 Installing required packages..."
    
    # Install Qt6 dependencies
    sudo apt update
    sudo apt install -y \
        libxcb-cursor0 \
        libxcb-cursor-dev \
        python3-pyqt6 \
        python3-pyqt6.qtwidgets \
        python3-pyqt6.qtcore \
        python3-pyqt6.qtgui \
        libqt6core6 \
        libqt6gui6 \
        libqt6widgets6 \
        qt6-qpa-plugins
    
    echo "✅ Packages installed successfully!"
    
elif command -v pacman &> /dev/null; then
    echo "📦 Installing Arch Linux packages..."
    sudo pacman -S python-pyqt6 qt6-base
    
elif command -v dnf &> /dev/null; then
    echo "📦 Installing Fedora packages..."
    sudo dnf install python3-PyQt6 qt6-qtbase
    
else
    echo "❌ Unsupported package manager. Please install manually:"
    echo "   - PyQt6"
    echo "   - libxcb-cursor0"
    echo "   - Qt6 base packages"
    exit 1
fi

echo ""
echo "🧪 Testing Qt installation..."

# Test Qt
python3 -c "
import sys
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication([])
    print('✅ PyQt6 working correctly')
    app.quit()
except Exception as e:
    print(f'❌ PyQt6 error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "🎉 Dependencies fixed! You can now run: ./run.sh"
else
    echo "❌ Still having issues. Try the alternative solutions below:"
    echo ""
    echo "🔄 Alternative 1 - Use Wayland:"
    echo "   export QT_QPA_PLATFORM=wayland"
    echo "   ./run.sh"
    echo ""
    echo "🔄 Alternative 2 - Use virtual display:"
    echo "   export QT_QPA_PLATFORM=offscreen"
    echo "   python3 demo_gui.py"
    echo ""
    echo "🔄 Alternative 3 - Install via pip:"
    echo "   pip3 uninstall PyQt6"
    echo "   pip3 install PyQt6==6.4.0"
fi