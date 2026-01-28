import json
import requests
import re
from datetime import datetime

class AIEngine:
    def __init__(self, config, memory):
        self.config = config
        self.memory = memory
        self.backend = config['ai_backend']
        self.responses = self.load_responses()
        
    def load_responses(self):
        """Load response patterns"""
        return {
            "greeting": [
                "नमस्ते सर! आप कैसे हैं?",
                "हैलो! मुझे देखकर खुशी हुई।",
                "आपका दिन शुभ हो! मैं नोवा हूं।"
            ],
            "time": [
                "अभी समय है {time}",
                "सर, टाइम {time} है",
                "{time} बज चुके हैं"
            ],
            "date": [
                "आज की तारीख {date} है",
                "आज {date} है",
                "तारीख {date} है"
            ]
        }
    
    def process(self, command, context, personality):
        """Process command through AI"""
        # Try multiple backends
        response = None
        
        # 1. Try Sambanova
        if self.backend == "sambanova" or response is None:
            response = self.try_sambanova(command)
            
        # 2. Try HuggingChat
        if self.backend == "huggingchat" or response is None:
            response = self.try_huggingchat(command)
            
        # 3. Try local AI
        if response is None:
            response = self.local_ai(command)
            
        # Add personality
        response = self.add_personality(response, personality)
        
        # Learn from interaction
        self.learn(command, response)
        
        return response
        
    def try_sambanova(self, command):
        """Try Sambanova API"""
        # Placeholder - add your Sambanova API key
        api_key = self.config.get('sambanova_api_key', '')
        if not api_key:
            return None
            
        try:
            # API call structure
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "prompt": command,
                "max_tokens": 150
            }
            
            # response = requests.post(
            #     "https://api.sambanova.ai/v1/complete",
            #     headers=headers,
            #     json=data
            # )
            # 
            # if response.status_code == 200:
            #     return response.json()['text']
            
            return None
            
        except:
            return None
            
    def try_huggingchat(self, command):
        """Try HuggingChat without API"""
        # This is a web scraping approach
        # Since we can't implement full scraping here, using fallback
        
        # Simulate HuggingChat-like response
        responses = [
            f"मैं समझ गई आपकी बात: '{command}'। मैं आपकी मदद कैसे कर सकती हूं?",
            f"आपका संदेश मिल गया: '{command}'। क्या आप और विस्तार से बता सकते हैं?",
            f"हां सर, मैंने सुन लिया। आप चाहते हैं: '{command}'"
        ]
        
        import random
        return random.choice(responses)
        
    def local_ai(self, command):
        """Local rule-based AI"""
        command_lower = command.lower()
        
        # Greetings
        if any(word in command_lower for word in ['hi', 'hello', 'नमस्ते', 'हैलो']):
            import random
            return random.choice(self.responses["greeting"])
            
        # Time
        elif any(word in command_lower for word in ['time', 'समय', 'कितना बजा']):
            current_time = datetime.now().strftime("%I:%M %p")
            import random
            return random.choice(self.responses["time"]).format(time=current_time)
            
        # Date
        elif any(word in command_lower for word in ['date', 'तारीख', 'आज क्या तारीख']):
            current_date = datetime.now().strftime("%d %B, %Y")
            import random
            return random.choice(self.responses["date"]).format(date=current_date)
            
        # Default response
        return f"मैंने समझ लिया: '{command}'। मैं इसपर काम कर रही हूं।"
        
    def add_personality(self, response, personality):
        """Add personality to response"""
        if personality['style'] == 'friendly_feminine':
            # Add feminine friendly touches
            enhancements = ['जी!', 'सर!', 'आपके लिए', 'ज़रूर']
            import random
            if random.random() > 0.5:
                response = f"{random.choice(enhancements)} {response}"
                
        # Add Hinglish flavor
        if personality['language'] == 'hinglish':
            response = self.make_hinglish(response)
            
        return response
        
    def make_hinglish(self, text):
        """Convert text to Hinglish style"""
        replacements = {
            'मैं': 'मैं',
            'आप': 'तुम',
            'कर': 'करो',
            'है': 'है',
            'हूं': 'हूं'
        }
        
        for hindi, hinglish in replacements.items():
            text = text.replace(hindi, hinglish)
            
        return text
        
    def generate_code(self, topic):
        """Generate code for given topic"""
        # Simple code templates
        templates = {
            'python': '''# Python code for {topic}
def main():
    print("Hello, World!")
    
if __name__ == "__main__":
    main()''',
            
            'website': '''<!-- HTML for {topic} -->
<!DOCTYPE html>
<html>
<head>
    <title>{topic}</title>
</head>
<body>
    <h1>Welcome to {topic}</h1>
</body>
</html>''',
            
            'android': '''// Android code for {topic}
public class MainActivity extends AppCompatActivity {{
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }}
}}'''
        }
        
        # Detect language
        if 'python' in topic.lower():
            lang = 'python'
        elif 'html' in topic.lower() or 'website' in topic.lower():
            lang = 'website'
        elif 'android' in topic.lower() or 'app' in topic.lower():
            lang = 'android'
        else:
            lang = 'python'
            
        return templates[lang].format(topic=topic)
        
    def learn(self, command, response):
        """Learn from interactions"""
        if 'learnings' not in self.memory.data:
            self.memory.data['learnings'] = {}
            
        key = command[:50]  # First 50 chars as key
        self.memory.data['learnings'][key] = {
            'command': command,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'count': self.memory.data['learnings'].get(key, {}).get('count', 0) + 1
        }
