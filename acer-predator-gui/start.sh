#!/bin/bash
# Simple launcher for Acer Predator RGB Web GUI

echo "🎮 Starting Acer Predator RGB Web GUI..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if facer_rgb.py exists in parent directory
if [ ! -f "../facer_rgb.py" ]; then
    echo "⚠️  Warning: facer_rgb.py not found in parent directory"
    echo "   RGB control may not work properly"
fi

# Check if RGB device is available
if [ ! -e "/dev/acer-gkbbl-0" ] && [ ! -e "/dev/acer-gkbbl-static-0" ]; then
    echo "⚠️  Warning: RGB keyboard device not found"
    echo "   Make sure the facer kernel module is loaded"
fi

# Launch the web GUI
echo "🚀 Launching web interface..."
echo "📱 Will open at: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 web_gui.py