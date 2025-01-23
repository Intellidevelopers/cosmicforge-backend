import asyncio
import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
import aiofiles
import io
import logging

class VoiceInterface:
    def __init__(self):
        self.recognizer = None
        self.logger = None

    async def initialize(self):
        # Set up logging
        self.logger = logging.getLogger('VoiceInterface')
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                self.logger.info("Adjusting for ambient noise. Please wait...")
                await asyncio.to_thread(self.recognizer.adjust_for_ambient_noise, source, duration=5)
                self.logger.info("Ambient noise adjustment complete.")
        except sr.RequestError:
            self.logger.warning("Could not adjust for ambient noise. Microphone may not be available.")

        # Test text-to-speech functionality
        try:
            test_audio = await self.text_to_speech("Voice interface initialized successfully.")
            os.remove(test_audio) 
            self.logger.info("Text-to-speech functionality tested successfully.")
        except Exception as e:
            self.logger.error(f"Error testing text-to-speech functionality: {e}")

        self.logger.info("Voice interface initialization complete.")

    async def speech_to_text(self, audio_file):
        if not self.recognizer:
            raise RuntimeError("VoiceInterface not initialized. Call initialize() first.")

        async with aiofiles.open(audio_file, 'rb') as file:
            audio_data = await file.read()

        def recognize_audio():
            with sr.AudioFile(io.BytesIO(audio_data)) as source:
                audio = self.recognizer.record(source)
            try:
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return "Speech recognition could not understand the audio"
            except sr.RequestError as e:
                return f"Could not request results from speech recognition service; {e}"

        return await asyncio.to_thread(recognize_audio)

    async def text_to_speech(self, text):
        if not self.recognizer:
            raise RuntimeError("VoiceInterface not initialized. Call initialize() first.")

        def generate_speech():
            tts = gTTS(text=text, lang='en')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                tts.save(fp.name)
                return fp.name

        audio_file = await asyncio.to_thread(generate_speech)
        return audio_file


