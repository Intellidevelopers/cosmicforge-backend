import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')
    MODEL_DIR = os.path.join(BASE_DIR, 'models')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    LOG_FILE = os.path.join(LOG_DIR, 'medical_diagnosis.log')
    MODEL_VERSION = '1.0'  