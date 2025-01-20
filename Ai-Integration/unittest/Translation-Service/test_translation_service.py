import unittest
import json
import os
from flask import Flask
from werkzeug.datastructures import FileStorage
from your_app_file import app  # Import your Flask app

class TranslationServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_chat_text_translation(self):
        response = self.app.post('/chat', json={
            'text': 'Hello, world!',
            'target_lang': 'es'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('translated_text', data)
        self.assertEqual(data['source_lang'], 'en')
        self.assertEqual(data['target_lang'], 'es')

    def test_chat_file_translation(self):
        with open('test_file.txt', 'w') as f:
            f.write('Hello, world!')
        
        with open('test_file.txt', 'rb') as f:
            response = self.app.post('/chat', 
                data={
                    'file': (f, 'test_file.txt'),
                    'file_type': 'text',
                    'target_lang': 'es'
                },
                content_type='multipart/form-data'
            )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('translated_text', data)
        self.assertEqual(data['source_lang'], 'en')
        self.assertEqual(data['target_lang'], 'es')

        os.remove('test_file.txt')

    def test_chat_voice_translation(self):
        with open('test_audio.mp3', 'rb') as f:
            response = self.app.post('/chat', 
                data={
                    'file': (f, 'test_audio.mp3'),
                    'file_type': 'audio',
                    'target_lang': 'es'
                },
                content_type='multipart/form-data'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'audio/mpeg')

    def test_chat_video_translation(self):
        with open('test_video.mp4', 'rb') as f:
            response = self.app.post('/chat', 
                data={
                    'file': (f, 'test_video.mp4'),
                    'file_type': 'video',
                    'target_lang': 'es'
                },
                content_type='multipart/form-data'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'video/mp4')

    def test_standard_translation(self):
        response = self.app.post('/api/translate', json={
            'text': 'Hello, world!',
            'targetLanguage': 'fr'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('translatedText', data)
        self.assertEqual(data['sourceLang'], 'en')
        self.assertEqual(data['targetLang'], 'fr')

    def test_background_translation(self):
        # Start background translation
        response = self.app.post('/api/background_translate', json={
            'text': 'Hello, world!',
            'targetLanguage': 'de',
            'sessionId': 'test_session'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('sessionId', data)

        # Get background translation result
        response = self.app.get('/api/get_background_translation?sessionId=test_session')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('translatedText', data)

    def test_language_detection(self):
        response = self.app.post('/api/detect_language', json={
            'text': 'Bonjour le monde!'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['detectedLanguage'], 'fr')

    def test_supported_languages(self):
        response = self.app.get('/api/supported_languages')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('en', data)
        self.assertIn('es', data)
        self.assertIn('fr', data)

    def test_health_check(self):
        response = self.app.get('/health')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')

    def test_file_translation(self):
        with open('test_file.txt', 'w') as f:
            f.write('Hello, world!')
        
        with open('test_file.txt', 'rb') as f:
            response = self.app.post('/api/translate_file', 
                data={
                    'file': (f, 'test_file.txt'),
                    'target_lang': 'es'
                },
                content_type='multipart/form-data'
            )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('translatedText', data)
        self.assertEqual(data['sourceLang'], 'en')
        self.assertEqual(data['targetLang'], 'es')

        os.remove('test_file.txt')

    def test_voice_translation(self):
        # For this test, you need a sample audio file
        with open('test_audio.mp3', 'rb') as f:
            response = self.app.post('/api/translate_voice', 
                data={
                    'file': (f, 'test_audio.mp3'),
                    'target_lang': 'es'
                },
                content_type='multipart/form-data'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'audio/mpeg')

    def test_video_translation(self):
        # For this test, you need a sample video file
        with open('test_video.mp4', 'rb') as f:
            response = self.app.post('/api/translate_video', 
                data={
                    'file': (f, 'test_video.mp4'),
                    'target_lang': 'es'
                },
                content_type='multipart/form-data'
            )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'video/mp4')

if __name__ == '__main__':
    unittest.main()
