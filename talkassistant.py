import speech_recognition as sr
import google.generativeai as genai
import threading
import os
from gtts import gTTS

class VoiceAgent:
    def __init__(self, api_key):
        # Configure Gemini
        genai.configure(api_key=api_key)

        system_instruction = (
            "You are a helpful, conversational voice assistant. Your responses must be brief and at a maximum of 3 sentences regardless of prompt, "
            "use short, natural-sounding sentences, and read aloud clearly. Never use special characters, "
            "Markdown formatting (like bolding, lists, or headers), or emojis. Focus purely "
            "on the content in a friendly, spoken tone."
        )

        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            system_instruction=system_instruction
        )
        
        # Configure Speech Recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.5  # Wait for 1.5s silence, then stop listening
        self.running = False

    def speak(self, text):
        """Generates a human-like voice using Google TTS and plays it."""
        if not text: return
        print(f"[Voice] Speaking response...")
        
        try:
            tts = gTTS(text=text, lang='en', tld='us') 
            
            # save to a temporary file
            filename = "temp_response.mp3"
            tts.save(filename)
            
            # mpg321 is light on Pi
            # The -q flag keeps it quiet (no text output from player)
            os.system(f"mpg321 -q {filename}")
            
            # clean up
            os.remove(filename)
            
        except Exception as e:
            print(f"[Voice] TTS Error: {e}")

    def listen_once(self):
        with sr.Microphone() as source:
            print("[Voice] Adjusting for noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("[Voice] Listening (waiting for 1.5s pause)...")
            
            try:
                audio = self.recognizer.listen(source, timeout=None)
                print("[Voice] Processing audio...")
                text = self.recognizer.recognize_google(audio)
                print(f"[Voice] User said: '{text}'")
                return text
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                print("[Voice] Connection error during recognition.")
                return None
            except Exception:
                return None

    def get_ai_response(self, prompt):
        if not prompt: return None
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[Voice] Gemini Error: {e}")
            return None

    def start_loop(self):
        self.running = True
        print("--- Voice Agent Thread Started, exit = [quit, exit, stop] ---")
        
        while self.running:
            user_text = self.listen_once()
            
            if user_text:
                if user_text.lower() in ["quit", "exit", "stop"]:
                    print("[Voice] Stopping voice loop...")
                    self.speak("Goodbye.")
                    self.running = False
                    break
                
                response = self.get_ai_response(user_text)
                if response:
                    print(f"\n--- GEMINI ---\n{response}\n--------------\n")
                    self.speak(response)
