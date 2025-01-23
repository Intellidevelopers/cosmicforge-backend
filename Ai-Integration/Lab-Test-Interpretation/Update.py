
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

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
from .Config import Config

Base = declarative_base()

class LabTest(Base):
    __tablename__ = 'lab_tests'
    id = Column(Integer, primary_key=True)
    test_name = Column(String, unique=True)
    category = Column(String)
    unit = Column(String)
    low_critical = Column(Float)
    low_normal = Column(Float)
    high_normal = Column(Float)
    high_critical = Column(Float)
    description = Column(Text)
    physiological_significance = Column(Text)
    feedback_entries = relationship("FeedbackEntry", back_populates="lab_test")

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Interpretation(Base):
    __tablename__ = 'interpretations'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('lab_tests.id'))
    range_start = Column(Float)
    range_end = Column(Float)
    interpretation = Column(Text)
    recommendation = Column(Text)
    confidence_score = Column(Float)

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class MedicalGuideline(Base):
    __tablename__ = 'medical_guidelines'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('lab_tests.id'))
    guideline = Column(Text)
    source = Column(String)
    last_updated = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class MedicalContext(Base):
    __tablename__ = 'medical_context'
    test_name = Column(String, primary_key=True)
    description = Column(Text)
    common_interpretations = Column(Text)
    related_conditions = Column(Text)
    last_updated = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class ReferenceRange(Base):
    __tablename__ = 'reference_ranges'
    test_name = Column(String, primary_key=True)
    low = Column(Float)
    high = Column(Float)
    unit = Column(String)
    last_updated = Column(DateTime)

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class FeedbackEntry(Base):
    __tablename__ = 'feedback_entries'
    id = Column(Integer, primary_key=True)
    lab_test_id = Column(Integer, ForeignKey('lab_tests.id'))
    original_interpretation = Column(String)
    corrected_interpretation = Column(String)
    feedback_provider = Column(String)
    feedback_time = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)
    lab_test = relationship("LabTest", back_populates="feedback_entries")

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class LabTestExpansion(Base):
    __tablename__ = 'lab_test_expansions'
    id = Column(Integer, primary_key=True)
    test_name = Column(String, unique=True)
    category = Column(String)
    reference_range = Column(JSON)
    units = Column(String)
    description = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

class TrainingData(Base):
    __tablename__ = 'training_data'
    id = Column(Integer, primary_key=True)
    text = Column(String)
    label = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Database(ABC):
    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def add_test(self, test_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_test_info(self, test_name: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_interpretation(self, interpretation_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_interpretation(self, test_name: str, value: float) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_medical_guideline(self, guideline_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_medical_guideline(self, test_name: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def update_knowledge_base(self, update_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def add_feedback(self, feedback_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_feedback(self, test_name: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def add_lab_test_expansion(self, expansion_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_lab_test_expansion(self, test_name: str) -> Optional[Dict[str, Any]]:
        pass

class PostgreSQLDatabase(Database):
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_connection(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            self.logger.error(f"Database error: {str(e)}")
            raise
        finally:
            session.close()

    def initialize(self) -> None:
        Base.metadata.create_all(self.engine)
        self.logger.info("Database initialized successfully")

    def add_test(self, test_data: Dict[str, Any]) -> None:
        with self.get_connection() as session:
            lab_test = LabTest(**test_data)
            session.add(lab_test)
            self.logger.info(f"Added new lab test: {test_data['test_name']}")

    def get_test_info(self, test_name: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as session:
            lab_test = session.query(LabTest).filter_by(test_name=test_name).first()
            return lab_test.to_dict() if lab_test else None

    def add_interpretation(self, interpretation_data: Dict[str, Any]) -> None:
        with self.get_connection() as session:
            interpretation = Interpretation(**interpretation_data)
            session.add(interpretation)
            self.logger.info(f"Added new interpretation for test ID: {interpretation_data['test_id']}")

    def get_interpretation(self, test_name: str, value: float) -> Optional[Dict[str, Any]]:
        with self.get_connection() as session:
            interpretation = session.query(Interpretation).join(LabTest).filter(
                LabTest.test_name == test_name,
                Interpretation.range_start <= value,
                Interpretation.range_end >= value
            ).first()
            return interpretation.to_dict() if interpretation else None

    def add_medical_guideline(self, guideline_data: Dict[str, Any]) -> None:
        with self.get_connection() as session:
            guideline = MedicalGuideline(**guideline_data)
            session.add(guideline)
            self.logger.info(f"Added new medical guideline for test ID: {guideline_data['test_id']}")

    def get_medical_guideline(self, test_name: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as session:
            guideline = session.query(MedicalGuideline).join(LabTest).filter(
                LabTest.test_name == test_name
            ).first()
            return guideline.to_dict() if guideline else None

    def update_knowledge_base(self, update_data: Dict[str, Any]) -> None:
        with self.get_connection() as session:
            context = MedicalContext(**update_data)
            session.merge(context)
            self.logger.info(f"Updated medical context for test: {update_data['test_name']}")

    def add_feedback(self, feedback_data: Dict[str, Any]) -> None:
        with self.get_connection() as session:
            feedback = FeedbackEntry(**feedback_data)
            session.add(feedback)
            self.logger.info(f"Added new feedback for lab test ID: {feedback_data['lab_test_id']}")

    def get_feedback(self, test_name: str) -> List[Dict[str, Any]]:
        with self.get_connection() as session:
            feedbacks = session.query(FeedbackEntry).join(LabTest).filter(
                LabTest.test_name == test_name
            ).all()
            return [feedback.to_dict() for feedback in feedbacks]

    def add_lab_test_expansion(self, expansion_data: Dict[str, Any]) -> None:
        with self.get_connection() as session:
            expansion = LabTestExpansion(**expansion_data)
            session.add(expansion)
            self.logger.info(f"Added lab test expansion for: {expansion_data['test_name']}")

    def get_lab_test_expansion(self, test_name: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as session:
            expansion = session.query(LabTestExpansion).filter_by(test_name=test_name).first()
            return expansion.to_dict() if expansion else None

# Initialize the database
config = Config()
db_url = config.get_db_url()
database = PostgreSQLDatabase(db_url)
database.initialize()

import numpy as np
import pandas as pd
import torch
import joblib
import json
import logging
import aiohttp
import aiofiles
import asyncio
import os
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import classification_report
from transformers import BertTokenizer, BertModel
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, select, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import fitz  # PyMuPDF
import cv2
import pytesseract
from PIL import Image
import re
import openai
from tenacity import retry, wait_random_exponential, stop_after_attempt

# Import custom modules
from .expanded_input import process_expanded_input
from .ethical_ai_monitoring import ethical_ai_wrapper
from .federated_learning import FederatedLearning, train_federated_model, predict_with_federated_model
from .integrations.automated_alerts import check_critical_results, send_alert
from .integrations.language_support import LanguageProcessor
from .integrations.voice_interface import VoiceInterface
from .features.continuous_learning import ContinuousLearning
from .ai_models.llm import LLMInterpreter
from .config import Config
from .Database import (
    LabTest, Interpretation, MedicalGuideline, MedicalContext, 
    ReferenceRange, FeedbackEntry, LabTestExpansion, Base
)

Base = declarative_base()

class Models:
    def __init__(self):
        self.interpretation_model = None
        self.recommendation_model = None
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.interp_encoder = LabelEncoder()
        self.recom_encoder = LabelEncoder()
        self.feature_names = None
        self.tfidf_vectorizer = TfidfVectorizer()
        self.interpretation_corpus = []
        self.recommendation_corpus = []
        self.vectorized_interpretations = None
        self.vectorized_recommendations = None
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.logger = logging.getLogger(__name__)
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.medical_context = None
        self.unsafe_patterns = None
        self.federated_model = None
        self.local_dataset = []
        self.last_federated_update = asyncio.get_event_loop().time()
        self.federated_update_interval = 3600  # Update every hour, adjust as needed
        self.language_processor = LanguageProcessor()
        self.voice_interface = VoiceInterface()
        self.continuous_learning = ContinuousLearning(self.ensemble_model)
        self.llm_interpreter = LLMInterpreter()
        self.config = Config()

    async def initialize(self):
        engine = create_async_engine(self.config.get_db_url())
        async with engine.begin() as conn:
        self.AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        self.medical_context = await self.load_medical_context()
        self.unsafe_patterns = await self.load_unsafe_patterns()
        asyncio.create_task(self.schedule_lab_test_expansion())
        self.federated_model = await self.initialize_federated_model()
        
        await self.llm_interpreter.initialize()
        await self.schedule_context_update()
        await self.load_models()
        await self.language_processor.initialize()
        await self.voice_interface.initialize()
        await self.continuous_learning.initialize()

    async def load_and_train(self, new_data_path: str, test_size: float = 0.2, random_state: int = 42) -> None:
        try:
            new_data = pd.read_csv(new_data_path)
            self.logger.info(f"Loaded new data from {new_data_path}")

            X, y_interpretation, y_recommendation = await self.preprocess_data(new_data)

            X_train, X_test, y_interp_train, y_interp_test, y_recom_train, y_recom_test = train_test_split(
                X, y_interpretation, y_recommendation, test_size=test_size, random_state=random_state
            )

            await self.train_models(X_train, y_interp_train, y_recom_train)
            await self.evaluate_models(X_test, y_interp_test, y_recom_test)
            await self.save_models()

            self.logger.info("Model training and saving completed successfully")
        except Exception as e:
            self.logger.error(f"Error in load_and_train: {str(e)}")
            raise

    async def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        try:
            X = data['test_result'].values.reshape(-1, 1)
            y_interpretation = data['interpretation'].values
            y_recommendation = data['recommendation'].values

            X = self.imputer.fit_transform(X)
            X = self.scaler.fit_transform(X)

            y_interpretation = self.interp_encoder.fit_transform(y_interpretation)
            y_recommendation = self.recom_encoder.fit_transform(y_recommendation)

            return X, y_interpretation, y_recommendation
        except Exception as e:
            self.logger.error(f"Error in preprocess_data: {str(e)}")
            raise

    async def train_models(self, X_train: np.ndarray, y_interp_train: np.ndarray, y_recom_train: np.ndarray) -> None:
        try:
            self.interpretation_model = GradientBoostingClassifier(random_state=42)
            await asyncio.to_thread(self.interpretation_model.fit, X_train, y_interp_train)

            self.recommendation_model = GradientBoostingClassifier(random_state=42)
            await asyncio.to_thread(self.recommendation_model.fit, X_train, y_recom_train)

            self.logger.info("Models trained successfully")
        except Exception as e:
            self.logger.error(f"Error in train_models: {str(e)}")
            raise

    async def evaluate_models(self, X_test: np.ndarray, y_interp_test: np.ndarray, y_recom_test: np.ndarray) -> None:
        try:
            y_interp_pred = await asyncio.to_thread(self.interpretation_model.predict, X_test)
            interp_report = classification_report(y_interp_test, y_interp_pred, target_names=self.interp_encoder.classes_)
            self.logger.info(f"Interpretation Model Evaluation:\n{interp_report}")

            y_recom_pred = await asyncio.to_thread(self.recommendation_model.predict, X_test)
            recom_report = classification_report(y_recom_test, y_recom_pred, target_names=self.recom_encoder.classes_)
            self.logger.info(f"Recommendation Model Evaluation:\n{recom_report}")
        except Exception as e:
            self.logger.error(f"Error in evaluate_models: {str(e)}")
            raise

    async def save_models(self) -> None:
        try:
            model_path = self.config.MODELS_DIR
            os.makedirs(model_path, exist_ok=True)

            joblib.dump(self.interpretation_model, f"{model_path}/interpretation_model.joblib")
            joblib.dump(self.recommendation_model, f"{model_path}/recommendation_model.joblib")
            joblib.dump(self.imputer, f"{model_path}/imputer.joblib")
            joblib.dump(self.scaler, f"{model_path}/scaler.joblib")
            joblib.dump(self.interp_encoder, f"{model_path}/interp_encoder.joblib")
            joblib.dump(self.recom_encoder, f"{model_path}/recom_encoder.joblib")

            self.logger.info("Models and preprocessing objects saved successfully")
        except Exception as e:
            self.logger.error(f"Error in save_models: {str(e)}")
            raise

    async def load_models(self) -> None:
        try:
            model_path = self.config.MODELS_DIR

            self.interpretation_model = joblib.load(f"{model_path}/interpretation_model.joblib")
            self.recommendation_model = joblib.load(f"{model_path}/recommendation_model.joblib")
            self.imputer = joblib.load(f"{model_path}/imputer.joblib")
            self.scaler = joblib.load(f"{model_path}/scaler.joblib")
            self.interp_encoder = joblib.load(f"{model_path}/interp_encoder.joblib")
            self.recom_encoder = joblib.load(f"{model_path}/recom_encoder.joblib")

            self.logger.info("Models and preprocessing objects loaded successfully")
        except Exception as e:
            self.logger.error(f"Error in load_models: {str(e)}")
            raise

    async def submit_feedback(self, lab_test_id: int, original_interpretation: str, 
                              corrected_interpretation: str, feedback_provider: str) -> None:
        async with self.AsyncSession() as session:
            try:
                feedback_entry = FeedbackEntry(
                    lab_test_id=lab_test_id,
                    original_interpretation=original_interpretation,
                    corrected_interpretation=corrected_interpretation,
                    feedback_provider=feedback_provider,
                    feedback_time=datetime.utcnow(),
                    confidence_score=1.0  # You might want to adjust this
                )
                session.add(feedback_entry)
                await session.commit()
                self.logger.info(f"Feedback submitted successfully for lab test ID: {lab_test_id}")
            except Exception as e:
                await session.rollback()
                self.logger.error(f"Error submitting feedback: {str(e)}")
                raise

    async def initialize_federated_model(self):
        # Initialize federated learning model
        self.federated_model = FederatedLearning(
            model=self.ensemble_model,
            optimizer=torch.optim.Adam,
            loss_fn=torch.nn.CrossEntropyLoss()
        )
        return self.federated_model

    async def update_federated_model(self):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_federated_update >= self.federated_update_interval:
            try:
                # Prepare local data for federated learning
                X, y = self.prepare_data_for_federated_learning(self.local_dataset)
                
                # Update the federated model
                await train_federated_model(self.federated_model, X, y)
                
                # Clear the local dataset after updating
                self.local_dataset.clear()
                
                self.last_federated_update = current_time
                self.logger.info("Federated model updated successfully")
            except Exception as e:
                self.logger.error(f"Error updating federated model: {str(e)}")

    async def predict_with_federated_model(self, features: np.array) -> Tuple[str, str, float]:
        try:
            interpretation, recommendation, confidence = await predict_with_federated_model(self.federated_model, features)
            return interpretation, recommendation, confidence
        except Exception as e:
            self.logger.error(f"Error predicting with federated model: {str(e)}")
            raise

    async def load_medical_context(self) -> Dict[str, Any]:
        async with self.AsyncSession() as session:
            try:
                result = await session.execute(select(MedicalContext))
                contexts = result.scalars().all()
                
                medical_context = {}
                for context in contexts:
                    medical_context[context.test_name] = {
                        'description': context.description,
                        'common_interpretations': json.loads(context.common_interpretations),
                        'related_conditions': json.loads(context.related_conditions),
                        'last_updated': context.last_updated
                    }
                
                return medical_context
            except Exception as e:
                self.logger.error(f"Error loading medical context: {str(e)}")
                raise

    async def load_unsafe_patterns(self) -> Dict[str, Any]:
        return self.config.get_unsafe_patterns()

    async def schedule_lab_test_expansion(self):
        while True:
            await self.expand_lab_tests()
            await asyncio.sleep(self.config.LAB_TEST_EXPANSION_INTERVAL)

    async def expand_lab_tests(self):
        try:
            async with self.AsyncSession() as session:
                result = await session.execute(select(LabTest))
                lab_tests = result.scalars().all()
                
                for lab_test in lab_tests:
                    expanded_info = await self.get_expanded_info(lab_test.test_name)
                    
                    expansion = LabTestExpansion(
                        test_name=lab_test.test_name,
                        category=expanded_info.get('category', ''),
                        reference_range=json.dumps(expanded_info.get('reference_range', {})),
                        units=expanded_info.get('units', ''),
                        description=expanded_info.get('description', ''),
                        last_updated=datetime.utcnow()
                    )
                    
                    session.add(expansion)
                
                await session.commit()
            self.logger.info("Lab test expansion completed successfully")
        except Exception as e:
            self.logger.error(f"Error in lab test expansion: {str(e)}")

    async def get_expanded_info(self, test_name: str) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.MEDICAL_API_URL}/lab_test_info/{test_name}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Failed to get expanded info for {test_name}")
                        return {}
        except Exception as e:
            self.logger.error(f"Error getting expanded info for {test_name}: {str(e)}")
            return {}

    async def schedule_context_update(self):
        while True:
            await self.update_medical_context()
            await asyncio.sleep(self.config.MEDICAL_CONTEXT_UPDATE_INTERVAL)

    async def update_medical_context(self):
        try:
            async with self.AsyncSession() as session:
                for test_name, context in self.medical_context.items():
                    updated_context = await self.get_updated_context(test_name)
                    
                    medical_context = MedicalContext(
                        test_name=test_name,
                        description=updated_context['description'],
                        common_interpretations=json.dumps(updated_context['common_interpretations']),
                        related_conditions=json.dumps(updated_context['related_conditions']),
                        last_updated=datetime.utcnow()
                    )
                    
                    session.add(medical_context)
                
                await session.commit()
            self.logger.info("Medical context updated successfully")
        except Exception as e:
            self.logger.error(f"Error updating medical context: {str(e)}")

    async def get_updated_context(self, test_name: str) -> Dict[str, Any]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.config.MEDICAL_API_URL}/medical_context/{test_name}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Failed to get updated context for {test_name}")
                        return {}
        except Exception as e:
            self.logger.error(f"Error getting updated context for {test_name}: {str(e)}")
            return {}

def ensemble_model(self, features: np.array) -> Tuple[str, str, float]:
    try:
        # Get predictions from multiple models
        models = [
            self.predict,
            self.predict_with_federated_model,
            self.predict_with_llm,
            self.predict_with_rule_based
        ]
        
        interpretations = []
        recommendations = []
        confidences = []
        
        for model in models:
            interp, rec, conf = model(features)
            interpretations.append(interp)
            recommendations.append(rec)
            confidences.append(conf)
        
        # Calibrate confidences
        calibrated_confidences = self.calibrate_confidences(confidences)
        
        # Weight the predictions based on calibrated confidences
        weighted_interp = self.weighted_mode(interpretations, calibrated_confidences)
        weighted_rec = self.weighted_mode(recommendations, calibrated_confidences)
        
        # Combine confidences using a reliability metric
        final_conf = self.combine_confidences(calibrated_confidences)
        
        # Apply domain-specific rules
        final_interp, final_rec, final_conf = self.apply_domain_rules(
            weighted_interp, weighted_rec, final_conf, features
        )
        
        # Log the ensemble decision for future analysis
        self.log_ensemble_decision(features, interpretations, recommendations, 
                                   confidences, final_interp, final_rec, final_conf)
        
        return final_interp, final_rec, final_conf
    
    except Exception as e:
        self.logger.error(f"Error in ensemble_model: {str(e)}")
        raise

def calibrate_confidences(self, confidences: List[float]) -> List[float]:
    try:
        # Use historical data to calibrate confidences
        historical_features = self.get_historical_features()
        historical_labels = self.get_historical_labels()
        
        calibrated_confidences = []
        for i, conf in enumerate(confidences):
            calibrator = CalibratedClassifierCV(base_estimator=self.models[i], cv='prefit')
            calibrator.fit(historical_features, historical_labels)
            calibrated_conf = calibrator.predict_proba(features)[:, 1]
            calibrated_confidences.append(calibrated_conf[0])
        
        return calibrated_confidences
    except Exception as e:
        self.logger.error(f"Error in calibrate_confidences: {str(e)}")
        raise

def weighted_mode(self, predictions: List[str], weights: List[float]) -> str:
    try:
        unique_predictions = list(set(predictions))
        weighted_counts = {pred: sum(weights[i] for i, p in enumerate(predictions) if p == pred)
                           for pred in unique_predictions}
        return max(weighted_counts, key=weighted_counts.get)
    except Exception as e:
        self.logger.error(f"Error in weighted_mode: {str(e)}")
        raise

def combine_confidences(self, confidences: List[float]) -> float:
    try:
        # Use Brier score as a reliability metric
        historical_probs = self.get_historical_probabilities()
        historical_outcomes = self.get_historical_outcomes()
        
        brier_scores = [brier_score_loss(historical_outcomes, probs) for probs in historical_probs]
        reliability_weights = [1 / (score + 1e-8) for score in br
        
        

import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import json
import csv
import xml.etree.ElementTree as ET
import logging

class OutputFormatter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def to_plain_text(self, interpretations: Dict[str, Dict[str, Any]]) -> str:
        try:
            output = ""
            for test, data in interpretations.items():
                output += f"{test}:\n"
                output += f"Value: {data.get('value', 'N/A')}\n"
                output += f"Status: {data.get('status', 'N/A')}\n"
                output += f"Interpretation: {data.get('interpretation', 'N/A')}\n"
                output += f"Recommendation: {data.get('recommendation', 'N/A')}\n\n"
            return output
        except Exception as e:
            self.logger.error(f"Error in to_plain_text: {str(e)}")
            raise

    def to_html(self, interpretations: Dict[str, Dict[str, Any]]) -> str:
        try:
            html = "<html><body>"
            for test, data in interpretations.items():
                html += f"<h2>{test}</h2>"
                html += f"<p><strong>Value:</strong> {data.get('value', 'N/A')}</p>"
                html += f"<p><strong>Status:</strong> {data.get('status', 'N/A')}</p>"
                html += f"<p><strong>Interpretation:</strong> {data.get('interpretation', 'N/A')}</p>"
                html += f"<p><strong>Recommendation:</strong> {data.get('recommendation', 'N/A')}</p>"
            html += "</body></html>"
            return html
        except Exception as e:
            self.logger.error(f"Error in to_html: {str(e)}")
            raise

    def to_pdf(self, interpretations: Dict[str, Dict[str, Any]], output_path: str, patient_info: Dict[str, str]):
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            story = []
            styles = getSampleStyleSheet()
            styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceBefore=12, spaceAfter=6))
            styles.add(ParagraphStyle(name='BodyText', fontSize=11, spaceBefore=6, spaceAfter=6))

            story.append(Paragraph("Lab Test Results Report", styles['Heading1']))
            story.append(Spacer(1, 12))

            patient_data = [
                ["Patient Name:", patient_info.get('name', 'N/A')],
                ["Age:", patient_info.get('age', 'N/A')],
                ["Gender:", patient_info.get('gender', 'N/A')],
                ["Date of Report:", patient_info.get('report_date', 'N/A')]
            ]
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 12))

            for test_name, data in interpretations.items():
                story.append(Paragraph(test_name, styles['Heading2']))
                story.append(Paragraph(f"Value: {data.get('value', 'N/A')}", styles['BodyText']))
                story.append(Paragraph(f"Status: {data.get('status', 'N/A')}", styles['BodyText']))
                story.append(Paragraph("Interpretation:", styles['BodyText']))
                story.append(Paragraph(data.get('interpretation', 'N/A'), styles['BodyText']))
                story.append(Paragraph("Recommendation:", styles['BodyText']))
                story.append(Paragraph(data.get('recommendation', 'N/A'), styles['BodyText']))
                story.append(Spacer(1, 12))

            disclaimer = ("This report is generated by an AI system and should not replace professional medical advice. "
                          "Always consult with your healthcare provider for a comprehensive interpretation of your test "
                          "results and appropriate medical care.")
            story.append(Paragraph(disclaimer, ParagraphStyle(name='Disclaimer', fontSize=8, textColor=colors.grey)))

            doc.build(story)

            pdf = buffer.getvalue()
            buffer.close()
            with open(output_path, 'wb') as f:
                f.write(pdf)
            
            self.logger.info(f"PDF report generated successfully: {output_path}")
        except Exception as e:
            self.logger.error(f"Error in to_pdf: {str(e)}")
            raise

    def to_json(self, interpretations: Dict[str, Dict[str, Any]]) -> str:
        try:
            return json.dumps(interpretations, indent=2)
        except Exception as e:
            self.logger.error(f"Error in to_json: {str(e)}")
            raise

    def to_csv(self, interpretations: Dict[str, Dict[str, Any]], output_path: str):
        try:
            with open(output_path, 'w', newline='') as csvfile:
                fieldnames = ['Test', 'Value', 'Status', 'Interpretation', 'Recommendation']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for test, data in interpretations.items():
                    writer.writerow({
                        'Test': test,
                        'Value': data.get('value', 'N/A'),
                        'Status': data.get('status', 'N/A'),
                        'Interpretation': data.get('interpretation', 'N/A'),
                        'Recommendation': data.get('recommendation', 'N/A')
                    })
            self.logger.info(f"CSV report generated successfully: {output_path}")
        except Exception as e:
            self.logger.error(f"Error in to_csv: {str(e)}")
            raise

    def to_xml(self, interpretations: Dict[str, Dict[str, Any]]) -> str:
        try:
            root = ET.Element("lab_results")
            for test, data in interpretations.items():
                test_elem = ET.SubElement(root, "test")
                ET.SubElement(test_elem, "name").text = test
                ET.SubElement(test_elem, "value").text = str(data.get('value', 'N/A'))
                ET.SubElement(test_elem, "status").text = data.get('status', 'N/A')
                ET.SubElement(test_elem, "interpretation").text = data.get('interpretation', 'N/A')
                ET.SubElement(test_elem, "recommendation").text = data.get('recommendation', 'N/A')
            return ET.tostring(root, encoding='unicode', method='xml')
        except Exception as e:
            self.logger.error(f"Error in to_xml: {str(e)}")
            raise

import os
import json
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

from .AILabInterpreter import AILabInterpreter
from .Database import PostgreSQLDatabase
from .Config import Config
from .OutputFormatter import OutputFormatter

app = Flask(__name__)
load_dotenv()

class LabReportAPI:
    def __init__(self, interpreter: AILabInterpreter, database: PostgreSQLDatabase):
        self.interpreter = interpreter
        self.database = database
        self.app = app
        self.output_formatter = OutputFormatter()
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/interpret', methods=['POST'])
        async def interpret_report():
            try:
                data = await request.get_json()
                lab_results = data['lab_results']
                patient_info = data['patient_info']
                patient_id = patient_info.get('id')
                use_voice = data.get('use_voice', False)
                target_lang = data.get('target_lang', 'en')

                if not patient_id:
                    return jsonify({'error': 'Patient ID is required'}), 400

                interpretations = await self.interpreter.interpret_lab_results(lab_results, patient_id, use_voice, target_lang)
                
                if use_voice:
                    audio_file = await self.interpreter.voice_interface.text_to_speech(interpretations['interpretation'])
                    return send_file(audio_file, mimetype='audio/mp3')
                else:
                    return jsonify(interpretations)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/update_guidelines', methods=['POST'])
        async def update_guidelines():
            try:
                await self.interpreter.update_medical_guidelines()
                return jsonify({"message": "Guidelines updated successfully"})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/explain', methods=['GET'])
        async def explain_interpretation():
            try:
                test_name = request.args.get('test_name')
                interpretation = request.args.get('interpretation')
                explanation = await self.interpreter.explain_interpretation(test_name, interpretation)
                return jsonify({"explanation": explanation})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/submit_feedback', methods=['POST'])
        async def submit_feedback():
            try:
                data = await request.get_json()
                await self.interpreter.submit_feedback(
                    data['lab_test_id'],
                    data['original_interpretation'],
                    data['corrected_interpretation'],
                    data['feedback_provider']
                )
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/voice_input', methods=['POST'])
        async def voice_input():
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file part'}), 400
                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No selected file'}), 400
                if file and self.allowed_file(file.filename, {'wav', 'mp3'}):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    text = await self.interpreter.voice_interface.speech_to_text(filepath)
                    os.remove(filepath)  # Clean up the uploaded file
                    
                    return jsonify({'text': text})
                return jsonify({'error': 'Invalid file type'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/expert_feedback', methods=['POST'])
        async def expert_feedback():
            try:
                data = await request.get_json()
                text = data['text']
                expert_interpretation = data['expert_interpretation']

                result = await self.interpreter.handle_expert_feedback(text, expert_interpretation)
                return jsonify(result)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/generate_report', methods=['POST'])
        async def generate_report():
            try:
                data = await request.get_json()
                interpretations = data['interpretations']
                patient_info = data['patient_info']
                report_format = data.get('format', 'pdf')

                if report_format == 'pdf':
                    pdf_path = 'temp_report.pdf'
                    self.output_formatter.to_pdf(interpretations, pdf_path, patient_info)
                    return send_file(pdf_path, as_attachment=True, attachment_filename='lab_report.pdf')
                elif report_format == 'html':
                    html_content = self.output_formatter.to_html(interpretations)
                    return html_content
                elif report_format == 'json':
                    return jsonify(interpretations)
                else:
                    return jsonify({'error': 'Unsupported report format'}), 400
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def allowed_file(self, filename, allowed_extensions):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

    async def start(self):
        self.app.run(host='0.0.0.0', port=5000)

async def main():
    # Load environment variables
    load_dotenv()

    # Initialize the config
    config = Config()

    # Initialize the database
    database = PostgreSQLDatabase(config.get_db_url())
    await database.initialize()

    # Initialize the interpreter
    interpreter = AILabInterpreter(config, database)
    await interpreter.initialize()

    # Train the interpreter (if needed)
    await interpreter.train(os.getenv('TRAINING_DATA_PATH'))

    # Save the trained models
    await interpreter.save_models(os.getenv('MODELS_DIR'))

    # Update medical guidelines
    await interpreter.update_medical_guidelines()

    # Process a sample lab report
    lab_report = {
        "patient_info": {
            "id": "12345",
            "name": "John Doe",
            "age": 45,
            "gender": "Male",
            "medical_history": ["hypertension", "type 2 diabetes"]
        },
        "results": {
            "Complete Blood Count": 7.5,
            "Lipid Panel": 220
        }
    }

    interpretations = await interpreter.interpret_lab_results(lab_report['results'], lab_report['patient_info']['id'])
    print("Lab Report Interpretations:")
    print(json.dumps(interpretations, indent=2))

    # Generate a narrative report
    report = await interpreter.generate_narrative_report(interpretations, lab_report["patient_info"])
    print("\nNarrative Report:")
    print(report)

    # Initialize and run the API
    api = LabReportAPI(interpreter, database)
    await api.start()

if __name__ == "__main__":
    asyncio.run(main())

import os
import re
import json
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import requests
import aiohttp
import asyncio
import joblib
import openai
import torch
import torch.nn as nn
import cv2
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
from nltk.tokenize import sent_tokenize
from profanity_check import predict as predict_profanity
from sqlalchemy import create_engine, Column, String, DateTime, Text, Float, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
import boto3
from botocore.exceptions import ClientError
from cachetools import TTLCache
from tenacity import retry, stop_after_attempt, wait_random_exponential
from jinja2 import Environment, FileSystemLoader

import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import spacy
import nltk

from expanded_input import process_expanded_input
from ethical_ai_monitoring import ethical_ai_wrapper
from federated_learning import train_federated_model, predict_with_federated_model
from typing import Dict, Any, List
import logging

from models import Base, LabTest, Interpretation, MedicalGuideline, MedicalContext, ReferenceRange, FeedbackEntry, LabTestExpansion
from ai_models import EnsembleModel, ExplainableAI
from data_processing import preprocess_text, extract_lab_results
from report_generation import generate_report

from integrations.automated_alerts import check_critical_results, send_alert
from integrations.language_support import LanguageProcessor
from integrations.voice_interface import VoiceInterface
from features.continuous_learning import ContinuousLearning
from ai_models.llm import LLMInterpreter

from .model_utils import load_model, save_model, load_initial_data
from .models import TrainingData
from .federated_learning import FederatedLearning, EnsembleModel, prepare_data_for_federated_learning

import aiofiles

from dotenv import load_dotenv

load_dotenv()

class AILabInterpreter:
    def __init__(self):
        # Database setup
        db_url = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_async_engine(db_url)
        self.AsyncSession = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

        # Redis setup
        self.redis_conn = Redis.from_url(os.getenv('REDIS_URL'))
        self.task_queue = Queue(connection=self.redis_conn)
        self.scheduler = Scheduler(queue=self.task_queue, connection=self.redis_conn)

        # AWS setup
        self.s3 = boto3.client('s3', 
                               aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                               aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
                               region_name=os.getenv('AWS_REGION'))

        # OpenAI setup
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.base_delay = float(os.getenv('BASE_DELAY', 1))
        self.max_delay = float(os.getenv('MAX_DELAY', 60))

        # API and template setup
        self.medical_api_url = os.getenv('MEDICAL_API_URL')
        self.jinja_env = Environment(loader=FileSystemLoader(os.getenv('TEMPLATE_DIR')))

        # Caching setup
        self.reference_range_cache = TTLCache(maxsize=1000, ttl=3600)  # Cache for 1 hour
        self.interpretation_cache = TTLCache(maxsize=10000, ttl=86400)  # Cache for 24 hours

        # Concurrency control
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent API calls

        # Logging setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # ML model attributes
        self.interpretation_model = None
        self.recommendation_model = None
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='mean')
        self.label_encoder = LabelEncoder()
        self.feature_names = None
        self.tfidf_vectorizer = TfidfVectorizer()
        self.interpretation_corpus = []
        self.recommendation_corpus = []
        self.vectorized_interpretations = None
        self.vectorized_recommendations = None
        self.federated_model = None

        self.language_processor = LanguageProcessor()
        self.voice_interface = VoiceInterface()
        self.continuous_learning = ContinuousLearning(self.ensemble_model)
        self.llm_interpreter = LLMInterpreter()
        
        self.imputer = None
        self.scaler = None
        self.interp_encoder = None
        self.recom_encoder = None
        self.loop = asyncio.get_event_loop()
        
        # BERT model setup
        self.bert_model = None
        self.bert_tokenizer = None

        # Load pre-trained BERT model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModel.from_pretrained('bert-base-uncased')
        
        # Load spaCy model for named entity recognition
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize NLTK components
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

        # Other attributes
        self.medical_context = None
        self.unsafe_patterns = None
        self.update_interval = timedelta(hours=24)
        self.common_units = {
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

    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self.medical_context = await self.load_medical_context()
        self.unsafe_patterns = await self.load_unsafe_patterns()
        self.loop.create_task(self.schedule_lab_test_expansion())
        self.federated_model = await self.initialize_federated_model()
        self.local_dataset = []
        self.last_federated_update = asyncio.get_event_loop().time()
        self.federated_update_interval = 3600  # Update every hour, adjust as needed
        self.llm_interpreter = LLMInterpreter()
        
        await self.llm_interpreter.initialize()
        await self.schedule_context_update()
        await self.load_models()
        await self.initialize_federated_model()
        await self.language_processor.initialize()
        await self.voice_interface.initialize()
        await self.continuous_learning.initialize()

    async def load_medical_context(self) -> Dict[str, Any]:
        try:
            async with self.AsyncSession() as session:
                result = await session.execute(select(MedicalContext))
                contexts = result.scalars().all()
            
            medical_context = {}
            for context in contexts:
                medical_context[context.test_name] = {
                    'description': context.description,
                    'common_interpretations': json.loads(context.common_interpretations),
                    'related_conditions': json.loads(context.related_conditions),
                    'last_updated': context.last_updated
                }
            
            if not medical_context or (datetime.now() - contexts[0].last_updated) > self.update_interval:
                await self.update_medical_context()
            
            return medical_context
        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading medical context: {e}")
            return {}

    async def update_medical_context(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.medical_api_url}/medical-context') as response:
                if response.status == 200:
                    new_data = await response.json()
                    
                    async with self.AsyncSession() as db_session:
                        try:
                            for test, data in new_data.items():
                                context = MedicalContext(
                                    test_name=test,
                                    description=data['description'],
                                    common_interpretations=json.dumps(data['common_interpretations']),
                                    related_conditions=json.dumps(data['related_conditions']),
                                    last_updated=datetime.now()
                                )
                                db_session.merge(context)
                            await db_session.commit()
                        except SQLAlchemyError as e:
                            self.logger.error(f"Database error during update: {e}")
                            await db_session.rollback()
                else:
                    self.logger.error(f"Failed to fetch medical context. Status: {response.status}")

    async def schedule_context_update(self):
        self.scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=self.update_medical_context,
            interval=self.update_interval.total_seconds()
        )

    async def load_unsafe_patterns(self) -> Dict[str, Any]:
        try:
            response = await self.s3.get_object_async(Bucket='your-bucket', Key='unsafe_patterns.json')
            unsafe_patterns = json.loads(await response['Body'].read())
            return unsafe_patterns
        except Exception as e:
            self.logger.error(f"Error loading unsafe patterns from S3: {e}")
            return {
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

    async def post_process_explanation(self, explanation: str, test_name: str) -> str:
        tasks = [
            self.remove_unsafe_content(explanation),
            self.check_sensitive_topics(explanation),
            self.check_profanity(explanation),
            self.add_context_information(explanation, test_name),
            self.add_disclaimer()
        ]
        results = await asyncio.gather(*tasks)
        
        return ''.join(results)

    async def remove_unsafe_content(self, explanation: str) -> str:
        for phrase in self.unsafe_patterns['disclaimer_phrases']:
            explanation = explanation.split(phrase)[0] if phrase in explanation else explanation
        return explanation

    async def check_sensitive_topics(self, explanation: str) -> str:
        for topic in self.unsafe_patterns['sensitive_topics']:
            if topic.lower() in explanation.lower():
                return f"{explanation}\n\nThis explanation contains information about {topic}. " \
                       f"Please consult with your healthcare provider for more information."
        return explanation

    async def check_profanity(self, explanation: str) -> str:
        if predict_profanity([explanation])[0] > self.unsafe_patterns['profanity_threshold']:
            return "We apologize, but we couldn't generate an appropriate explanation. " \
                   "Please consult with your healthcare provider for information about your test results."
        return explanation

    async def add_context_information(self, explanation: str, test_name: str) -> str:
        if test_name in self.medical_context:
            context = self.medical_context[test_name]
            additional_info = f"\n\nAdditional information about {test_name}:\n"
            additional_info += f"- {context['description']}\n"
            additional_info += "- Common related conditions: " + ", ".join(json.loads(context['related_conditions']))
            return explanation + additional_info
        return explanation

    async def add_disclaimer(self) -> str:
        return ("\n\nPlease note: This explanation is generated by an AI system and should not "
                "replace professional medical advice. Always consult with your healthcare provider "
                "for a comprehensive interpretation of your test results and appropriate medical care.")

    async def post_process_interpretation(self, interpretation: str, test_name: str, value: float, reference_range: Dict[str, float]) -> str:
        if value < reference_range['low']:
            summary = f"Your {test_name} result of {value} {reference_range['unit']} is below the reference range of {reference_range['low']} - {reference_range['high']} {reference_range['unit']}."
        elif value > reference_range['high']:
            summary = f"Your {test_name} result of {value} {reference_range['unit']} is above the reference range of {reference_range['low']} - {reference_range['high']} {reference_range['unit']}."
        else:
            summary = f"Your {test_name} result of {value} {reference_range['unit']} is within the reference range of {reference_range['low']} - {reference_range['high']} {reference_range['unit']}."

        interpretation = summary + "\n\n" + interpretation

        max_length = 1000
        if len(interpretation) > max_length:
            interpretation = interpretation[:max_length] + "... (truncated for brevity)"

        disclaimer = ("\n\nPlease note: This interpretation is generated by an AI system and should not "
                      "replace professional medical advice. Always consult with your healthcare provider "
                      "for a comprehensive interpretation of your test results and appropriate medical care.")
        interpretation += disclaimer

        return interpretation

    async def process_lab_report(self, lab_report: Dict[str, Any]) -> Dict[str, Any]:
        interpretations = {}
        
        async def process_test(test_name: str, value: float, patient_info: Dict[str, Any]):
            interpretation = await self.interpret_lab_result(test_name, value, patient_info)
            processed_interpretation = await self.post_process_explanation(interpretation, test_name)
            return test_name, processed_interpretation
        
        tasks = [process_test(test, value, lab_report['patient_info']) 
                 for test, value in lab_report['results'].items()]
        
        results = await asyncio.gather(*tasks)
        
        for test_name, interpretation in results:
            interpretations[test_name] = interpretation
        
        return interpretations

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(3))
    async def call_gpt4(self, prompt: str) -> str:
        async with self.semaphore:
            try:
                response = await openai.ChatCompletion.acreate(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a highly knowledgeable medical AI assistant, capable of interpreting lab results with precision and clarity."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    n=1,
                    temperature=0.2,
                    api_key=self.openai_api_key
                )
                return response.choices[0].message['content'].strip()
            except openai.error.RateLimitError:
                await asyncio.sleep(20)
                raise
            except openai.error.APIError as e:
                self.logger.error(f"OpenAI API error: {str(e)}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in GPT-4 call: {str(e)}")
                raise

        async def get_reference_range(self, test_name: str) -> Dict[str, float]:
        if test_name in self.reference_range_cache:
            return self.reference_range_cache[test_name]

        async with self.AsyncSession() as session:
            result = await session.execute(select(ReferenceRange).filter_by(test_name=test_name))
            range_data = result.scalar_one_or_none()

        if range_data:
            reference_range = {
                'low': range_data.low,
                'high': range_data.high,
                'unit': range_data.unit
            }
            self.reference_range_cache[test_name] = reference_range
            return reference_range
        else:
            self.logger.warning(f"Reference range not found for {test_name}")
            return None
            
     async def interpret_lab_results(self, lab_results: Dict[str, Any], patient_info: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Generate a unique cache key
        cache_key = f"{json.dumps(lab_results, sort_keys=True)}_{json.dumps(patient_info, sort_keys=True)}"

        # Check if the interpretation is already in the cache
        if cache_key in self.interpretation_cache:
            return self.interpretation_cache[cache_key]

        # Preprocess the lab results and patient info
        processed_data = await self.preprocess_data(lab_results, patient_info)

        # Get interpretations from other models
        ensemble_interpretation = await self.ensemble_model.predict(processed_data)
        nn_interpretation = await self.interpretation_model.predict(processed_data)
        federated_interpretation = await self.federated_model.predict(processed_data)
        nlp_interpretation = await self.nlp_model.analyze(processed_data)

        # Combine interpretations
        combined_interpretation = {
            "ensemble": ensemble_interpretation,
            "neural_network": nn_interpretation,
            "federated": federated_interpretation,
            "nlp": nlp_interpretation
        }

        # Get historical results if available
        historical_results = await self.get_historical_results(patient_info)

        # Use LLMInterpreter to process lab results
        llm_result = await self.llm_interpreter.process_lab_results(lab_results, patient_info, historical_results)

        # Combine all results
        final_result = {
            "lab_results": lab_results,
            "model_interpretations": combined_interpretation,
            "llm_interpretation": llm_result["enhanced_interpretation"],
            "patient_friendly_explanation": llm_result