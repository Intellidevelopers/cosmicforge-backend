import os
from dotenv import load_dotenv
from typing import Dict, Any
import secrets
import logging

# Load environment variables from .env file
load_dotenv()

class BaseConfig:
    @classmethod
    def get_env(cls, key: str, default: Any = None, required: bool = False) -> Any:
        value = os.getenv(key, default)
        if required and value is None:
            raise ValueError(f"Environment variable {key} is required but not set.")
        return value

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        return cls.get_env(key, str(default)).lower() in ('true', '1', 'yes', 'on')

    @classmethod
    def get_int(cls, key: str, default: int) -> int:
        try:
            return int(cls.get_env(key, default))
        except ValueError:
            logging.warning(f"Invalid integer value for {key}. Using default: {default}")
            return default

    @classmethod
    def get_float(cls, key: str, default: float) -> float:
        try:
            return float(cls.get_env(key, default))
        except ValueError:
            logging.warning(f"Invalid float value for {key}. Using default: {default}")
            return default

    @classmethod
    def get_list(cls, key: str, default: list, separator: str = ',') -> list:
        value = cls.get_env(key)
        return value.split(separator) if value else default

class Config(BaseConfig):
    # Database configuration
    DATABASE_URL = BaseConfig.get_env("DATABASE_URL", required=True)

    # JWT configuration
    SECRET_KEY = BaseConfig.get_env("SECRET_KEY", secrets.token_urlsafe(32))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = BaseConfig.get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

    # Hugging Face configuration
    HUGGINGFACE_TOKEN = BaseConfig.get_env("HUGGINGFACE_TOKEN", required=True)
    HUGGINGFACE_REPO_ID = BaseConfig.get_env("HUGGINGFACE_REPO_ID", "your-repo/health-models")

    # AI Model configuration
    HEALTH_SCORE_MODEL_NAME = "health_score_model.joblib"
    HEALTH_PLAN_MODEL_NAME = "health_plan_model.joblib"

    # Data integration configuration
    WEARABLE_API_URL = BaseConfig.get_env("WEARABLE_API_URL", "https://api.wearabledevice.com")
    EHR_API_URL = BaseConfig.get_env("EHR_API_URL", "https://api.ehrsystem.com")
    LAB_RESULTS_API_URL = BaseConfig.get_env("LAB_RESULTS_API_URL", "https://api.labresults.com")

    # Notification settings
    EMAIL_NOTIFICATIONS_ENABLED = BaseConfig.get_bool("EMAIL_NOTIFICATIONS_ENABLED", True)
    SMS_NOTIFICATIONS_ENABLED = BaseConfig.get_bool("SMS_NOTIFICATIONS_ENABLED", False)
    PUSH_NOTIFICATIONS_ENABLED = BaseConfig.get_bool("PUSH_NOTIFICATIONS_ENABLED", True)

    # Privacy settings
    DEFAULT_SHARE_DATA_WITH_DOCTORS = BaseConfig.get_bool("DEFAULT_SHARE_DATA_WITH_DOCTORS", True)
    DEFAULT_SHARE_ANONYMIZED_DATA = BaseConfig.get_bool("DEFAULT_SHARE_ANONYMIZED_DATA", False)

    # Logging configuration
    LOG_LEVEL = BaseConfig.get_env("LOG_LEVEL", "INFO")

    # API rate limiting
    RATE_LIMIT_REQUESTS = BaseConfig.get_int("RATE_LIMIT_REQUESTS", 100)
    RATE_LIMIT_PERIOD = BaseConfig.get_int("RATE_LIMIT_PERIOD", 3600)  # in seconds

    # Feature flags
    ENABLE_AI_PREDICTIONS = BaseConfig.get_bool("ENABLE_AI_PREDICTIONS", True)
    ENABLE_REAL_TIME_ALERTS = BaseConfig.get_bool("ENABLE_REAL_TIME_ALERTS", True)

    # Cache configuration
    CACHE_TYPE = BaseConfig.get_env("CACHE_TYPE", "simple")
    CACHE_REDIS_URL = BaseConfig.get_env("CACHE_REDIS_URL", "redis://localhost:6379/0")

    # Celery configuration for background tasks
    CELERY_BROKER_URL = BaseConfig.get_env("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND = BaseConfig.get_env("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # External service URLs
    WEATHER_API_URL = BaseConfig.get_env("WEATHER_API_URL", "https://api.weatherservice.com")
    AIR_QUALITY_API_URL = BaseConfig.get_env("AIR_QUALITY_API_URL", "https://api.airqualityservice.com")

    # Default language and localization
    DEFAULT_LANGUAGE = BaseConfig.get_env("DEFAULT_LANGUAGE", "en")
    SUPPORTED_LANGUAGES = BaseConfig.get_list("SUPPORTED_LANGUAGES", ["en", "es", "fr", "de", "zh"])

    # Health data thresholds
    NORMAL_HEART_RATE_MIN = BaseConfig.get_int("NORMAL_HEART_RATE_MIN", 60)
    NORMAL_HEART_RATE_MAX = BaseConfig.get_int("NORMAL_HEART_RATE_MAX", 100)
    NORMAL_BLOOD_PRESSURE_SYSTOLIC_MAX = BaseConfig.get_int("NORMAL_BLOOD_PRESSURE_SYSTOLIC_MAX", 120)
    NORMAL_BLOOD_PRESSURE_DIASTOLIC_MAX = BaseConfig.get_int("NORMAL_BLOOD_PRESSURE_DIASTOLIC_MAX", 80)

    # AI model update frequency (in hours)
    MODEL_UPDATE_FREQUENCY = BaseConfig.get_int("MODEL_UPDATE_FREQUENCY", 24)

    # Data retention policy (in days)
    DATA_RETENTION_PERIOD = BaseConfig.get_int("DATA_RETENTION_PERIOD", 365)

    # Maximum number of health goals per user
    MAX_HEALTH_GOALS = BaseConfig.get_int("MAX_HEALTH_GOALS", 5)

    # Dashboard customization options
    DASHBOARD_LAYOUTS = BaseConfig.get_list("DASHBOARD_LAYOUTS", ["default", "compact", "detailed", "minimal"])
    DEFAULT_DASHBOARD_LAYOUT = BaseConfig.get_env("DEFAULT_DASHBOARD_LAYOUT", "default")

    # Telemedicine integration
    TELEMEDICINE_ENABLED = BaseConfig.get_bool("TELEMEDICINE_ENABLED", True)
    TELEMEDICINE_PROVIDER_URL = BaseConfig.get_env("TELEMEDICINE_PROVIDER_URL", "https://api.telemedicine-provider.com")

    # Emergency contact information
    EMERGENCY_SERVICES_NUMBER = BaseConfig.get_env("EMERGENCY_SERVICES_NUMBER", "911")

    # System maintenance window
    MAINTENANCE_WINDOW_START = BaseConfig.get_env("MAINTENANCE_WINDOW_START", "02:00")
    MAINTENANCE_WINDOW_END = BaseConfig.get_env("MAINTENANCE_WINDOW_END", "04:00")

    # API versioning
    API_VERSION = BaseConfig.get_env("API_VERSION", "v1")

    # Maximum file upload size (in MB)
    MAX_UPLOAD_SIZE_MB = BaseConfig.get_int("MAX_UPLOAD_SIZE_MB", 10)

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

    # Override some settings for production
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    RATE_LIMIT_REQUESTS = 50
    RATE_LIMIT_PERIOD = 3600

def get_config() -> Dict[str, Any]:
    env = os.getenv("FLASK_ENV", "development").lower()
    config_class = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }.get(env, DevelopmentConfig)
    
    return {key: value for key, value in config_class.__dict__.items() 
            if not key.startswith('__') and not callable(value)}

# Set the active configuration
active_config = get_config()

# Validate required environment variables
for key, value in active_config.items():
    if value is None and key in ["DATABASE_URL", "SECRET_KEY", "HUGGINGFACE_TOKEN"]:
        raise ValueError(f"Required configuration {key} is not set.")

# Configure logging
logging.basicConfig(level=getattr(logging, active_config['LOG_LEVEL']))

# Log the active configuration (excluding sensitive information)
sensitive_keys = ['SECRET_KEY', 'DATABASE_URL', 'HUGGINGFACE_TOKEN']
safe_config = {k: v for k, v in active_config.items() if k not in sensitive_keys}
logging.info(f"Active configuration: {safe_config}")
