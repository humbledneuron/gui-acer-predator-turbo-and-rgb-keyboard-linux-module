#!/usr/bin/env python3
"""
Web-based GUI for Acer Predator RGB - Alternative when Qt fails
Modern web interface that works on any browser
"""

import sys
import os
import json
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import socketserver

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from core.rgb_controller import RGBController

class RGBWebHandler(SimpleHTTPRequestHandler):
    """Web server handler for RGB control"""
    
    def __init__(self, *args, rgb_controller=None, **kwargs):
        self.rgb_controller = rgb_controller
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_main_page()
        elif parsed_path.path == '/api/status':
            self.serve_status()
        elif parsed_path.path == '/api/modes':
            self.serve_modes()
        elif parsed_path.path == '/api/profiles':
            self.serve_profiles()
        elif parsed_path.path.startswith('/api/'):
            self.serve_api(parsed_path)
        else:
            super().do_GET()
    
    def do_POST(self):
        """Handle POST requests for RGB control"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/set_mode':
            self.handle_set_mode()
        elif parsed_path.path == '/api/save_profile':
            self.handle_save_profile()
        elif parsed_path.path == '/api/load_profile':
            self.handle_load_profile()
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve the main web GUI"""
        html_content = self.generate_html()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_status(self):
        """Serve current RGB status as JSON"""
        try:
            status = {
                'connected': self.rgb_controller.is_device_available(),
                'state': self.rgb_controller.get_current_state()
            }
            self.send_json(status)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def serve_modes(self):
        """Serve available RGB modes"""
        try:
            modes = []
            for mode in self.rgb_controller.get_modes():
                modes.append({
                    'id': mode.id,
                    'name': mode.name,
                    'description': mode.description,
                    'supports_color': mode.supports_color,
                    'supports_zone': mode.supports_zone,
                    'supports_speed': mode.supports_speed,
                    'supports_direction': mode.supports_direction
                })
            self.send_json(modes)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def serve_profiles(self):
        """Serve saved profiles"""
        try:
            profiles = self.rgb_controller.list_profiles()
            self.send_json(profiles)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_set_mode(self):
        """Handle RGB mode setting"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            mode = data.get('mode', 3)
            kwargs = {}
            
            if 'brightness' in data:
                kwargs['brightness'] = data['brightness']
            if 'speed' in data:
                kwargs['speed'] = data['speed']
            if 'color' in data:
                kwargs['color'] = tuple(data['color'])
            if 'direction' in data:
                kwargs['direction'] = data['direction']
            if 'zone' in data:
                kwargs['zone'] = data['zone']
            
            success = self.rgb_controller.set_rgb_mode(mode, **kwargs)
            self.send_json({'success': success})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_save_profile(self):
        """Handle profile saving"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            name = data.get('name', 'New Profile')
            success = self.rgb_controller.save_profile(name)
            self.send_json({'success': success})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_load_profile(self):
        """Handle profile loading"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            name = data.get('name')
            success = self.rgb_controller.load_profile(name)
            self.send_json({'success': success})
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def generate_html(self):
        """Generate the web GUI HTML"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Acer Predator RGB Control</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%);
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            background: #2c3e50;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #83B81A;
        }
        
        .header h1 {
            color: #83B81A;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            color: #b0b0b0;
            font-size: 1.1em;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .panel {
            background: #2d2d2d;
            border: 1px solid #404040;
            border-radius: 12px;
            padding: 20px;
        }
        
        .panel h2 {
            color: #83B81A;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .mode-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .mode-btn {
            background: #404040;
            color: white;
            border: 2px solid #505050;
            border-radius: 8px;
            padding: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 14px;
        }
        
        .mode-btn:hover {
            border-color: #83B81A;
            background: #505050;
        }
        
        .mode-btn.active {
            background: #83B81A;
            border-color: #96D61F;
        }
        
        .slider-group {
            margin-bottom: 15px;
        }
        
        .slider-group label {
            display: block;
            margin-bottom: 5px;
            color: #b0b0b0;
        }
        
        .slider {
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: #404040;
            outline: none;
            margin-bottom: 5px;
        }
        
        .slider::-webkit-slider-thumb {
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #83B81A;
            cursor: pointer;
        }
        
        .color-picker {
            width: 100%;
            height: 40px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        
        .preset-colors {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
            margin-top: 10px;
        }
        
        .preset-color {
            width: 40px;
            height: 40px;
            border: 2px solid #404040;
            border-radius: 8px;
            cursor: pointer;
            transition: border-color 0.3s ease;
        }
        
        .preset-color:hover {
            border-color: #83B81A;
        }
        
        .keyboard-preview {
            background: #1a1a1a;
            border: 2px solid #404040;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 150px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .keyboard-zones {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            width: 100%;
            max-width: 400px;
        }
        
        .keyboard-zone {
            height: 60px;
            border-radius: 8px;
            border: 1px solid #404040;
            background: #83B81A;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        
        .status-bar {
            background: #2c3e50;
            padding: 10px 20px;
            border-radius: 8px;
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #83B81A;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .btn {
            background: #83B81A;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            cursor: pointer;
            transition: background 0.3s ease;
            font-size: 14px;
        }
        
        .btn:hover {
            background: #96D61F;
        }
        
        .btn-secondary {
            background: #404040;
        }
        
        .btn-secondary:hover {
            background: #505050;
        }
        
        .direction-btn.active, .zone-btn.active {
            background: #83B81A !important;
            color: white;
        }
        
        .zone-btn {
            font-size: 12px;
            padding: 8px;
            min-height: 35px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .mode-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎮 Acer Predator RGB Control</h1>
            <p>Modern Web Interface - Works in Any Browser!</p>
        </header>
        
        <div class="main-content">
            <div class="panel">
                <h2>🌈 RGB Modes</h2>
                <div class="mode-grid" id="modeGrid">
                    <!-- Modes will be loaded here -->
                </div>
                
                <div class="slider-group">
                    <label>💡 Brightness: <span id="brightnessValue">100</span>%</label>
                    <input type="range" class="slider" id="brightnessSlider" min="0" max="100" value="100">
                </div>
                
                <div class="slider-group" id="speedGroup">
                    <label>⚡ Speed: <span id="speedValue">5</span></label>
                    <input type="range" class="slider" id="speedSlider" min="1" max="9" value="5">
                </div>
                
                <div class="slider-group" id="directionGroup" style="display: none;">
                    <label>↔️ Direction</label>
                    <div style="display: flex; gap: 10px; margin-top: 5px;">
                        <button class="btn btn-secondary direction-btn" data-direction="1" style="flex: 1;">→ Right to Left</button>
                        <button class="btn btn-secondary direction-btn" data-direction="2" style="flex: 1;">← Left to Right</button>
                    </div>
                </div>
                
                <div class="slider-group" id="zoneGroup" style="display: none;">
                    <label>🎯 Zone Selection</label>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 5px;">
                        <button class="btn btn-secondary zone-btn" data-zone="1">Zone 1</button>
                        <button class="btn btn-secondary zone-btn" data-zone="2">Zone 2</button>
                        <button class="btn btn-secondary zone-btn" data-zone="3">Zone 3</button>
                        <button class="btn btn-secondary zone-btn" data-zone="4">Zone 4</button>
                    </div>
                    <button class="btn" onclick="applyToAllZones()" style="width: 100%; margin-top: 8px;">🌈 Apply to All Zones</button>
                </div>

                <div class="slider-group" id="colorGroup">
                    <label>🎨 Color</label>
                    <input type="color" class="color-picker" id="colorPicker" value="#32ff32">
                    
                    <div class="preset-colors">
                        <div class="preset-color" style="background: #83B81A" data-color="#83B81A" title="Acer Green"></div>
                        <div class="preset-color" style="background: #ff0000" data-color="#ff0000" title="Red"></div>
                        <div class="preset-color" style="background: #00ff00" data-color="#00ff00" title="Green"></div>
                        <div class="preset-color" style="background: #0000ff" data-color="#0000ff" title="Blue"></div>
                        <div class="preset-color" style="background: #ffff00" data-color="#ffff00" title="Yellow"></div>
                        <div class="preset-color" style="background: #ff00ff" data-color="#ff00ff" title="Magenta"></div>
                        <div class="preset-color" style="background: #00ffff" data-color="#00ffff" title="Cyan"></div>
                        <div class="preset-color" style="background: #ffffff" data-color="#ffffff" title="White"></div>
                    </div>
                </div>
                
                <div class="slider-group">
                    <label>⚡ Quick Presets</label>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-top: 5px;">
                        <button class="btn" onclick="applyPreset('acer_green')">🟢 Acer Green</button>
                        <button class="btn" onclick="applyPreset('gaming_red')">🔴 Gaming Red</button>
                        <button class="btn" onclick="applyPreset('cool_blue')">🔵 Cool Blue</button>
                        <button class="btn" onclick="applyPreset('rainbow')">🌈 Rainbow</button>
                        <button class="btn" onclick="applyPreset('purple_zoom')">🟣 Purple Zoom</button>
                        <button class="btn btn-secondary" onclick="applyPreset('turn_off')">⚫ Turn Off</button>
                    </div>
                </div>
            </div>
            
            <div class="panel">
                <h2>⚡ Live Preview</h2>
                <div class="keyboard-preview">
                    <div class="keyboard-zones">
                        <div class="keyboard-zone" id="zone1">Zone 1</div>
                        <div class="keyboard-zone" id="zone2">Zone 2</div>
                        <div class="keyboard-zone" id="zone3">Zone 3</div>
                        <div class="keyboard-zone" id="zone4">Zone 4</div>
                    </div>
                </div>
                
                <h2>📁 Profiles</h2>
                <div style="margin-bottom: 10px;">
                    <input type="text" id="profileName" placeholder="Profile name..." style="padding: 8px; border-radius: 4px; border: 1px solid #404040; background: #2d2d2d; color: white; margin-right: 10px;">
                    <button class="btn" onclick="saveProfile()">💾 Save</button>
                </div>
                
                <div id="profilesList">
                    <!-- Profiles will be loaded here -->
                </div>
            </div>
        </div>
        
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot" id="statusDot"></div>
                <span id="statusText">Connected</span>
            </div>
            <div>
                <span id="currentMode">Wave Mode</span> • 
                <span id="currentBrightness">100%</span>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 3;
        let rgbModes = [];
        let currentDirection = 1;
        let currentZone = 1;
        
        // Initialize the web interface
        async function init() {
            await loadModes();
            await loadProfiles();
            await updateStatus();
            setupEventListeners();
            
            // Update status periodically
            setInterval(updateStatus, 5000);
        }
        
        async function loadModes() {
            try {
                const response = await fetch('/api/modes');
                rgbModes = await response.json();
                
                const modeGrid = document.getElementById('modeGrid');
                modeGrid.innerHTML = '';
                
                rgbModes.forEach(mode => {
                    const btn = document.createElement('button');
                    btn.className = 'mode-btn';
                    btn.innerHTML = `${getModeIcon(mode.id)} ${mode.name}`;
                    btn.title = mode.description;
                    btn.onclick = () => selectMode(mode.id);
                    
                    if (mode.id === currentMode) {
                        btn.classList.add('active');
                    }
                    
                    modeGrid.appendChild(btn);
                });
            } catch (error) {
                console.error('Failed to load modes:', error);
            }
        }
        
        function getModeIcon(modeId) {
            const icons = ['🎯', '💨', '🌈', '🌊', '↔️', '🔍'];
            return icons[modeId] || '🎨';
        }
        
        async function loadProfiles() {
            try {
                const response = await fetch('/api/profiles');
                const profiles = await response.json();
                
                const profilesList = document.getElementById('profilesList');
                profilesList.innerHTML = '';
                
                profiles.forEach(profile => {
                    const profileBtn = document.createElement('button');
                    profileBtn.className = 'btn btn-secondary';
                    profileBtn.style.marginRight = '5px';
                    profileBtn.style.marginBottom = '5px';
                    profileBtn.innerHTML = `📁 ${profile}`;
                    profileBtn.onclick = () => loadProfile(profile);
                    profilesList.appendChild(profileBtn);
                });
            } catch (error) {
                console.error('Failed to load profiles:', error);
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                const statusDot = document.getElementById('statusDot');
                const statusText = document.getElementById('statusText');
                
                if (status.connected) {
                    statusDot.style.background = '#83B81A';
                    statusText.textContent = 'Connected';
                } else {
                    statusDot.style.background = '#ff4444';
                    statusText.textContent = 'Disconnected';
                }
                
                // Update current state display
                const mode = rgbModes.find(m => m.id === status.state.mode);
                if (mode) {
                    document.getElementById('currentMode').textContent = `${mode.name} Mode`;
                }
                document.getElementById('currentBrightness').textContent = `${status.state.brightness}%`;
                
                // Update sliders
                document.getElementById('brightnessSlider').value = status.state.brightness;
                document.getElementById('brightnessValue').textContent = status.state.brightness;
                document.getElementById('speedSlider').value = status.state.speed;
                document.getElementById('speedValue').textContent = status.state.speed;
                
                // Update color
                const [r, g, b] = status.state.color;
                const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
                document.getElementById('colorPicker').value = hexColor;
                
                // Update preview
                updatePreview(status.state);
                
            } catch (error) {
                console.error('Failed to update status:', error);
            }
        }
        
        function updatePreview(state) {
            const [r, g, b] = state.color;
            const brightness = state.brightness / 100;
            
            const adjustedR = Math.floor(r * brightness);
            const adjustedG = Math.floor(g * brightness);
            const adjustedB = Math.floor(b * brightness);
            
            const color = `rgb(${adjustedR}, ${adjustedG}, ${adjustedB})`;
            
            // Update zones based on mode
            if (state.mode === 0) {
                // Static mode - only update selected zone
                for (let i = 1; i <= 4; i++) {
                    const zone = document.getElementById(`zone${i}`);
                    if (i === state.zone) {
                        zone.style.background = color;
                    } else {
                        // Keep other zones dimmed or in previous color
                        zone.style.background = '#404040';
                    }
                }
            } else {
                // Other modes - update all zones
                for (let i = 1; i <= 4; i++) {
                    const zone = document.getElementById(`zone${i}`);
                    zone.style.background = color;
                }
            }
        }
        
        function setupEventListeners() {
            // Brightness slider
            document.getElementById('brightnessSlider').addEventListener('input', (e) => {
                document.getElementById('brightnessValue').textContent = e.target.value;
                applySettings();
            });
            
            // Speed slider
            document.getElementById('speedSlider').addEventListener('input', (e) => {
                document.getElementById('speedValue').textContent = e.target.value;
                applySettings();
            });
            
            // Color picker
            document.getElementById('colorPicker').addEventListener('input', applySettings);
            
            // Preset colors
            document.querySelectorAll('.preset-color').forEach(preset => {
                preset.addEventListener('click', (e) => {
                    const color = e.target.dataset.color;
                    document.getElementById('colorPicker').value = color;
                    applySettings();
                });
            });
            
            // Direction buttons
            document.querySelectorAll('.direction-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.direction-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    currentDirection = parseInt(e.target.dataset.direction);
                    applySettings();
                });
            });
            
            // Zone buttons
            document.querySelectorAll('.zone-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.zone-btn').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    currentZone = parseInt(e.target.dataset.zone);
                    applySettings();
                });
            });
            
            // Set default active states
            document.querySelector('.direction-btn[data-direction="1"]').classList.add('active');
            document.querySelector('.zone-btn[data-zone="1"]').classList.add('active');
        }
        
        function selectMode(modeId) {
            currentMode = modeId;
            
            // Update UI
            document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Show/hide controls based on mode
            const mode = rgbModes.find(m => m.id === modeId);
            
            // Speed control (all animated modes)
            document.getElementById('speedGroup').style.display = mode.supports_speed ? 'block' : 'none';
            
            // Color control (modes that accept color)
            document.getElementById('colorGroup').style.display = mode.supports_color ? 'block' : 'none';
            
            // Direction control (Wave and Shifting modes)
            document.getElementById('directionGroup').style.display = (modeId === 3 || modeId === 4) ? 'block' : 'none';
            
            // Zone control (Static mode only)
            document.getElementById('zoneGroup').style.display = (modeId === 0) ? 'block' : 'none';
            
            applySettings();
        }
        
        async function applySettings() {
            const brightness = parseInt(document.getElementById('brightnessSlider').value);
            const speed = parseInt(document.getElementById('speedSlider').value);
            const colorHex = document.getElementById('colorPicker').value;
            
            // Convert hex to RGB
            const r = parseInt(colorHex.substr(1, 2), 16);
            const g = parseInt(colorHex.substr(3, 2), 16);
            const b = parseInt(colorHex.substr(5, 2), 16);
            
            const data = {
                mode: currentMode,
                brightness: brightness,
                speed: speed,
                color: [r, g, b],
                direction: currentDirection,
                zone: currentZone
            };
            
            try {
                const response = await fetch('/api/set_mode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                if (result.success) {
                    // Update preview immediately
                    updatePreview({ color: [r, g, b], brightness: brightness });
                }
            } catch (error) {
                console.error('Failed to apply settings:', error);
            }
        }
        
        async function saveProfile() {
            const name = document.getElementById('profileName').value.trim();
            if (!name) {
                alert('Please enter a profile name');
                return;
            }
            
            try {
                const response = await fetch('/api/save_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name })
                });
                
                const result = await response.json();
                if (result.success) {
                    document.getElementById('profileName').value = '';
                    await loadProfiles();
                    alert(`Profile "${name}" saved!`);
                } else {
                    alert('Failed to save profile');
                }
            } catch (error) {
                console.error('Failed to save profile:', error);
            }
        }
        
        async function loadProfile(name) {
            try {
                const response = await fetch('/api/load_profile', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: name })
                });
                
                const result = await response.json();
                if (result.success) {
                    await updateStatus();
                    alert(`Profile "${name}" loaded!`);
                } else {
                    alert('Failed to load profile');
                }
            } catch (error) {
                console.error('Failed to load profile:', error);
            }
        }
        
        async function applyPreset(presetName) {
            const presets = {
                'acer_green': { mode: 1, color: [131, 184, 26], speed: 5, brightness: 100 },
                'gaming_red': { mode: 3, color: [255, 0, 0], speed: 7, brightness: 90 },
                'cool_blue': { mode: 0, color: [0, 100, 255], zone: 1, brightness: 80 },
                'rainbow': { mode: 2, speed: 6, brightness: 100 },
                'purple_zoom': { mode: 5, color: [128, 0, 255], speed: 4, brightness: 85 },
                'turn_off': { brightness: 0 }
            };
            
            const preset = presets[presetName];
            if (!preset) return;
            
            try {
                // Apply the preset
                if (presetName === 'turn_off') {
                    // Just turn off brightness
                    const response = await fetch('/api/set_mode', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ mode: currentMode, brightness: 0 })
                    });
                } else {
                    // Apply full preset
                    const data = {
                        mode: preset.mode,
                        brightness: preset.brightness,
                        speed: preset.speed || 5,
                        color: preset.color || [255, 255, 255],
                        direction: currentDirection,
                        zone: preset.zone || currentZone
                    };
                    
                    const response = await fetch('/api/set_mode', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    
                    // Update UI to reflect preset
                    if (preset.mode !== undefined) {
                        currentMode = preset.mode;
                        document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
                        document.querySelector(`[onclick*="selectMode(${preset.mode})"]`).classList.add('active');
                        
                        // Update control visibility
                        const mode = rgbModes.find(m => m.id === preset.mode);
                        document.getElementById('speedGroup').style.display = mode?.supports_speed ? 'block' : 'none';
                        document.getElementById('colorGroup').style.display = mode?.supports_color ? 'block' : 'none';
                        document.getElementById('directionGroup').style.display = (preset.mode === 3 || preset.mode === 4) ? 'block' : 'none';
                        document.getElementById('zoneGroup').style.display = (preset.mode === 0) ? 'block' : 'none';
                    }
                    
                    if (preset.color) {
                        const [r, g, b] = preset.color;
                        const hexColor = `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
                        document.getElementById('colorPicker').value = hexColor;
                    }
                    
                    if (preset.brightness !== undefined) {
                        document.getElementById('brightnessSlider').value = preset.brightness;
                        document.getElementById('brightnessValue').textContent = preset.brightness;
                    }
                    
                    if (preset.speed !== undefined) {
                        document.getElementById('speedSlider').value = preset.speed;
                        document.getElementById('speedValue').textContent = preset.speed;
                    }
                }
                
                // Show success message
                const presetNames = {
                    'acer_green': 'Acer Green Breathing',
                    'gaming_red': 'Gaming Red Wave',
                    'cool_blue': 'Cool Blue Static',
                    'rainbow': 'Rainbow Neon',
                    'purple_zoom': 'Purple Zoom',
                    'turn_off': 'Turn Off'
                };
                
                console.log(`Applied preset: ${presetNames[presetName]}`);
                
            } catch (error) {
                console.error('Failed to apply preset:', error);
            }
        }
        
        async function applyToAllZones() {
            if (currentMode !== 0) return; // Only works in static mode
            
            const brightness = parseInt(document.getElementById('brightnessSlider').value);
            const colorHex = document.getElementById('colorPicker').value;
            
            // Convert hex to RGB
            const r = parseInt(colorHex.substr(1, 2), 16);
            const g = parseInt(colorHex.substr(3, 2), 16);
            const b = parseInt(colorHex.substr(5, 2), 16);
            
            // Apply to all zones
            for (let zone = 1; zone <= 4; zone++) {
                const data = {
                    mode: 0,
                    brightness: brightness,
                    color: [r, g, b],
                    zone: zone
                };
                
                try {
                    await fetch('/api/set_mode', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                } catch (error) {
                    console.error(`Failed to apply to zone ${zone}:`, error);
                }
            }
            
            console.log('Applied color to all zones');
        }
        
        // Initialize when page loads
        window.addEventListener('load', init);
    </script>
</body>
</html>'''

def create_handler_class(rgb_controller):
    """Create handler class with RGB controller"""
    class Handler(RGBWebHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, rgb_controller=rgb_controller, **kwargs)
    return Handler

def main():
    """Main entry point for web GUI"""
    print("🌐 Starting Acer Predator RGB Web GUI...")
    print("=" * 50)
    
    try:
        # Initialize RGB controller
        rgb_controller = RGBController()
        print("✅ RGB Controller initialized")
        
        # Create web server
        PORT = 8080
        Handler = create_handler_class(rgb_controller)
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"🚀 Web GUI running at: http://localhost:{PORT}")
            print(f"📱 Also accessible at: http://127.0.0.1:{PORT}")
            print("")
            print("Features:")
            print("  ✅ All 6 RGB modes (Static, Breath, Neon, Wave, Shifting, Zoom)")
            print("  ✅ Real-time color picker and sliders")
            print("  ✅ Live 4-zone keyboard preview")
            print("  ✅ Profile management (save/load)")
            print("  ✅ Responsive design for mobile/desktop")
            print("  ✅ Works in any modern browser")
            print("")
            print("🔄 Opening browser automatically...")
            
            # Open browser automatically
            threading.Timer(1.0, lambda: webbrowser.open(f'http://localhost:{PORT}')).start()
            
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n👋 Web GUI stopped")
    except Exception as e:
        print(f"❌ Error starting web GUI: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())