import time
import re
from datetime import datetime

class NotificationMonitor:
    def __init__(self, adb, ai, memory):
        self.adb = adb
        self.ai = ai
        self.memory = memory
        self.last_notifications = []
        
    def monitor_continuously(self):
        """Monitor notifications 24/7"""
        print("🔔 नोटिफिकेशन मॉनिटरिंग शुरू (24/7)...")
        
        while True:
            try:
                # Check screen state
                screen_state = self.adb.get_screen_state()
                
                # Get notifications
                notifications = self.adb.get_notifications()
                
                # Check for new notifications
                new_notifs = self.get_new_notifications(notifications)
                
                # Process new notifications
                for notif in new_notifs:
                    self.process_notification(notif, screen_state)
                    
                # Update last notifications
                self.last_notifications = notifications
                
                # Sleep
                time.sleep(2)
                
            except Exception as e:
                print(f"Notification monitoring error: {e}")
                time.sleep(5)
                
    def get_new_notifications(self, current_notifs):
        """Get only new notifications"""
        new_notifs = []
        
        for notif in current_notifs:
            is_new = True
            for last_notif in self.last_notifications:
                if self.notifications_equal(notif, last_notif):
                    is_new = False
                    break
                    
            if is_new:
                new_notifs.append(notif)
                
        return new_notifs
        
    def notifications_equal(self, notif1, notif2):
        """Check if two notifications are the same"""
        keys = ['ticker', 'title', 'text', 'package']
        for key in keys:
            if notif1.get(key) != notif2.get(key):
                return False
        return True
        
    def process_notification(self, notification, screen_state):
        """Process a notification"""
        print(f"📱 नया नोटिफिकेशन: {notification.get('title', 'No title')}")
        
        # Speak notification if screen is off
        if screen_state == "OFF":
            self.speak_notification(notification)
            
        # Auto-reply for messaging apps
        if self.should_auto_reply(notification):
            self.auto_reply(notification)
            
        # Save to memory
        self.save_notification(notification)
        
    def speak_notification(self, notification):
        """Speak notification aloud"""
        title = notification.get('title', '')
        text = notification.get('text', '')
        package = notification.get('package', '')
        
        # Determine app name
        app_name = self.get_app_name(package)
        
        # Create message
        if app_name and title:
            message = f"{app_name} से {title} ने मैसेज भेजा है"
            if text:
                message += f": {text[:50]}"
        else:
            message = "नया नोटिफिकेशन आया है"
            
        # Speak (you would integrate with TTS here)
        print(f"🔊 बोल रही हूं: {message}")
        
    def should_auto_reply(self, notification):
        """Check if should auto-reply"""
        package = notification.get('package', '')
        
        # Check if from messaging app
        messaging_apps = [
            'com.whatsapp',
            'com.instagram.android',
            'com.facebook.orca',
            'org.telegram.messenger'
        ]
        
        if package in messaging_apps:
            return True
            
        return False
        
    def auto_reply(self, notification):
        """Auto-reply to notification"""
        print(f"🤖 ऑटो-रिप्लाई तैयार कर रही हूं...")
        
        # Extract sender and message
        sender = notification.get('title', '').split(':')[0]
        message = notification.get('text', '')
        
        # Generate reply
        reply = self.generate_reply(sender, message)
        
        # Open app and send reply
        self.send_reply(notification['package'], sender, reply)
        
        print(f"✅ रिप्लाई भेज दी: {reply[:50]}...")
        
    def generate_reply(self, sender, message):
        """Generate automatic reply"""
        # Simple rule-based replies
        greetings = ['hi', 'hello', 'नमस्ते', 'हैलो']
        questions = ['कैसे', 'क्या', 'कब', 'कहाँ', 'how', 'what', 'when', 'where']
        
        message_lower = message.lower()
        
        # Check for greeting
        if any(greet in message_lower for greet in greetings):
            replies = [
                f"हैलो {sender}! मैं नोवा हूं, आपके बॉस की असिस्टेंट।",
                f"नमस्ते {sender}! बॉस अभी व्यस्त हैं, मैं उन्हें बता दूंगी।",
                f"हैलो! मैं नोवा बोल रही हूं। आपका मैसेज बॉस को दिखा दूंगी।"
            ]
            
        # Check for question
        elif any(q in message_lower for q in questions):
            replies = [
                f"मैं यह जानकारी बॉस से पूछकर बताती हूं।",
                f"इस सवाल का जवाब मैं बॉस से पूछकर दूंगी।",
                f"बॉस से पूछती हूं और आपको जवाब देती हूं।"
            ]
            
        # Default reply
        else:
            replies = [
                f"धन्यवाद {sender}! बॉस को आपका मैसेज दिखा दूंगी।",
                f"मैसेज मिल गया {sender}। बॉस को इनफॉर्म कर देती हूं।",
                f"आपका मैसेज नोट कर लिया {sender}। बॉस रिप्लाई देंगे।"
            ]
            
        import random
        return random.choice(replies)
        
    def send_reply(self, package, sender, reply):
        """Send reply via ADB"""
        # This is a simplified version
        # Actual implementation would need to:
        # 1. Open the app
        # 2. Navigate to chat
        # 3. Type reply
        # 4. Send
        
        # For now, just log
        print(f"📤 रिप्लाई भेजी जा रही है...")
        print(f"ऐप: {package}")
        print(fसेंडर: {sender}")
        print(fरिप्लाई: {reply}")
        
        # You would implement actual ADB commands here
        # Example:
        # self.adb.open_app(package)
        # time.sleep(2)
        # self.adb.tap(x, y)  # Tap on chat
        # time.sleep(1)
        # self.adb.type_text(reply)
        # self.adb.press_key(66)  # Send
        
    def get_app_name(self, package):
        """Get app name from package"""
        app_names = {
            'com.whatsapp': 'WhatsApp',
            'com.instagram.android': 'Instagram',
            'com.facebook.orca': 'Messenger',
            'com.android.messaging': 'Messages',
            'com.google.android.gm': 'Gmail'
        }
        
        return app_names.get(package, package)
        
    def save_notification(self, notification):
        """Save notification to memory"""
        if 'notifications' not in self.memory.data:
            self.memory.data['notifications'] = []
            
        notification['timestamp'] = datetime.now().isoformat()
        self.memory.data['notifications'].append(notification)
        
        # Keep only last 100 notifications
        if len(self.memory.data['notifications']) > 100:
            self.memory.data['notifications'] = self.memory.data['notifications'][-100:]
