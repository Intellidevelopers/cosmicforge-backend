import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/telemedicine_app')
    
    # SMTP configuration for email notifications. Use App Password to make it easier
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'noreply@example.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your_smtp_password')
    
    # Firebase configuration for push notifications
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', 'path/to/firebase_credentials.json')
    
    # AI model configurations
    BERT_MODEL = os.getenv('BERT_MODEL', 'bert-base-uncased')
    GPT2_MODEL = os.getenv('GPT2_MODEL', 'gpt2')
    T5_MODEL = os.getenv('T5_MODEL', 't5-small')
    
    # API keys and external service configurations
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', 'your_google_translate_api_key')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/telemedicine_app_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
