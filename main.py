#!/data/data/com.termux/files/usr/bin/python3
"""
नोवा - इंटेलिजेंट पर्सनल असिस्टेंट
फुली ऑटोनोमस, सेल्फ-लर्निंग, एडबी-कंट्रोल्ड
"""

import os
import sys
import json
import time
import threading
import subprocess
import logging
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules
from nova_core import NovaCore
from ai_engine import AIEngine
from adb_controller import ADBController
from notification_monitor import NotificationMonitor
from voice_system import VoiceSystem
from memory_manager import MemoryManager
from evolution_engine import EvolutionEngine

class NovaAssistant:
    def __init__(self):
        # Initialize paths
        self.home_dir = Path.home()
        self.nova_dir = self.home_dir / ".nova"
        self.nova_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.config_file = self.nova_dir / "config.json"
        self.memory_file = self.nova_dir / "abheraj.json"
        self.log_file = self.nova_dir / "nova.log"
        
        # Setup logging
        self.setup_logging()
        
        # Initialize components
        self.log("🚀 नोवा असिस्टेंट शुरू हो रही है...")
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize core systems
        self.memory = MemoryManager(self.memory_file)
        self.adb = ADBController(self.config['adb_host'])
        self.ai = AIEngine(self.config, self.memory)
        self.voice = VoiceSystem(self.config)
        self.notifications = NotificationMonitor(self.adb, self.ai, self.memory)
        self.evolution = EvolutionEngine(self.memory, self.config)
        
        # State variables
        self.is_running = True
        self.is_silent = False
        self.last_command_time = 0
        
        # Threads
        self.threads = []
        
        # Personality
        self.name = "Nova"
        self.personality = {
            "style": "friendly_feminine",
            "language": "hinglish",
            "tone": "caring",
            "humor_level": 0.7
        }
        
    def setup_logging(self):
        """Setup logging system"""
        logging.basicConfig(
            filename=self.log_file,
            level=logging.DEBUG,
            format='%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger('Nova')
        
    def log(self, message, level="INFO"):
        """Log messages"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        if level == "INFO":
            self.logger.info(message)
        elif level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
            
    def load_config(self):
        """Load or create configuration"""
        default_config = {
            "name": "Nova",
            "adb_host": "localhost:5555",
            "auto_reply": True,
            "voice_enabled": True,
            "ai_backend": "huggingchat",  # sambanova, huggingchat, local
            "learning_rate": 0.1,
            "backup_interval": 300,
            "screen_monitoring": True,
            "notification_check_interval": 2,
            "max_memory_entries": 1000,
            "personality": "friendly_secretary"
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                # Update with any new defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
        else:
            config = default_config
            
        # Save config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
            
        return config
        
    def start_background_services(self):
        """Start all background services"""
        self.log("🔄 बैकग्राउंड सर्विसेज शुरू हो रही हैं...")
        
        # 1. ADB Connection
        if not self.adb.connect():
            self.log("❌ ADB कनेक्शन विफल, रिट्राइंग...", "WARNING")
            # Try to start ADB server
            subprocess.run(["adb", "start-server"])
            time.sleep(2)
            self.adb.connect()
            
        # 2. Notification Monitor (24/7)
        notif_thread = threading.Thread(
            target=self.notifications.monitor_continuously,
            daemon=True
        )
        self.threads.append(notif_thread)
        notif_thread.start()
        
        # 3. Screen Monitoring
        if self.config['screen_monitoring']:
            screen_thread = threading.Thread(
                target=self.monitor_screen,
                daemon=True
            )
            self.threads.append(screen_thread)
            screen_thread.start()
            
        # 4. Auto Evolution
        evolution_thread = threading.Thread(
            target=self.evolution.continuous_evolution,
            daemon=True
        )
        self.threads.append(evolution_thread)
        evolution_thread.start()
        
        # 5. Memory Backup
        backup_thread = threading.Thread(
            target=self.memory.auto_backup,
            daemon=True
        )
        self.threads.append(backup_thread)
        backup_thread.start()
        
    def monitor_screen(self):
        """Monitor device screen continuously"""
        self.log("👁️ स्क्रीन मॉनिटरिंग शुरू...")
        
        while self.is_running:
            try:
                # Take screenshot every 5 seconds
                screenshot_path = self.nova_dir / "screen.png"
                self.adb.take_screenshot(str(screenshot_path))
                
                # Analyze screen content
                # This can be extended for OCR, object detection, etc.
                
                time.sleep(5)
                
            except Exception as e:
                self.log(f"स्क्रीन मॉनिटरिंग त्रुटि: {e}", "ERROR")
                time.sleep(10)
                
    def listen_for_voice(self):
        """Listen for voice commands"""
        self.log("🎤 वॉयस लिसनिंग शुरू...")
        
        while self.is_running:
            try:
                # Check if we should be silent
                if self.is_silent:
                    time.sleep(0.1)
                    continue
                    
                # Listen for voice input using Termux API
                result = self.voice.listen()
                
                if result and result.strip():
                    self.process_command(result, source="voice")
                    
            except Exception as e:
                self.log(f"वॉयस लिसनिंग त्रुटि: {e}", "ERROR")
                time.sleep(1)
                
    def process_command(self, command, source="text"):
        """Process user commands"""
        self.log(f"प्रोसेसिंग कमांड: {command}")
        
        # Check if user is speaking (for voice)
        if source == "voice" and self.is_user_speaking():
            self.is_silent = True
            while self.is_user_speaking():
                time.sleep(0.1)
            time.sleep(1)  # Wait 1 second after user stops
            self.is_silent = False
            
        # Analyze command
        response = self.ai.process(
            command=command,
            context=self.memory.get_context(),
            personality=self.personality
        )
        
        # Speak response
        if self.config['voice_enabled'] and source == "voice":
            self.voice.speak(response)
        else:
            self.print_response(response)
            
        # Save to memory
        self.memory.add_conversation(command, response)
        
        # Execute actions if needed
        self.execute_actions(command, response)
        
    def is_user_speaking(self):
        """Detect if user is currently speaking"""
        # This is a simplified version
        # You can implement proper VAD (Voice Activity Detection)
        return False  # Placeholder
        
    def print_response(self, response):
        """Print response in friendly format"""
        print(f"\n{'='*60}")
        print(f"🌟 {self.name}: {response}")
        print(f"{'='*60}\n")
        
    def execute_actions(self, command, response):
        """Execute actions based on command"""
        # Open app
        if "खोलो" in command or "open" in command.lower():
            app_name = self.extract_app_name(command)
            if app_name:
                self.adb.open_app(app_name)
                
        # Send message
        elif "भेजो" in command or "send" in command.lower():
            self.handle_messaging(command)
            
        # Take note
        elif "नोट" in command or "note" in command.lower():
            self.take_note(command)
            
        # Code something
        elif "कोड" in command or "code" in command.lower():
            self.write_code(command)
            
    def extract_app_name(self, command):
        """Extract app name from command"""
        words = command.lower().split()
        for i, word in enumerate(words):
            if word in ["खोलो", "open", "लॉन्च", "launch"]:
                if i + 1 < len(words):
                    return words[i + 1]
        return None
        
    def handle_messaging(self, command):
        """Handle messaging commands"""
        # Extract contact and message
        # This is simplified - you'd need proper NLP
        self.log("📱 मैसेजिंग हैंडल की जा रही है...")
        
    def take_note(self, command):
        """Take note in notes app"""
        note_text = command.replace("नोट", "").replace("note", "").strip()
        
        # Open notes app
        self.adb.open_app("com.google.android.keep")
        time.sleep(1)
        
        # Create new note
        self.adb.tap(100, 100)  # New note button
        time.sleep(0.5)
        
        # Type note
        self.adb.type_text(note_text)
        
        # Save
        self.adb.press_back()
        
        self.log(f"📝 नोट सेव किया गया: {note_text[:50]}...")
        
    def write_code(self, command):
        """Write code in notes app"""
        code_topic = command.replace("कोड", "").replace("code", "").strip()
        
        # Generate code using AI
        code = self.ai.generate_code(code_topic)
        
        # Open notes app
        self.adb.open_app("com.google.android.keep")
        time.sleep(1)
        
        # Create new note
        self.adb.tap(100, 100)
        time.sleep(0.5)
        
        # Type code
        self.adb.type_text(f"# Code for: {code_topic}\n\n{code}")
        
        self.log(f"💻 कोड जेनरेट किया गया: {code_topic}")
        
    def interactive_mode(self):
        """Interactive command line interface"""
        self.print_welcome()
        
        while self.is_running:
            try:
                # Get user input
                user_input = input("\nआप: ").strip()
                
                if not user_input:
                    continue
                    
                # Check for exit command
                if user_input.lower() in ['exit', 'बंद', 'stop', 'quit']:
                    self.shutdown()
                    break
                    
                # Process command
                self.process_command(user_input, source="text")
                
            except KeyboardInterrupt:
                self.log("\n🛑 कीबोर्ड इंटरप्ट प्राप्त हुआ")
                self.shutdown()
                break
            except Exception as e:
                self.log(f"इंटरैक्टिव मोड त्रुटि: {e}", "ERROR")
                
    def print_welcome(self):
        """Print welcome message"""
        print("\n" + "🌟" * 30)
        print("🌟" + " " * 28 + "🌟")
        print("🌟      नोवा पर्सनल असिस्टेंट      🌟")
        print("🌟" + " " * 28 + "🌟")
        print("🌟" * 30)
        print("\nनमस्ते! मैं नोवा हूं, आपकी पर्सनल सेक्रेटरी।")
        print("मुझसे कुछ भी पूछ सकते हैं, मैं हर काम में मदद करूंगी।")
        print("\nकमांड्स:")
        print("- 'नोट [टेक्स्ट]' - नया नोट बनाएं")
        print("- 'कोड [टॉपिक]' - कोड जेनरेट करें")
        print("- 'खोलो [ऐप]' - ऐप ओपन करें")
        print("- 'बंद' - प्रोग्राम बंद करें")
        print("\n" + "-" * 60)
        
    def shutdown(self):
        """Shutdown procedure"""
        self.log("🔴 नोवा बंद हो रही है...")
        self.is_running = False
        
        # Save memory
        self.memory.save()
        
        # Wait for threads
        for thread in self.threads:
            thread.join(timeout=1)
            
        self.log("✅ नोवा सफलतापूर्वक बंद हो गई")
        print("\nधन्यवाद! जल्द मिलते हैं। 👋")
        
    def run(self):
        """Main run method"""
        try:
            # Start background services
            self.start_background_services()
            
            # Start voice listening in background
            voice_thread = threading.Thread(
                target=self.listen_for_voice,
                daemon=True
            )
            self.threads.append(voice_thread)
            voice_thread.start()
            
            # Start interactive mode
            self.interactive_mode()
            
        except Exception as e:
            self.log(f"मुख्य त्रुटि: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            self.shutdown()

def main():
    """Entry point"""
    print("Initializing Nova Assistant...")
    
    # Check if running in Termux
    if not os.path.exists('/data/data/com.termux/files/home'):
        print("⚠️  चेतावनी: यह स्क्रिप्ट Termux के लिए डिज़ाइन की गई है")
        print("इसे Termux में चलाने की सलाह दी जाती है")
        
    # Create assistant instance
    assistant = NovaAssistant()
    
    # Run assistant
    assistant.run()

if __name__ == "__main__":
    main()
