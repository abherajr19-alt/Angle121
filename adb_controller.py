import subprocess
import time
import os

class ADBController:
    def __init__(self, host="localhost:5555"):
        self.host = host
        self.connected = False
        
    def connect(self):
        """Connect to ADB device"""
        try:
            # Kill existing server
            subprocess.run(["adb", "kill-server"], 
                         capture_output=True, text=True)
            
            # Start server
            subprocess.run(["adb", "start-server"], 
                         capture_output=True, text=True)
            
            # Connect to device
            result = subprocess.run(
                ["adb", "connect", self.host],
                capture_output=True,
                text=True
            )
            
            if "connected" in result.stdout:
                self.connected = True
                return True
                
            return False
            
        except Exception as e:
            print(f"ADB Connection error: {e}")
            return False
            
    def execute(self, command):
        """Execute ADB command"""
        try:
            result = subprocess.run(
                ["adb", "shell", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except:
            return ""
            
    def tap(self, x, y):
        """Tap at coordinates"""
        self.execute(f"input tap {x} {y}")
        
    def swipe(self, x1, y1, x2, y2, duration=300):
        """Swipe between coordinates"""
        self.execute(f"input swipe {x1} {y1} {x2} {y2} {duration}")
        
    def type_text(self, text):
        """Type text"""
        # Escape special characters
        text = text.replace('"', '\\"')
        text = text.replace("'", "\\'")
        text = text.replace(" ", "%s")
        text = text.replace("&", "\\&")
        
        self.execute(f'input text "{text}"')
        
    def press_key(self, keycode):
        """Press key"""
        # Common keycodes: 3=HOME, 4=BACK, 26=POWER
        self.execute(f"input keyevent {keycode}")
        
    def press_back(self):
        """Press back button"""
        self.press_key(4)
        
    def press_home(self):
        """Press home button"""
        self.press_key(3)
        
    def press_power(self):
        """Press power button"""
        self.press_key(26)
        
    def open_app(self, package_name):
        """Open app by package name"""
        self.execute(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        
    def take_screenshot(self, save_path):
        """Take screenshot"""
        # Save to device
        temp_path = "/sdcard/screenshot.png"
        self.execute(f"screencap -p {temp_path}")
        
        # Pull to computer
        subprocess.run(["adb", "pull", temp_path, save_path], 
                      capture_output=True, text=True)
        
        # Cleanup
        self.execute(f"rm {temp_path}")
        
    def get_notifications(self):
        """Get notifications"""
        output = self.execute("dumpsys notification")
        notifications = []
        
        # Parse notification output
        lines = output.split('\n')
        current_notif = {}
        
        for line in lines:
            line = line.strip()
            if "NotificationRecord" in line:
                if current_notif:
                    notifications.append(current_notif)
                current_notif = {}
            elif "tickerText=" in line:
                current_notif['ticker'] = line.split('=')[1]
            elif "title=" in line:
                current_notif['title'] = line.split('=')[1]
            elif "text=" in line:
                current_notif['text'] = line.split('=')[1]
            elif "package=" in line:
                current_notif['package'] = line.split('=')[1]
                
        if current_notif:
            notifications.append(current_notif)
            
        return notifications
        
    def unlock_screen(self, pin=None):
        """Unlock screen"""
        # Wake up
        self.press_power()
        time.sleep(0.5)
        
        # Swipe to unlock
        self.swipe(500, 1500, 500, 500, 300)
        time.sleep(0.5)
        
        # Enter PIN if provided
        if pin:
            self.type_text(pin)
            time.sleep(0.5)
            self.press_key(66)  # Enter
            
    def lock_screen(self):
        """Lock screen"""
        self.press_power()
        
    def get_screen_state(self):
        """Get screen state"""
        output = self.execute("dumpsys power")
        if "mHoldingDisplaySuspendBlocker=true" in output:
            return "ON"
        else:
            return "OFF"
