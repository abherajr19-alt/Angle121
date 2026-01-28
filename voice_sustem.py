import subprocess
import tempfile
import os

class VoiceSystem:
    def __init__(self, config):
        self.config = config
        self.is_speaking = False
        
    def listen(self):
        """Listen for voice input using Termux API"""
        try:
            # Create temp file for recording
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                temp_file = tmp.name
                
            # Record audio using Termux API
            result = subprocess.run(
                ["termux-microphone-record", "-f", temp_file, "-l", "3"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Convert speech to text
                text = self.speech_to_text(temp_file)
                
                # Cleanup
                os.unlink(temp_file)
                
                return text
                
        except Exception as e:
            print(f"Voice listening error: {e}")
            return None
            
    def speech_to_text(self, audio_file):
        """Convert speech to text"""
        # Using Termux API for speech recognition
        try:
            result = subprocess.run(
                ["termux-speech-to-text"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout:
                return result.stdout.strip()
                
        except:
            pass
            
        # Fallback: Google's speech recognition (requires internet)
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language='hi-IN')
                return text
                
        except:
            return "मैंने आपकी आवाज नहीं समझी"
            
    def speak(self, text):
        """Speak text using Termux TTS"""
        self.is_speaking = True
        
        try:
            # Clean text for TTS
            text = text.replace('"', '').replace("'", "")
            
            # Speak using Termux TTS
            subprocess.run(
                ["termux-tts-speak", "-l", "hi", "-r", "1.0", text],
                capture_output=True,
                text=True,
                timeout=10
            )
            
        except Exception as e:
            print(f"TTS error: {e}")
            # Fallback: print text
            print(f"🔊 {text}")
            
        finally:
            self.is_speaking = False
            
    def stop_speaking(self):
        """Stop any ongoing speech"""
        try:
            subprocess.run(["termux-tts-speak", "--stop"],
                          capture_output=True, text=True)
        except:
            pass
            
        self.is_speaking = False
