# Installation Guide - Acer Predator RGB GUI

## Quick Start

1. **Install Dependencies**
   ```bash
   cd acer-predator-gui
   pip install -r requirements.txt
   ```

2. **Launch the Application**
   ```bash
   ./run.sh
   ```
   
   Or manually:
   ```bash
   python3 main.py
   ```

## Detailed Installation

### Prerequisites

- **Python 3.8+** - Required for PyQt6 compatibility
- **Linux system** with Acer RGB keyboard support
- **Acer kernel module (facer)** - Must be installed and loaded
- **PyQt6** - For the GUI framework
- **psutil** - For system monitoring

### Step 1: Install Python Dependencies

#### Using pip (Recommended)
```bash
pip install PyQt6 psutil
```

#### Using package manager

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-pyqt6 python3-psutil
```

**Arch Linux:**
```bash
sudo pacman -S python-pyqt6 python-psutil
```

**Fedora:**
```bash
sudo dnf install python3-PyQt6 python3-psutil
```

### Step 2: Verify Kernel Module

Make sure the facer kernel module is installed and loaded:

```bash
# Check if module is loaded
lsmod | grep facer

# Check if devices are available
ls -la /dev/acer-gkbbl*

# If not loaded, load it manually
sudo modprobe facer
```

### Step 3: Download and Setup GUI

```bash
cd /path/to/acer-predator-turbo-and-rgb-keyboard-linux-module
cd acer-predator-gui

# Make run script executable
chmod +x run.sh

# Test the application
./run.sh
```

## Usage

### Basic Usage

1. **Launch the GUI**
   ```bash
   ./run.sh
   ```

2. **Select RGB Mode** - Choose from Static, Breath, Neon, Wave, Shifting, or Zoom

3. **Adjust Settings** - Use sliders for brightness, speed, and other parameters

4. **Pick Colors** - Use the color picker or preset colors

5. **Save Profiles** - Save your favorite settings for quick access

### Command Line Options

```bash
python3 main.py [OPTIONS]

Options:
  --no-tray          Disable system tray integration
  --debug            Enable debug output  
  --profile NAME     Load specific profile on startup
  --facer-rgb-path   Specify custom path to facer_rgb.py
  --minimized        Start minimized to system tray
  -h, --help         Show help message
```

### Examples

```bash
# Start with debug output
./run.sh --debug

# Start minimized to system tray
./run.sh --minimized

# Load a specific profile
./run.sh --profile "Gaming Red"

# Use custom facer_rgb.py location
./run.sh --facer-rgb-path /custom/path/facer_rgb.py
```

## Troubleshooting

### Common Issues

**1. "PyQt6 not found" Error**
```bash
# Install PyQt6
pip install PyQt6
# Or use system package manager
sudo apt install python3-pyqt6
```

**2. "RGB device not found" Warning**
```bash
# Check if kernel module is loaded
sudo modprobe facer
# Verify device files exist
ls -la /dev/acer-gkbbl*
```

**3. "facer_rgb.py not found" Warning**
```bash
# Make sure facer_rgb.py is in parent directory
ls -la ../facer_rgb.py
# Or specify custom path
./run.sh --facer-rgb-path /path/to/facer_rgb.py
```

**4. Permission Denied Errors**
```bash
# Add user to necessary groups
sudo usermod -a -G dialout $USER
# Logout and login again
```

**5. Application Won't Start**
```bash
# Check Python version
python3 --version
# Should be 3.8 or higher

# Check dependencies
python3 -c "import PyQt6; print('PyQt6 OK')"
python3 -c "import psutil; print('psutil OK')"
```

### Debug Mode

Enable debug mode for detailed output:

```bash
./run.sh --debug
```

This will show:
- Dependency check results
- Device detection status
- facer_rgb.py location
- Qt debug information
- Error details

### Log Files

Application logs are stored in:
- **Linux**: `~/.config/predator/logs/`
- **Profile data**: `~/.config/predator/saved profiles/`

## Advanced Setup

### Desktop Integration

Create a desktop entry for easy access:

```bash
cat > ~/.local/share/applications/acer-predator-rgb.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Acer Predator RGB
Comment=Control Acer RGB Keyboard
Exec=/path/to/acer-predator-gui/run.sh
Icon=/path/to/acer-predator-gui/assets/icons/app_icon.png
Terminal=false
Categories=System;Settings;
Keywords=RGB;Keyboard;Acer;Predator;
StartupNotify=true
EOF
```

### Auto-start Setup

To start the GUI automatically at login:

```bash
cat > ~/.config/autostart/acer-predator-rgb.desktop << EOF
[Desktop Entry]
Type=Application
Name=Acer Predator RGB
Exec=/path/to/acer-predator-gui/run.sh --minimized
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
```

### System-wide Installation

For system-wide installation:

```bash
# Copy to system location
sudo cp -r acer-predator-gui /opt/
sudo chown -R root:root /opt/acer-predator-gui

# Create system launcher
sudo ln -s /opt/acer-predator-gui/run.sh /usr/local/bin/acer-predator-rgb

# Now you can run from anywhere
acer-predator-rgb
```

## Uninstallation

To completely remove the GUI:

```bash
# Remove application files
rm -rf acer-predator-gui

# Remove configuration and profiles
rm -rf ~/.config/predator

# Remove desktop integration
rm -f ~/.local/share/applications/acer-predator-rgb.desktop
rm -f ~/.config/autostart/acer-predator-rgb.desktop

# Remove system-wide installation (if applicable)
sudo rm -rf /opt/acer-predator-gui
sudo rm -f /usr/local/bin/acer-predator-rgb
```

## Support

For issues and support:

1. **Check logs** in `~/.config/predator/logs/`
2. **Run in debug mode** with `--debug` flag
3. **Report issues** on the GitHub repository
4. **Check compatibility** with your specific Acer model

## Next Steps

After installation, consider:

1. **Creating custom profiles** for different scenarios
2. **Setting up auto-start** for convenience
3. **Exploring advanced features** like ambient mode (coming soon)
4. **Contributing** to the project with feedback and suggestions