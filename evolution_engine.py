import json
import time
from datetime import datetime
import random

class EvolutionEngine:
    def __init__(self, memory, config):
        self.memory = memory
        self.config = config
        self.evolution_rate = config.get('learning_rate', 0.1)
        
    def continuous_evolution(self):
        """Continuous evolution in background"""
        print("🧬 इवोल्यूशन इंजन शुरू...")
        
        while True:
            try:
                # Analyze and evolve every hour
                time.sleep(3600)
                self.evolve()
                
            except Exception as e:
                print(f"Evolution error: {e}")
                time.sleep(300)
                
    def evolve(self):
        """Evolve the system"""
        print("🔄 सिस्टम इवोल्व हो रहा है...")
        
        # Analyze conversations
        self.analyze_conversations()
        
        # Improve responses
        self.improve_responses()
        
        # Optimize memory
        self.optimize_memory()
        
        # Record evolution
        self.record_evolution()
        
        print("✅ इवोल्यूशन पूर्ण")
        
    def analyze_conversations(self):
        """Analyze conversations for patterns"""
        conversations = self.memory.data.get("conversations", [])
        
        if len(conversations) < 10:
            return
            
        # Find successful patterns
        successful_patterns = {}
        
        for conv in conversations[-100:]:  # Last 100 conversations
            user_msg = conv["user"].lower()
            
            # Simple pattern extraction
            words = user_msg.split()
            if len(words) > 2:
                pattern = " ".join(words[:2])  # First two words as pattern
                
                if pattern not in successful_patterns:
                    successful_patterns[pattern] = []
                    
                successful_patterns[pattern].append(conv["nova"])
                
        # Store patterns
        for pattern, responses in successful_patterns.items():
            if len(responses) > 2:  # Pattern used multiple times
                if pattern not in self.memory.data.get("learned_patterns", {}):
                    self.memory.data.setdefault("learned_patterns", {})[pattern] = []
                    
                # Add best response (most frequent)
                from collections import Counter
                response_counts = Counter(responses)
                best_response = response_counts.most_common(1)[0][0]
                
                self.memory.data["learned_patterns"][pattern].append({
                    "response": best_response,
                    "confidence": len(responses) / len(conversations),
                    "last_used": datetime.now().isoformat()
                })
                
    def improve_responses(self):
        """Improve response quality"""
        if "learned_patterns" not in self.memory.data:
            return
            
        for pattern, responses in self.memory.data["learned_patterns"].items():
            if responses:
                # Get most successful response
                latest_response = responses[-1]
                
                # Add variations
                variations = self.generate_variations(latest_response["response"])
                
                if "variations" not in latest_response:
                    latest_response["variations"] = []
                    
                latest_response["variations"].extend(variations[:3])
                
    def generate_variations(self, response):
        """Generate response variations"""
        variations = []
        
        # Add different openings
        openings = ["जी!", "हां सर!", "बिल्कुल!", "ज़रूर!"]
        
        for opening in openings:
            if not response.startswith(opening):
                variations.append(f"{opening} {response}")
                
        # Add different endings
        endings = ["😊", "👍", "जी!", "आपका दिन शुभ हो!"]
        
        for ending in endings:
            if not response.endswith(ending):
                variations.append(f"{response} {ending}")
                
        return variations
        
    def optimize_memory(self):
        """Optimize memory storage"""
        # Remove old conversations
        conversations = self.memory.data.get("conversations", [])
        if len(conversations) > 1000:
            self.memory.data["conversations"] = conversations[-1000:]
            
        # Remove old notifications
        notifications = self.memory.data.get("notifications", [])
        if len(notifications) > 500:
            self.memory.data["notifications"] = notifications[-500:]
            
        # Compress learnings
        if "learnings" in self.memory.data:
            for key in list(self.memory.data["learnings"].keys()):
                if len(self.memory.data["learnings"][key]) > 10:
                    self.memory.data["learnings"][key] = self.memory.data["learnings"][key][-10:]
                    
    def record_evolution(self):
        """Record evolution progress"""
        evolution_entry = {
            "timestamp": datetime.now().isoformat(),
            "conversations_count": len(self.memory.data.get("conversations", [])),
            "patterns_learned": len(self.memory.data.get("learned_patterns", {})),
            "version": self.get_version()
        }
        
        if "evolution_history" not in self.memory.data:
            self.memory.data["evolution_history"] = []
            
        self.memory.data["evolution_history"].append(evolution_entry)
        
    def get_version(self):
        """Get current version"""
        base_version = "1.0"
        evolutions = len(self.memory.data.get("evolution_history", []))
        return f"{base_version}.{evolutions}"
        
    def self_repair(self):
        """Self-repair mechanism"""
        print("🔧 सेल्फ-रिपेयर शुरू...")
        
        # Check memory integrity
        self.check_memory_integrity()
        
        # Check configuration
        self.check_configuration()
        
        # Backup critical data
        self.backup_critical_data()
        
        print("✅ सेल्फ-रिपेयर पूर्ण")
        
    def check_memory_integrity(self):
        """Check memory file integrity"""
        try:
            # Try to load and save memory
            temp_data = json.dumps(self.memory.data, indent=2)
            json.loads(temp_data)  # This will fail if corrupted
            return True
        except:
            # Create fresh memory
            print("⚠️ मेमोरी करप्ट, नई मेमोरी बना रहा हूं...")
            self.memory.data = self.memory.create_default_memory()
            return False
            
    def check_configuration(self):
        """Check and fix configuration"""
        required_keys = ['adb_host', 'auto_reply', 'voice_enabled']
        
        for key in required_keys:
            if key not in self.config:
                self.config[key] = self.get_default_config().get(key)
                
    def backup_critical_data(self):
        """Backup critical data"""
        critical_data = {
            "learned_patterns": self.memory.data.get("learned_patterns", {}),
            "user_preferences": self.memory.data.get("user_preferences", {}),
            "evolution_data": self.memory.data.get("evolution_data", {})
        }
        
        backup_file = self.memory.memory_file.with_suffix('.critical.backup')
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(critical_data, f, indent=2, ensure_ascii=False)
            
    def get_default_config(self):
        """Get default configuration"""
        return {
            "name": "Nova",
            "adb_host": "localhost:5555",
            "auto_reply": True,
            "voice_enabled": True,
            "ai_backend": "huggingchat"
        }
