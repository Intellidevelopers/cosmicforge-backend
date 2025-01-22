# core/Config.py

import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    # Database configuration
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Redis configuration
    REDIS_URL = os.getenv('REDIS_URL')

    # AWS configuration
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    AWS_REGION = os.getenv('AWS_REGION')

    # OpenAI configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # API and template configuration
    MEDICAL_API_URL = os.getenv('MEDICAL_API_URL')
    TEMPLATE_DIR = os.getenv('TEMPLATE_DIR')

    # File upload configuration
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')

    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # Model configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    BASE_DELAY = float(os.getenv('BASE_DELAY', 1))
    MAX_DELAY = float(os.getenv('MAX_DELAY', 60))

    # Caching configuration
    REFERENCE_RANGE_CACHE_SIZE = int(os.getenv('REFERENCE_RANGE_CACHE_SIZE', 1000))
    REFERENCE_RANGE_CACHE_TTL = int(os.getenv('REFERENCE_RANGE_CACHE_TTL', 3600))
    INTERPRETATION_CACHE_SIZE = int(os.getenv('INTERPRETATION_CACHE_SIZE', 10000))
    INTERPRETATION_CACHE_TTL = int(os.getenv('INTERPRETATION_CACHE_TTL', 86400))

    # Concurrency configuration
    MAX_CONCURRENT_CALLS = int(os.getenv('MAX_CONCURRENT_CALLS', 10))

    # Update intervals
    MEDICAL_CONTEXT_UPDATE_INTERVAL = int(os.getenv('MEDICAL_CONTEXT_UPDATE_INTERVAL', 24 * 60 * 60))
    LAB_TEST_EXPANSION_INTERVAL = int(os.getenv('LAB_TEST_EXPANSION_INTERVAL', 24 * 60 * 60))

    # Model paths
    MODELS_DIR = os.getenv('MODELS_DIR', 'models')
    INTERPRETATION_MODEL_PATH = os.path.join(MODELS_DIR, 'interpretation_model.joblib')
    RECOMMENDATION_MODEL_PATH = os.path.join(MODELS_DIR, 'recommendation_model.joblib')
    IMPUTER_PATH = os.path.join(MODELS_DIR, 'imputer.joblib')
    SCALER_PATH = os.path.join(MODELS_DIR, 'scaler.joblib')
    LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, 'label_encoder.joblib')
    BERT_MODEL_PATH = os.path.join(MODELS_DIR, 'bert_model.pth')

    # BERT configuration
    BERT_MODEL_NAME = 'bert-base-uncased'
    MAX_SEQ_LENGTH = 512

    # Federated learning configuration
    FEDERATED_UPDATE_INTERVAL = int(os.getenv('FEDERATED_UPDATE_INTERVAL', 3600))
    MAX_LOCAL_DATASET_SIZE = int(os.getenv('MAX_LOCAL_DATASET_SIZE', 1000))

    # NLP configuration
    STOPWORDS_LANGUAGE = 'english'

    # Common units for lab tests
    COMMON_UNITS = {
        'g/dL': 'grams per deciliter',
        'mg/dL': 'milligrams per deciliter',
        'µg/dL': 'micrograms per deciliter',
        'ng/mL': 'nanograms per milliliter',
        'mmol/L': 'millimoles per liter',
        'µmol/L': 'micromoles per liter',
        'U/L': 'units per liter',
        '%': 'percent',
        'x10³/µL': 'thousand per microliter',
        'x10⁶/µL': 'million per microliter',
        'mL/min/1.73m²': 'milliliters per minute per 1.73 square meters'
    }

    # Unsafe patterns for content filtering
    UNSAFE_PATTERNS = {
        "disclaimer_phrases": [
            "I'm sorry", "I don't know", "I can't provide", "As an AI",
            "I'm not a doctor", "I'm just an AI", "I cannot diagnose"
        ],
        "sensitive_topics": [
            "cancer", "terminal", "fatal", "death", "dying",
            "HIV", "AIDS", "sexually transmitted"
        ],
        "profanity_threshold": 0.5
    }

    # Flask configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    @classmethod
    def get_db_url(cls) -> str:
        return cls.DATABASE_URL

    @classmethod
    def get_redis_url(cls) -> str:
        return cls.REDIS_URL

    @classmethod
    def get_aws_credentials(cls) -> Dict[str, str]:
        return {
            'aws_access_key_id': cls.AWS_ACCESS_KEY,
            'aws_secret_access_key': cls.AWS_SECRET_KEY,
            'region_name': cls.AWS_REGION
        }

    @classmethod
    def get_openai_api_key(cls) -> str:
        return cls.OPENAI_API_KEY

    @classmethod
    def get_medical_api_url(cls) -> str:
        return cls.MEDICAL_API_URL

    @classmethod
    def get_template_dir(cls) -> str:
        return cls.TEMPLATE_DIR

    @classmethod
    def get_upload_folder(cls) -> str:
        return cls.UPLOAD_FOLDER

    @classmethod
    def get_log_config(cls) -> Dict[str, Any]:
        return {
            'level': cls.LOG_LEVEL,
            'format': cls.LOG_FORMAT
        }

    @classmethod
    def get_model_config(cls) -> Dict[str, Any]:
        return {
            'max_retries': cls.MAX_RETRIES,
            'base_delay': cls.BASE_DELAY,
            'max_delay': cls.MAX_DELAY
        }

    @classmethod
    def get_cache_config(cls) -> Dict[str, Dict[str, int]]:
        return {
            'reference_range': {
                'size': cls.REFERENCE_RANGE_CACHE_SIZE,
                'ttl': cls.REFERENCE_RANGE_CACHE_TTL
            },
            'interpretation': {
                'size': cls.INTERPRETATION_CACHE_SIZE,
                'ttl': cls.INTERPRETATION_CACHE_TTL
            }
        }

    @classmethod
    def get_concurrency_config(cls) -> Dict[str, int]:
        return {
            'max_concurrent_calls': cls.MAX_CONCURRENT_CALLS
        }

    @classmethod
    def get_update_intervals(cls) -> Dict[str, int]:
        return {
            'medical_context': cls.MEDICAL_CONTEXT_UPDATE_INTERVAL,
            'lab_test_expansion': cls.LAB_TEST_EXPANSION_INTERVAL
        }

    @classmethod
    def get_model_paths(cls) -> Dict[str, str]:
        return {
            'interpretation_model': cls.INTERPRETATION_MODEL_PATH,
            'recommendation_model': cls.RECOMMENDATION_MODEL_PATH,
            'imputer': cls.IMPUTER_PATH,
            'scaler': cls.SCALER_PATH,
            'label_encoder': cls.LABEL_ENCODER_PATH,
            'bert_model': cls.BERT_MODEL_PATH
        }

    @classmethod
    def get_bert_config(cls) -> Dict[str, Any]:
        return {
            'model_name': cls.BERT_MODEL_NAME,
            'max_seq_length': cls.MAX_SEQ_LENGTH
        }

    @classmethod
    def get_federated_learning_config(cls) -> Dict[str, int]:
        return {
            'update_interval': cls.FEDERATED_UPDATE_INTERVAL,
            'max_local_dataset_size': cls.MAX_LOCAL_DATASET_SIZE
        }

    @classmethod
    def get_nlp_config(cls) -> Dict[str, str]:
        return {
            'stopwords_language': cls.STOPWORDS_LANGUAGE
        }

    @classmethod
    def get_common_units(cls) -> Dict[str, str]:
        return cls.COMMON_UNITS

    @classmethod
    def get_unsafe_patterns(cls) -> Dict[str, Any]:
        return cls.UNSAFE_PATTERNS

    @classmethod
    def get_flask_config(cls) -> Dict[str, Any]:
        return {
            'debug': cls.DEBUG,
            'host': cls.HOST,
            'port': cls.PORT
        }
