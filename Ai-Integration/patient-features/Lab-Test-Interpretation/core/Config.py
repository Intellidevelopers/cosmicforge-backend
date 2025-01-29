import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        load_dotenv()
        self._config = {}
        self._load_config()

    def _load_config(self):
        # Database configuration
        self._set('DB_USER', os.getenv('DB_USER'))
        self._set('DB_PASSWORD', os.getenv('DB_PASSWORD'))
        self._set('DB_HOST', os.getenv('DB_HOST'))
        self._set('DB_PORT', os.getenv('DB_PORT'))
        self._set('DB_NAME', os.getenv('DB_NAME'))
        self._set('DATABASE_URL', f"postgresql+asyncpg://{self._get('DB_USER')}:{self._get('DB_PASSWORD')}@{self._get('DB_HOST')}:{self._get('DB_PORT')}/{self._get('DB_NAME')}")

        # Redis configuration
        self._set('REDIS_URL', os.getenv('REDIS_URL'))

        # AWS configuration
        self._set('AWS_ACCESS_KEY', os.getenv('AWS_ACCESS_KEY'))
        self._set('AWS_SECRET_KEY', os.getenv('AWS_SECRET_KEY'))
        self._set('AWS_REGION', os.getenv('AWS_REGION'))

        # OpenAI configuration
        self._set('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY'))

        # API and template configuration
        self._set('MEDICAL_API_URL', os.getenv('MEDICAL_API_URL'))
        self._set('TEMPLATE_DIR', os.getenv('TEMPLATE_DIR'))

        # File upload configuration
        self._set('UPLOAD_FOLDER', os.getenv('UPLOAD_FOLDER', '/tmp/uploads'))

        # Logging configuration
        self._set('LOG_LEVEL', os.getenv('LOG_LEVEL', 'INFO'))
        self._set('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')

        # Model configuration
        self._set('MAX_RETRIES', int(os.getenv('MAX_RETRIES', '3')))
        self._set('BASE_DELAY', float(os.getenv('BASE_DELAY', '1')))
        self._set('MAX_DELAY', float(os.getenv('MAX_DELAY', '60')))

        # Caching configuration
        self._set('REFERENCE_RANGE_CACHE_SIZE', int(os.getenv('REFERENCE_RANGE_CACHE_SIZE', '1000')))
        self._set('REFERENCE_RANGE_CACHE_TTL', int(os.getenv('REFERENCE_RANGE_CACHE_TTL', '3600')))
        self._set('INTERPRETATION_CACHE_SIZE', int(os.getenv('INTERPRETATION_CACHE_SIZE', '10000')))
        self._set('INTERPRETATION_CACHE_TTL', int(os.getenv('INTERPRETATION_CACHE_TTL', '86400')))

        # Concurrency configuration
        self._set('MAX_CONCURRENT_CALLS', int(os.getenv('MAX_CONCURRENT_CALLS', '10')))

        # Update intervals
        self._set('MEDICAL_CONTEXT_UPDATE_INTERVAL', int(os.getenv('MEDICAL_CONTEXT_UPDATE_INTERVAL', '86400')))
        self._set('LAB_TEST_EXPANSION_INTERVAL', int(os.getenv('LAB_TEST_EXPANSION_INTERVAL', '86400')))

        # Model paths
        self._set('MODELS_DIR', os.getenv('MODELS_DIR', 'models'))
        self._set('INTERPRETATION_MODEL_PATH', os.path.join(self._get('MODELS_DIR'), 'interpretation_model.joblib'))
        self._set('RECOMMENDATION_MODEL_PATH', os.path.join(self._get('MODELS_DIR'), 'recommendation_model.joblib'))
        self._set('IMPUTER_PATH', os.path.join(self._get('MODELS_DIR'), 'imputer.joblib'))
        self._set('SCALER_PATH', os.path.join(self._get('MODELS_DIR'), 'scaler.joblib'))
        self._set('LABEL_ENCODER_PATH', os.path.join(self._get('MODELS_DIR'), 'label_encoder.joblib'))
        self._set('BERT_MODEL_PATH', os.path.join(self._get('MODELS_DIR'), 'bert_model.pth'))

        # BERT configuration
        self._set('BERT_MODEL_NAME', 'bert-base-uncased')
        self._set('MAX_SEQ_LENGTH', 512)

        # Federated learning configuration
        self._set('FEDERATED_UPDATE_INTERVAL', int(os.getenv('FEDERATED_UPDATE_INTERVAL', '3600')))
        self._set('MAX_LOCAL_DATASET_SIZE', int(os.getenv('MAX_LOCAL_DATASET_SIZE', '1000')))

        # NLP configuration
        self._set('STOPWORDS_LANGUAGE', 'english')

        # Common units for lab tests
        self._set('COMMON_UNITS', {
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
        })

        # Unsafe patterns for content filtering
        self._set('UNSAFE_PATTERNS', {
            "disclaimer_phrases": [
                "I'm sorry", "I don't know", "I can't provide", "As an AI",
                "I'm not a doctor", "I'm just an AI", "I cannot diagnose"
            ],
            "sensitive_topics": [
                "cancer", "terminal", "fatal", "death", "dying",
                "HIV", "AIDS", "sexually transmitted"
            ],
            "profanity_threshold": 0.5
        })

        # Flask configuration
        self._set('DEBUG', os.getenv('DEBUG', 'False').lower() == 'true')
        self._set('HOST', os.getenv('HOST', '0.0.0.0'))
        self._set('PORT', int(os.getenv('PORT', '5000')))

        self._validate_config()

    def _set(self, key: str, value: Any):
        self._config[key] = value

    def _get(self, key: str) -> Any:
        return self._config.get(key)

    def _validate_config(self):
        required_keys = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'OPENAI_API_KEY']
        for key in required_keys:
            if not self._get(key):
                raise ValueError(f"Missing required configuration: {key}")

    def get_db_url(self) -> str:
        return self._get('DATABASE_URL')

    def get_redis_url(self) -> str:
        return self._get('REDIS_URL')

    def get_aws_credentials(self) -> Dict[str, str]:
        return {
            'aws_access_key_id': self._get('AWS_ACCESS_KEY'),
            'aws_secret_access_key': self._get('AWS_SECRET_KEY'),
            'region_name': self._get('AWS_REGION')
        }

    def get_openai_api_key(self) -> str:
        return self._get('OPENAI_API_KEY')

    def get_medical_api_url(self) -> str:
        return self._get('MEDICAL_API_URL')

    def get_template_dir(self) -> str:
        return self._get('TEMPLATE_DIR')

    def get_upload_folder(self) -> str:
        return self._get('UPLOAD_FOLDER')

    def get_log_config(self) -> Dict[str, Any]:
        return {
            'level': self._get('LOG_LEVEL'),
            'format': self._get('LOG_FORMAT')
        }

    def get_model_config(self) -> Dict[str, Any]:
        return {
            'max_retries': self._get('MAX_RETRIES'),
            'base_delay': self._get('BASE_DELAY'),
            'max_delay': self._get('MAX_DELAY')
        }

    def get_cache_config(self) -> Dict[str, Dict[str, int]]:
        return {
            'reference_range': {
                'size': self._get('REFERENCE_RANGE_CACHE_SIZE'),
                'ttl': self._get('REFERENCE_RANGE_CACHE_TTL')
            },
            'interpretation': {
                'size': self._get('INTERPRETATION_CACHE_SIZE'),
                'ttl': self._get('INTERPRETATION_CACHE_TTL')
            }
        }

    def get_concurrency_config(self) -> Dict[str, int]:
        return {
            'max_concurrent_calls': self._get('MAX_CONCURRENT_CALLS')
        }

    def get_update_intervals(self) -> Dict[str, int]:
        return {
            'medical_context': self._get('MEDICAL_CONTEXT_UPDATE_INTERVAL'),
            'lab_test_expansion': self._get('LAB_TEST_EXPANSION_INTERVAL')
        }

    def get_model_paths(self) -> Dict[str, str]:
        return {
            'interpretation_model': self._get('INTERPRETATION_MODEL_PATH'),
            'recommendation_model': self._get('RECOMMENDATION_MODEL_PATH'),
            'imputer': self._get('IMPUTER_PATH'),
            'scaler': self._get('SCALER_PATH'),
            'label_encoder': self._get('LABEL_ENCODER_PATH'),
            'bert_model': self._get('BERT_MODEL_PATH')
        }

    def get_bert_config(self) -> Dict[str, Any]:
        return {
            'model_name': self._get('BERT_MODEL_NAME'),
            'max_seq_length': self._get('MAX_SEQ_LENGTH')
        }

    def get_federated_learning_config(self) -> Dict[str, int]:
        return {
            'update_interval': self._get('FEDERATED_UPDATE_INTERVAL'),
            'max_local_dataset_size': self._get('MAX_LOCAL_DATASET_SIZE')
        }

    def get_nlp_config(self) -> Dict[str, str]:
        return {
            'stopwords_language': self._get('STOPWORDS_LANGUAGE')
        }

    def get_common_units(self) -> Dict[str, str]:
        return self._get('COMMON_UNITS')

    def get_unsafe_patterns(self) -> Dict[str, Any]:
        return self._get('UNSAFE_PATTERNS')

    def get_flask_config(self) -> Dict[str, Any]:
        return {
            'debug': self._get('DEBUG'),
            'host': self._get('HOST'),
            'port': self._get('PORT')
        }

config = Config()