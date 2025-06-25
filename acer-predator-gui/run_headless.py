#!/usr/bin/env python3
"""
Headless RGB Controller - CLI interface for GUI functionality
Alternative when Qt GUI can't run due to display issues
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from core.rgb_controller import RGBController

class HeadlessRGBController:
    """Command-line interface for RGB control with GUI-like features"""
    
    def __init__(self):
        try:
            self.controller = RGBController()
            print("✅ RGB Controller initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize RGB controller: {e}")
            sys.exit(1)
    
    def show_status(self):
        """Show current RGB status"""
        print("\n" + "="*50)
        print("🎮 ACER PREDATOR RGB STATUS")
        print("="*50)
        
        print(f"Device Available: {'✅ Yes' if self.controller.is_device_available() else '❌ No'}")
        
        state = self.controller.get_current_state()
        mode_info = self.controller.get_mode_by_id(state['mode'])
        mode_name = mode_info.name if mode_info else "Unknown"
        
        print(f"Current Mode: {state['mode']} ({mode_name})")
        print(f"Brightness: {state['brightness']}%")
        print(f"Speed: {state['speed']}")
        print(f"Color: RGB{state['color']}")
        print(f"Direction: {state['direction']}")
        print(f"Zone: {state['zone']}")
    
    def show_modes(self):
        """Show available RGB modes"""
        print("\n" + "="*50)
        print("🌈 AVAILABLE RGB MODES")
        print("="*50)
        
        for mode in self.controller.get_modes():
            supports = []
            if mode.supports_color: supports.append("Color")
            if mode.supports_zone: supports.append("Zone")
            if mode.supports_speed: supports.append("Speed")
            if mode.supports_direction: supports.append("Direction")
            
            print(f"{mode.id}. {mode.name}")
            print(f"   {mode.description}")
            print(f"   Supports: {', '.join(supports) if supports else 'Basic'}")
            print()
    
    def show_profiles(self):
        """Show saved profiles"""
        print("\n" + "="*50)
        print("📁 SAVED PROFILES")
        print("="*50)
        
        profiles = self.controller.list_profiles()
        if not profiles:
            print("No saved profiles found.")
            return
        
        for i, profile in enumerate(profiles, 1):
            print(f"{i}. {profile}")
    
    def set_mode_interactive(self):
        """Interactive mode setting"""
        print("\n" + "="*50)
        print("🎨 SET RGB MODE")
        print("="*50)
        
        # Show modes
        modes = self.controller.get_modes()
        for mode in modes:
            print(f"{mode.id}. {mode.name} - {mode.description}")
        
        try:
            mode_id = int(input("\nSelect mode (0-5): "))
            if mode_id not in range(6):
                print("❌ Invalid mode")
                return
            
            mode_info = self.controller.get_mode_by_id(mode_id)
            
            # Get parameters based on mode
            kwargs = {}
            
            # Brightness (all modes)
            brightness = input(f"Brightness (0-100, current: {self.controller.current_brightness}): ")
            if brightness.strip():
                kwargs['brightness'] = int(brightness)
            
            # Speed (animated modes)
            if mode_info.supports_speed:
                speed = input(f"Speed (1-9, current: {self.controller.current_speed}): ")
                if speed.strip():
                    kwargs['speed'] = int(speed)
            
            # Color (color modes)
            if mode_info.supports_color:
                print("Color (R G B format, e.g., 255 0 0 for red):")
                color_input = input(f"Current: {self.controller.current_color}: ")
                if color_input.strip():
                    r, g, b = map(int, color_input.split())
                    kwargs['color'] = (r, g, b)
            
            # Direction (directional modes)
            if mode_info.supports_direction:
                direction = input("Direction (1=Right to Left, 2=Left to Right): ")
                if direction.strip():
                    kwargs['direction'] = int(direction)
            
            # Zone (static mode)
            if mode_info.supports_zone:
                zone = input("Zone (1-4): ")
                if zone.strip():
                    kwargs['zone'] = int(zone)
            
            # Apply changes
            print("\n🔄 Applying RGB settings...")
            success = self.controller.set_rgb_mode(mode_id, **kwargs)
            
            if success:
                print("✅ RGB settings applied successfully!")
            else:
                print("❌ Failed to apply RGB settings")
        
        except (ValueError, KeyboardInterrupt):
            print("❌ Invalid input or cancelled")
    
    def quick_presets(self):
        """Quick preset colors"""
        print("\n" + "="*50)
        print("⚡ QUICK PRESETS")
        print("="*50)
        
        presets = [
            ("1", "Acer Green Breathing", 1, {"color": (131, 184, 26), "speed": 5, "brightness": 100}),
            ("2", "Gaming Red Wave", 3, {"speed": 7, "brightness": 90}),
            ("3", "Cool Blue Static", 0, {"color": (0, 100, 255), "zone": 1, "brightness": 80}),
            ("4", "Rainbow Neon", 2, {"speed": 6, "brightness": 100}),
            ("5", "Purple Zoom", 5, {"color": (128, 0, 255), "speed": 4, "brightness": 85}),
            ("0", "Turn Off", None, {"brightness": 0})
        ]
        
        for key, name, mode, params in presets:
            print(f"{key}. {name}")
        
        try:
            choice = input("\nSelect preset: ")
            
            for key, name, mode, params in presets:
                if choice == key:
                    print(f"\n🔄 Applying {name}...")
                    
                    if mode is not None:
                        success = self.controller.set_rgb_mode(mode, **params)
                    else:
                        success = self.controller.turn_off()
                    
                    if success:
                        print(f"✅ {name} applied successfully!")
                    else:
                        print(f"❌ Failed to apply {name}")
                    return
            
            print("❌ Invalid selection")
        
        except KeyboardInterrupt:
            print("❌ Cancelled")
    
    def save_profile_interactive(self):
        """Interactive profile saving"""
        print("\n" + "="*50)
        print("💾 SAVE CURRENT PROFILE")
        print("="*50)
        
        try:
            name = input("Profile name: ").strip()
            if not name:
                print("❌ Profile name cannot be empty")
                return
            
            success = self.controller.save_profile(name)
            if success:
                print(f"✅ Profile '{name}' saved successfully!")
            else:
                print(f"❌ Failed to save profile '{name}'")
        
        except KeyboardInterrupt:
            print("❌ Cancelled")
    
    def load_profile_interactive(self):
        """Interactive profile loading"""
        print("\n" + "="*50)
        print("📂 LOAD PROFILE")
        print("="*50)
        
        profiles = self.controller.list_profiles()
        if not profiles:
            print("No saved profiles found.")
            return
        
        for i, profile in enumerate(profiles, 1):
            print(f"{i}. {profile}")
        
        try:
            choice = input("\nSelect profile number: ")
            index = int(choice) - 1
            
            if 0 <= index < len(profiles):
                profile_name = profiles[index]
                print(f"\n🔄 Loading profile '{profile_name}'...")
                
                success = self.controller.load_profile(profile_name)
                if success:
                    print(f"✅ Profile '{profile_name}' loaded successfully!")
                    self.show_status()
                else:
                    print(f"❌ Failed to load profile '{profile_name}'")
            else:
                print("❌ Invalid selection")
        
        except (ValueError, KeyboardInterrupt):
            print("❌ Invalid input or cancelled")
    
    def main_menu(self):
        """Main interactive menu"""
        while True:
            print("\n" + "="*50)
            print("🎮 ACER PREDATOR RGB CONTROLLER")
            print("="*50)
            print("1. Show Status")
            print("2. Show Available Modes")
            print("3. Set RGB Mode")
            print("4. Quick Presets")
            print("5. Show Profiles")
            print("6. Save Current Profile")
            print("7. Load Profile")
            print("0. Exit")
            print()
            
            try:
                choice = input("Select option: ").strip()
                
                if choice == "1":
                    self.show_status()
                elif choice == "2":
                    self.show_modes()
                elif choice == "3":
                    self.set_mode_interactive()
                elif choice == "4":
                    self.quick_presets()
                elif choice == "5":
                    self.show_profiles()
                elif choice == "6":
                    self.save_profile_interactive()
                elif choice == "7":
                    self.load_profile_interactive()
                elif choice == "0":
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid option")
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break

def main():
    """Main entry point"""
    print("🎮 Acer Predator RGB - Headless Controller")
    print("This is an alternative CLI interface when the GUI can't run")
    print()
    
    try:
        controller = HeadlessRGBController()
        controller.main_menu()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())