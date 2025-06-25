#!/bin/bash
# Acer Predator RGB GUI - Launch Script

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set environment variables
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# Change to the application directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required dependencies are installed
echo "Checking dependencies..."
python3 -c "import PyQt6; import psutil" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing missing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        echo "Please install manually: pip3 install PyQt6 psutil"
        exit 1
    fi
fi

# Check if facer_rgb.py exists in parent directory
if [ ! -f "../facer_rgb.py" ]; then
    echo "Warning: facer_rgb.py not found in parent directory"
    echo "RGB control may not work properly"
fi

# Check if RGB device is available
if [ ! -e "/dev/acer-gkbbl-0" ] && [ ! -e "/dev/acer-gkbbl-static-0" ]; then
    echo "Warning: RGB keyboard device not found"
    echo "Make sure the facer kernel module is loaded"
fi

# Launch the application
echo "Starting Acer Predator RGB GUI..."
python3 main.py "$@"