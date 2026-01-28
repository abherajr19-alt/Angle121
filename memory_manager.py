import json
import os
from datetime import datetime
from pathlib import Path

class MemoryManager:
    def __init__(self, memory_file):
        self.memory_file = Path(memory_file)
        self.data = self.load_memory()
        
    def load_memory(self):
        """Load memory from file"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self.create_default_memory()
        else:
            return self.create_default_memory()
            
    def create_default_memory(self):
        """Create default memory structure"""
        return {
            "conversations": [],
            "learnings": {},
            "notifications": [],
            "commands_history": [],
            "user_preferences": {},
            "evolution_data": {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "upgrades": []
            },
            "settings": {
                "auto_reply": True,
                "voice_enabled": True,
                "learning_enabled": True
            }
        }
        
    def save(self):
        """Save memory to file"""
        # Create backup
        if self.memory_file.exists():
            backup_file = self.memory_file.with_suffix('.json.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                
        # Save current
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
            
    def add_conversation(self, user_input, nova_response):
        """Add conversation to memory"""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "nova": nova_response,
            "context": self.get_context()
        }
        
        self.data["conversations"].append(conversation)
        
        # Keep only last 500 conversations
        if len(self.data["conversations"]) > 500:
            self.data["conversations"] = self.data["conversations"][-500:]
            
        # Auto-save
        self.save()
        
    def get_context(self):
        """Get current context"""
        return {
            "time": datetime.now().strftime("%H:%M"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "last_5_conversations": self.data["conversations"][-5:] if len(self.data["conversations"]) >= 5 else self.data["conversations"]
        }
        
    def add_learning(self, pattern, response):
        """Add learning pattern"""
        if pattern not in self.data["learnings"]:
            self.data["learnings"][pattern] = []
            
        self.data["learnings"][pattern].append({
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "used_count": 0
        })
        
    def get_learning(self, pattern):
        """Get learning for pattern"""
        return self.data["learnings"].get(pattern, [])
        
    def auto_backup(self):
        """Auto-backup memory"""
        import time
        import threading
        
        def backup_loop():
            while True:
                time.sleep(300)  # 5 minutes
                self.save()
                print("💾 मेमोरी ऑटो-बैकअप किया गया")
                
        thread = threading.Thread(target=backup_loop, daemon=True)
        thread.start()
        
    def search_memory(self, query):
        """Search in memory"""
        results = []
        query_lower = query.lower()
        
        # Search conversations
        for conv in self.data["conversations"]:
            if query_lower in conv["user"].lower() or query_lower in conv["nova"].lower():
                results.append(conv)
                
        return results
