# 🎮 Acer Predator RGB - Web GUI

A modern, browser-based interface for controlling Acer RGB keyboards on Linux systems.

## 🌟 Features

- 🌐 **Web-Based Interface** - Works in any modern browser
- 🎨 **Complete RGB Control** - All 6 modes: Static, Breath, Neon, Wave, Shifting, Zoom
- 🌈 **Real-time Color Picker** - HSV wheel, RGB sliders, and preset colors
- ⚡ **Live Preview** - 4-zone keyboard visualization with real-time updates
- 📁 **Profile Management** - Save, load, and manage custom lighting profiles
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎯 **Zero Dependencies** - No Qt, no complex installations

## 🚀 Quick Start

1. **Install Dependencies** (optional - psutil for system monitoring):
   ```bash
   pip install psutil
   ```

2. **Launch the Web GUI**:
   ```bash
   python3 web_gui.py
   ```

3. **Open Browser**: Automatically opens at `http://localhost:8080`

## 🎨 Interface

The web interface provides:

- **RGB Mode Selection** - 6 visual mode buttons with icons
- **Real-time Controls** - Brightness and speed sliders
- **Color Picker** - Interactive color wheel + preset colors
- **Live Preview** - See RGB effects on virtual keyboard zones
- **Profile Manager** - Save/load favorite configurations
- **Status Monitoring** - Real-time device connection status

## 🔧 API Endpoints

The web GUI provides a REST API:

- `GET /api/status` - Current RGB status and device info
- `GET /api/modes` - Available RGB modes
- `GET /api/profiles` - Saved profiles list
- `POST /api/set_mode` - Apply RGB settings
- `POST /api/save_profile` - Save current profile
- `POST /api/load_profile` - Load saved profile

## 🌈 RGB Modes

1. **Static** 🎯 - Solid colors per zone
2. **Breath** 💨 - Breathing effect
3. **Neon** 🌈 - Rainbow cycling
4. **Wave** 🌊 - Wave animation
5. **Shifting** ↔️ - Color shifting
6. **Zoom** 🔍 - Zoom effect

## 📱 Mobile Support

The interface is fully responsive and works on:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Android Chrome)
- Tablet browsers

## 🔒 Security

- Local-only web server (localhost:8080)
- No external connections required
- No user authentication needed (local access only)

## 🛠️ Troubleshooting

### Port Already in Use
If port 8080 is busy, the server will show an error. Kill any existing processes:
```bash
pkill -f web_gui.py
```

### RGB Device Not Found
Make sure the facer kernel module is loaded:
```bash
sudo modprobe facer
ls -la /dev/acer-gkbbl*
```

### Browser Doesn't Open Automatically
Manually open: `http://localhost:8080`

## 🤝 Contributing

This web-based approach makes the RGB controller:
- More accessible to users
- Easier to develop and maintain
- Platform independent
- Simple to extend with new features

## 📄 License

GNU General Public License v3.0 - Same as the parent project.