# Standard library imports
import os
import re
import json
import logging
from logging.handlers import RotatingFileHandler
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

# Third-party library imports
from scipy import stats
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
from flask import Flask, request, jsonify
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

import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch

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

# Import existing components
from models import Base, LabTest, Interpretation, MedicalGuideline, MedicalContext, ReferenceRange, FeedbackEntry, LabTestExpansion
from ai_models import EnsembleModel, ExplainableAI
from data_processing import preprocess_text, extract_lab_results
from report_generation import generate_report

# Import new components
from integrations.automated_alerts import check_critical_results, send_alert
from integrations.language_support import LanguageProcessor
from integrations.voice_interface import VoiceInterface
from features.continuous_learning import ContinuousLearning

from .model_utils import load_model, save_model, load_initial_data
from .models import TrainingData
from typing import Optional
from .federated_learning import FederatedLearning, EnsembleModel, prepare_data_for_federated_learning

import aiofiles

from dotenv import load_dotenv

Base = declarative_base()

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', '/tmp/uploads')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define SQLAlchemy ORM models
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

    def to_dict(self):
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

class MedicalGuideline(Base):
    __tablename__ = 'medical_guidelines'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('lab_tests.id'))
    guideline = Column(Text)
    source = Column(String)
    last_updated = Column(DateTime)

class MedicalContext(Base):
    __tablename__ = 'medical_context'
    test_name = Column(String, primary_key=True)
    description = Column(Text)
    common_interpretations = Column(Text)
    related_conditions = Column(Text)
    last_updated = Column(DateTime)

class ReferenceRange(Base):
    __tablename__ = 'reference_ranges'
    test_name = Column(String, primary_key=True)
    low = Column(Float)
    high = Column(Float)
    unit = Column(String)
    last_updated = Column(String)

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


class LabTestExpansion(Base):
    __tablename__ = 'lab_test_expansions'

    id = Column(Integer, primary_key=True)
    test_name = Column(String, unique=True)
    category = Column(String)
    reference_range = Column(JSON)
    units = Column(String)
    description = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)

class Database(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def add_test(self, test_data: Dict[str, Any]):
        pass

    @abstractmethod
    def get_test_info(self, test_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def add_interpretation(self, interpretation_data: Dict[str, Any]):
        pass

    @abstractmethod
    def get_interpretation(self, test_name: str, value: float) -> Dict[str, Any]:
        pass

    @abstractmethod
    def add_medical_guideline(self, guideline_data: Dict[str, Any]):
        pass

    @abstractmethod
    def get_medical_guideline(self, test_name: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def update_knowledge_base(self, update_data: Dict[str, Any]):
        pass

class PostgreSQLDatabase(Database):
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    @contextmanager
    def get_connection(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def initialize(self):
        with self.get_connection() as session:
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS lab_tests (
                    id SERIAL PRIMARY KEY,
                    test_name TEXT UNIQUE,
                    category TEXT,
                    unit TEXT,
                    low_critical REAL,
                    low_normal REAL,
                    high_normal REAL,
                    high_critical REAL,
                    description TEXT,
                    physiological_significance TEXT
                )
            """))
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS interpretations (
                    id SERIAL PRIMARY KEY,
                    test_id INTEGER,
                    range_start REAL,
                    range_end REAL,
                    interpretation TEXT,
                    recommendation TEXT,
                    confidence_score REAL,
                    FOREIGN KEY (test_id) REFERENCES lab_tests (id)
                )
            """))
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS medical_guidelines (
                    id SERIAL PRIMARY KEY,
                    test_id INTEGER,
                    guideline TEXT,
                    source TEXT,
                    last_updated DATE,
                    FOREIGN KEY (test_id) REFERENCES lab_tests (id)
                )
            """))
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id SERIAL PRIMARY KEY,
                    topic TEXT,
                    content TEXT,
                    source TEXT,
                    last_updated DATE
                )
            """))

    def add_test(self, test_data: Dict[str, Any]):
        with self.get_connection() as session:
            session.execute(text("""
                INSERT INTO lab_tests 
                (test_name, category, unit, low_critical, low_normal, high_normal, high_critical, description, physiological_significance)
                VALUES (:test_name, :category, :unit, :low_critical, :low_normal, :high_normal, :high_critical, :description, :physiological_significance)
                ON CONFLICT (test_name) DO UPDATE SET
                category = EXCLUDED.category,
                unit = EXCLUDED.unit,
                low_critical = EXCLUDED.low_critical,
                low_normal = EXCLUDED.low_normal,
                high_normal = EXCLUDED.high_normal,
                high_critical = EXCLUDED.high_critical,
                description = EXCLUDED.description,
                physiological_significance = EXCLUDED.physiological_significance
            """), test_data)

    def get_test_info(self, test_name: str) -> Dict[str, Any]:
        with self.get_connection() as session:
            result = session.execute(text("SELECT * FROM lab_tests WHERE test_name = :test_name"), {"test_name": test_name}).fetchone()
            if result:
                return {
                    'id': result[0],
                    'test_name': result[1],
                    'category': result[2],
                    'unit': result[3],
                    'low_critical': result[4],
                    'low_normal': result[5],
                    'high_normal': result[6],
                    'high_critical': result[7],
                    'description': result[8],
                    'physiological_significance': result[9]
                }
            return None

    def add_interpretation(self, interpretation_data: Dict[str, Any]):
        with self.get_connection() as session:
            test_id = session.execute(text("SELECT id FROM lab_tests WHERE test_name = :test_name"), 
                                      {"test_name": interpretation_data['test_name']}).scalar()
            session.execute(text("""
                INSERT INTO interpretations 
                (test_id, range_start, range_end, interpretation, recommendation, confidence_score)
                VALUES (:test_id, :range_start, :range_end, :interpretation, :recommendation, :confidence_score)
            """), {**interpretation_data, 'test_id': test_id})

    def get_interpretation(self, test_name: str, value: float) -> Dict[str, Any]:
        with self.get_connection() as session:
            result = session.execute(text("""
                SELECT i.interpretation, i.recommendation, i.confidence_score
                FROM interpretations i
                JOIN lab_tests t ON i.test_id = t.id
                WHERE t.test_name = :test_name AND :value BETWEEN i.range_start AND i.range_end
            """), {"test_name": test_name, "value": value}).fetchone()
            if result:
                return {'interpretation': result[0], 'recommendation': result[1], 'confidence_score': result[2]}
            return None

    def add_medical_guideline(self, guideline_data: Dict[str, Any]):
        with self.get_connection() as session:
            test_id = session.execute(text("SELECT id FROM lab_tests WHERE test_name = :test_name"), 
                                      {"test_name": guideline_data['test_name']}).scalar()
            session.execute(text("""
                INSERT INTO medical_guidelines 
                (test_id, guideline, source, last_updated)
                VALUES (:test_id, :guideline, :source, :last_updated)
            """), {**guideline_data, 'test_id': test_id})

    def get_medical_guideline(self, test_name: str) -> Dict[str, Any]:
        with self.get_connection() as session:
            result = session.execute(text("""
                SELECT g.guideline, g.source, g.last_updated
                FROM medical_guidelines g
                JOIN lab_tests t ON g.test_id = t.id
                WHERE t.test_name = :test_name
            """), {"test_name": test_name}).fetchone()
            if result:
                return {'guideline': result[0], 'source': result[1], 'last_updated': result[2]}
            return None

    def update_knowledge_base(self, update_data: Dict[str, Any]):
        with self.get_connection() as session:
            session.execute(text("""
                INSERT INTO knowledge_base 
                (topic, content, source, last_updated)
                VALUES (:topic, :content, :source, :last_updated)
                ON CONFLICT (topic) DO UPDATE SET
                content = EXCLUDED.content,
                source = EXCLUDED.source,
                last_updated = EXCLUDED.last_updated
            """), update_data)


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

    async def interpret_lab_result(self, test_name: str, value: float, patient_info: Dict[str, Any]) -> str:
        # Generate a unique key for this interpretation request
        cache_key = f"{test_name}_{value}_{json.dumps(patient_info, sort_keys=True)}"

        # Check if the interpretation is already in the cache
        if cache_key in self.interpretation_cache:
            return self.interpretation_cache[cache_key]

        try:
            reference_range = await self.get_reference_range(test_name)
            
            age = patient_info.get('age', 'unknown age')
            gender = patient_info.get('gender', 'unknown gender')
            medical_history = ", ".join(patient_info.get('medical_history', ['No known medical history']))

            prompt = f"""As a medical professional, interpret the following lab test result:

Test Name: {test_name}
Test Value: {value} {reference_range['unit']}
Reference Range: {reference_range['low']} - {reference_range['high']} {reference_range['unit']}

Patient Information:
- Age: {age}
- Gender: {gender}
- Medical History: {medical_history}

Please provide:
1. A clear interpretation of the test result.
2. Possible implications of this result, considering the patient's information.
3. Any recommendations for follow-up or lifestyle changes, if applicable.
4. Potential related conditions to be aware of, given this result and the patient's history.

Format your response in a clear, concise manner that a patient could understand, while maintaining medical accuracy."""

            interpretation = await self.call_gpt4(prompt)

            # Post-process the interpretation
            interpretation = await self.post_process_interpretation(interpretation, test_name, value, reference_range)

            # Cache the interpretation
            self.interpretation_cache[cache_key] = interpretation

            return interpretation

        except Exception as e:
            self.logger.error(f"Error in interpret_lab_result: {str(e)}")
            return f"We apologize, but an error occurred while interpreting the {test_name} result. Please consult with your healthcare provider for accurate interpretation."

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
        # Check cache first
        if test_name in self.reference_range_cache:
            return self.reference_range_cache[test_name]

        async with self.AsyncSession() as session:
            try:
                result = await session.execute(select(ReferenceRange).where(ReferenceRange.test_name == test_name))
                range_data = result.scalars().first()

                if range_data:
                    # Check if data is outdated (older than 7 days)
                    last_updated = datetime.strptime(range_data.last_updated, "%Y-%m-%d")
                    if datetime.now() - last_updated > timedelta(days=7):
                        await self.update_reference_range(session, test_name)
                        await session.refresh(range_data)
                else:
                    # If not in database, fetch from API and store
                    range_data = await self.fetch_reference_range_from_api(test_name)
                    if range_data:
                        new_range = ReferenceRange(
                            test_name=test_name,
                            low=range_data['low'],
                            high=range_data['high'],
                            unit=range_data['unit'],
                            last_updated=datetime.now().strftime("%Y-%m-%d")
                        )
                        session.add(new_range)
                        await session.commit()
                    else:
                        self.logger.warning(f"No reference range found for {test_name}")
                        return {"low": 0, "high": 0, "unit": "unknown"}

                # Cache the result
                self.reference_range_cache[test_name] = {
                    "low": range_data.low,
                    "high": range_data.high,
                    "unit": range_data.unit
                }
                return self.reference_range_cache[test_name]

            except Exception as e:
                self.logger.error(f"Error fetching reference range for {test_name}: {str(e)}")
                return {"low": 0, "high": 0, "unit": "unknown"}

    async def fetch_reference_range_from_api(self, test_name: str) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.medical_api_url}/reference_range/{test_name}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"API error: {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Error fetching from API: {str(e)}")
                return None

    async def update_reference_range(self, session: AsyncSession, test_name: str):
        new_data = await self.fetch_reference_range_from_api(test_name)
        if new_data:
            await session.execute(
                update(ReferenceRange).
                where(ReferenceRange.test_name == test_name).
                values(
                    low=new_data['low'],
                    high=new_data['high'],
                    unit=new_data['unit'],
                    last_updated=datetime.now().strftime("%Y-%m-%d")
                )
            )
            await session.commit()


    async def interpret_lab_result(self, test_name: str, value: float, patient_info: Dict[str, Any]) -> str:
        try:
            reference_range = await self.get_reference_range(test_name)
            
            age = patient_info.get('age', 'unknown age')
            gender = patient_info.get('gender', 'unknown gender')
            medical_history = ", ".join(patient_info.get('medical_history', ['No known medical history']))

            prompt = f"""As a medical professional, interpret the following lab test result:

Test Name: {test_name}
Test Value: {value}
Reference Range: {reference_range['low']} - {reference_range['high']}

Patient Information:
- Age: {age}
- Gender: {gender}
- Medical History: {medical_history}

Please provide:
1. A clear interpretation of the test result.
2. Possible implications of this result, considering the patient's information.
3. Any recommendations for follow-up or lifestyle changes, if applicable.
4. Potential related conditions to be aware of, given this result and the patient's history.

Format your response in a clear, concise manner that a patient could understand, while maintaining medical accuracy."""

            interpretation = await self.call_gpt4(prompt)

            # Post-process the interpretation
            interpretation = await self.post_process_interpretation(interpretation, test_name, value, reference_range)

            return interpretation

        except Exception as e:
            self.logger.error(f"Error in interpret_lab_result: {str(e)}")
            return f"We apologize, but an error occurred while interpreting the {test_name} result. Please consult with your healthcare provider for accurate interpretation."

    async def post_process_interpretation(self, interpretation: str, test_name: str, value: float, reference_range: Dict[str, float]) -> str:
        # Add a summary statement at the beginning
        if value < reference_range['low']:
            summary = f"Your {test_name} result of {value} is below the reference range of {reference_range['low']} - {reference_range['high']}."
        elif value > reference_range['high']:
            summary = f"Your {test_name} result of {value} is above the reference range of {reference_range['low']} - {reference_range['high']}."
        else:
            summary = f"Your {test_name} result of {value} is within the reference range of {reference_range['low']} - {reference_range['high']}."

        interpretation = summary + "\n\n" + interpretation

        # Ensure the interpretation doesn't exceed a certain length
        max_length = 1000
        if len(interpretation) > max_length:
            interpretation = interpretation[:max_length] + "... (truncated for brevity)"

        # Add a disclaimer
        disclaimer = ("\n\nPlease note: This interpretation is generated by an AI system and should not "
                      "replace professional medical advice. Always consult with your healthcare provider "
                      "for a comprehensive interpretation of your test results and appropriate medical care.")
        interpretation += disclaimer

        return interpretation


    def train(self, dataset_path: str):
        data = pd.read_csv(dataset_path)
        
        X = data.drop(['test_name', 'interpretation', 'recommendation'], axis=1)
        y_interpretation = data['interpretation']
        y_recommendation = data['recommendation']
        
        self.feature_names = X.columns.tolist()
        
        X = self.imputer.fit_transform(X)
        X = self.scaler.fit_transform(X)
        y_interpretation = self.label_encoder.fit_transform(y_interpretation)
        
        X_train, X_test, y_int_train, y_int_test, y_rec_train, y_rec_test = train_test_split(
            X, y_interpretation, y_recommendation, test_size=0.2, random_state=42)
        
        self.interpretation_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.interpretation_model.fit(X_train, y_int_train)
        
        self.recommendation_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.recommendation_model.fit(X_train, y_rec_train)
        
        int_accuracy = self.interpretation_model.score(X_test, y_int_test)
        rec_accuracy = self.recommendation_model.score(X_test, y_rec_test)
        print(f"Interpretation model accuracy: {int_accuracy:.2f}")
        print(f"Recommendation model accuracy: {rec_accuracy:.2f}")

        self.interpretation_corpus = data['interpretation'].tolist()
        self.recommendation_corpus = data['recommendation'].tolist()
        self.vectorized_interpretations = self.tfidf_vectorizer.fit_transform(self.interpretation_corpus)
        self.vectorized_recommendations = self.tfidf_vectorizer.transform(self.recommendation_corpus)

        # Initialize and train BERT model
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.fine_tune_bert(data)

    async def update_models(self, new_data_path: str):
        await self.load_and_train(new_data_path)
        self.logger.info("Models updated with new data")

    async def load_and_train(self, new_data_path: str, test_size: float = 0.2, random_state: int = 42) -> None:
        """
        Load new data, preprocess it, train models, and save them.

        Args:
            new_data_path (str): Path to the new data CSV file.
            test_size (float): Proportion of the dataset to include in the test split.
            random_state (int): Random state for reproducibility.
        """
        try:
            # Load new data
            new_data = pd.read_csv(new_data_path)
            self.logger.info(f"Loaded new data from {new_data_path}")

            # Preprocess data
            X, y_interpretation, y_recommendation = await self.preprocess_data(new_data)

            # Split data into train and test sets
            X_train, X_test, y_interp_train, y_interp_test, y_recom_train, y_recom_test = train_test_split(
                X, y_interpretation, y_recommendation, test_size=test_size, random_state=random_state
            )

            # Train models
            await self.train_models(X_train, y_interp_train, y_recom_train)

            # Evaluate models
            await self.evaluate_models(X_test, y_interp_test, y_recom_test)

            # Save models
            await self.save_models()

            self.logger.info("Model training and saving completed successfully")
        except Exception as e:
            self.logger.error(f"Error in load_and_train: {str(e)}")
            raise

    async def preprocess_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Preprocess the input data for model training.

        Args:
            data (pd.DataFrame): Input data containing lab test results and interpretations.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: Preprocessed features, interpretation labels, and recommendation labels.
        """
        try:
           
            X = data['test_result'].values.reshape(-1, 1)
            y_interpretation = data['interpretation'].values
            y_recommendation = data['recommendation'].values

            # Handle missing values
            self.imputer = SimpleImputer(strategy='mean')
            X = self.imputer.fit_transform(X)

            # Scale features
            self.scaler = StandardScaler()
            X = self.scaler.fit_transform(X)

            # Encode labels
            self.interp_encoder = LabelEncoder()
            self.recom_encoder = LabelEncoder()
            y_interpretation = self.interp_encoder.fit_transform(y_interpretation)
            y_recommendation = self.recom_encoder.fit_transform(y_recommendation)

            return X, y_interpretation, y_recommendation
        except Exception as e:
            self.logger.error(f"Error in preprocess_data: {str(e)}")
            raise

    async def train_models(self, X_train: np.ndarray, y_interp_train: np.ndarray, y_recom_train: np.ndarray) -> None:
        """
        Train the interpretation and recommendation models.

        Args:
            X_train (np.ndarray): Training features.
            y_interp_train (np.ndarray): Training labels for interpretation.
            y_recom_train (np.ndarray): Training labels for recommendation.
        """
        try:
            # Train interpretation model
            self.interpretation_model = GradientBoostingClassifier(random_state=42)
            await self.loop.run_in_executor(None, self.interpretation_model.fit, X_train, y_interp_train)

            # Train recommendation model
            self.recommendation_model = GradientBoostingClassifier(random_state=42)
            await self.loop.run_in_executor(None, self.recommendation_model.fit, X_train, y_recom_train)

            self.logger.info("Models trained successfully")
        except Exception as e:
            self.logger.error(f"Error in train_models: {str(e)}")
            raise

    async def evaluate_models(self, X_test: np.ndarray, y_interp_test: np.ndarray, y_recom_test: np.ndarray) -> None:
        """
        Evaluate the trained models on the test set.

        Args:
            X_test (np.ndarray): Test features.
            y_interp_test (np.ndarray): Test labels for interpretation.
            y_recom_test (np.ndarray): Test labels for recommendation.
        """
        try:
            # Evaluate interpretation model
            y_interp_pred = await self.loop.run_in_executor(None, self.interpretation_model.predict, X_test)
            interp_report = classification_report(y_interp_test, y_interp_pred, target_names=self.interp_encoder.classes_)
            self.logger.info(f"Interpretation Model Evaluation:\n{interp_report}")

            # Evaluate recommendation model
            y_recom_pred = await self.loop.run_in_executor(None, self.recommendation_model.predict, X_test)
            recom_report = classification_report(y_recom_test, y_recom_pred, target_names=self.recom_encoder.classes_)
            self.logger.info(f"Recommendation Model Evaluation:\n{recom_report}")
        except Exception as e:
            self.logger.error(f"Error in evaluate_models: {str(e)}")
            raise

    async def save_models(self) -> None:
        """
        Save the trained models and preprocessing objects.
        """
        try:
            model_path = "models/"
            os.makedirs(model_path, exist_ok=True)

            joblib.dump(self.interpretation_model, f"{model_path}interpretation_model.joblib")
            joblib.dump(self.recommendation_model, f"{model_path}recommendation_model.joblib")
            joblib.dump(self.imputer, f"{model_path}imputer.joblib")
            joblib.dump(self.scaler, f"{model_path}scaler.joblib")
            joblib.dump(self.interp_encoder, f"{model_path}interp_encoder.joblib")
            joblib.dump(self.recom_encoder, f"{model_path}recom_encoder.joblib")

            self.logger.info("Models and preprocessing objects saved successfully")
        except Exception as e:
            self.logger.error(f"Error in save_models: {str(e)}")
            raise

    async def load_models(self) -> None:
        """
        Load the trained models and preprocessing objects.
        """
        try:
            model_path = "models/"

            self.interpretation_model = joblib.load(f"{model_path}interpretation_model.joblib")
            self.recommendation_model = joblib.load(f"{model_path}recommendation_model.joblib")
            self.imputer = joblib.load(f"{model_path}imputer.joblib")
            self.scaler = joblib.load(f"{model_path}scaler.joblib")
            self.interp_encoder = joblib.load(f"{model_path}interp_encoder.joblib")
            self.recom_encoder = joblib.load(f"{model_path}recom_encoder.joblib")

            self.logger.info("Models and preprocessing objects loaded successfully")
        except Exception as e:
            self.logger.error(f"Error in load_models: {str(e)}")
            raise

    async def submit_feedback(self, lab_test_id: int, original_interpretation: str, 
                              corrected_interpretation: str, feedback_provider: str) -> None:
        """
        Submit feedback for a lab test interpretation.
        """
        async with self.AsyncSession() as session:
            feedback_entry = FeedbackEntry(
                lab_test_id=lab_test_id,
                original_interpretation=original_interpretation,
                corrected_interpretation=corrected_interpretation,
                feedback_provider=feedback_provider,
                confidence_score=self.calculate_confidence_score(original_interpretation, corrected_interpretation)
            )
            session.add(feedback_entry)
            await session.commit()

        await self.trigger_model_update()


    def preprocess_text(self, text):
        # Tokenize, remove stopwords, and lemmatize
        tokens = word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)

    def get_bert_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

    def extract_medical_entities(self, text):
        doc = self.nlp(text)
        medical_entities = [ent.text for ent in doc.ents if ent.label_ in ['DISEASE', 'CHEMICAL', 'BODY_PART']]
        return set(medical_entities)

    def calculate_confidence_score(self, original: str, corrected: str) -> float:
        """
        Calculate a confidence score based on the difference between original and corrected interpretations
        using advanced NLP techniques.
        """
        # Preprocess texts
        original_processed = self.preprocess_text(original)
        corrected_processed = self.preprocess_text(corrected)

        # Get BERT embeddings
        original_embedding = self.get_bert_embedding(original_processed)
        corrected_embedding = self.get_bert_embedding(corrected_processed)

        # Calculate cosine similarity between embeddings
        semantic_similarity = cosine_similarity([original_embedding], [corrected_embedding])[0][0]

        # Extract medical entities
        original_entities = self.extract_medical_entities(original)
        corrected_entities = self.extract_medical_entities(corrected)

        # Calculate Jaccard similarity for medical entities
        entity_similarity = len(original_entities.intersection(corrected_entities)) / len(original_entities.union(corrected_entities))

        # Calculate edit distance
        edit_distance = nltk.edit_distance(original_processed, corrected_processed)
        max_length = max(len(original_processed), len(corrected_processed))
        edit_similarity = 1 - (edit_distance / max_length)

        # Combine scores (you may want to adjust weights based on your specific use case)
        confidence_score = 0.5 * semantic_similarity + 0.3 * entity_similarity + 0.2 * edit_similarity

        return confidence_score

    async def trigger_model_update(self) -> None:
        """
        Trigger a model update based on accumulated feedback.
        """
        async with self.AsyncSession() as session:
            result = await session.execute(select(FeedbackEntry).order_by(FeedbackEntry.feedback_time.desc()).limit(1000))
            recent_feedback = result.scalars().all()

        if len(recent_feedback) >= 100:  # Only update if we have a significant amount of new feedback
            await self.update_model_with_feedback(recent_feedback)

    async def update_model_with_feedback(self, feedback_entries: List[FeedbackEntry]) -> None:
        """
        Update the interpretation model using the feedback data.
        """
        X = []
        y = []
        for entry in feedback_entries:
            lab_test = await self.get_lab_test(entry.lab_test_id)
            X.append([lab_test.value])
            y.append(entry.corrected_interpretation)

        X = np.array(X)
        y = np.array(y)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        new_model = GradientBoostingClassifier(random_state=42)
        await self.loop.run_in_executor(None, new_model.fit, X_train, y_train)

        y_pred = await self.loop.run_in_executor(None, new_model.predict, X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')

        if accuracy > 0.9 and precision > 0.9 and recall > 0.9 and f1 > 0.9:
            self.interpretation_model = new_model
            await self.save_models()
            self.logger.info(f"Model updated successfully. Metrics: Accuracy={accuracy}, Precision={precision}, Recall={recall}, F1={f1}")
        else:
            self.logger.warning(f"Model update did not meet performance criteria. Metrics: Accuracy={accuracy}, Precision={precision}, Recall={recall}, F1={f1}")

    async def get_lab_test(self, lab_test_id: int) -> LabTest:
        """
        Retrieve a lab test by its ID.
        """
        async with self.AsyncSession() as session:
            result = await session.execute(select(LabTest).filter(LabTest.id == lab_test_id))
            return result.scalar_one()

    async def expand_lab_tests(self) -> None:
        """
        Expand the range of lab tests by fetching new tests from a medical API.
        """
        new_tests = await self.fetch_new_lab_tests()
        await self.add_new_lab_tests(new_tests)
        await self.update_models_with_new_tests(new_tests)

    async def fetch_new_lab_tests(self) -> List[Dict[str, Any]]:
        """
        Fetch new lab tests from a medical API.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{self.medical_api_url}/new_lab_tests') as response:
                if response.status == 200:
                    return await response.json()
                else:
                    self.logger.error(f"Failed to fetch new lab tests. Status: {response.status}")
                    return []

    async def add_new_lab_tests(self, new_tests: List[Dict[str, Any]]) -> None:
        """
        Add new lab tests to the database.
        """
        async with self.AsyncSession() as session:
            for test in new_tests:
                expansion = LabTestExpansion(
                    test_name=test['name'],
                    category=test['category'],
                    reference_range=test['reference_range'],
                    units=test['units'],
                    description=test['description']
                )
                session.add(expansion)
            await session.commit()

    async def update_models_with_new_tests(self, new_tests: List[Dict[str, Any]]) -> None:
        """
        Update the interpretation and recommendation models with new lab tests.
        """
        # Fetch existing data
        async with self.AsyncSession() as session:
            result = await session.execute(select(LabTest))
            existing_tests = result.scalars().all()

        # Combine existing and new data
        all_tests = existing_tests + new_tests
        X = [[test.value] for test in all_tests]
        y_interpretation = [test.interpretation for test in all_tests]
        y_recommendation = [test.recommendation for test in all_tests]

        # Update interpretation model
        self.interpretation_model = await self.train_model(X, y_interpretation)

        # Update recommendation model
        self.recommendation_model = await self.train_model(X, y_recommendation)

        await self.save_models()

    async def train_model(self, X: List[List[float]], y: List[str]) -> GradientBoostingClassifier:
        """
        Train a new model with the given data.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = GradientBoostingClassifier(random_state=42)
        await self.loop.run_in_executor(None, model.fit, X_train, y_train)
        return model

    async def schedule_lab_test_expansion(self) -> None:
        """
        Schedule regular updates to expand the range of lab tests.
        """
        while True:
            await self.expand_lab_tests()
            await asyncio.sleep(24 * 60 * 60)  # Wait for 24 hours before the next update

    def fine_tune_bert(self, data):
        # Prepare data for BERT
        encoded_data = self.bert_tokenizer(data['interpretation'].tolist(), truncation=True, padding=True, return_tensors='pt')
        
        # Fine-tune BERT
        optimizer = torch.optim.AdamW(self.bert_model.parameters(), lr=2e-5)
        
        for epoch in range(3):  # Number of epochs can be adjusted
            self.bert_model.train()
            for batch in torch.utils.data.DataLoader(encoded_data['input_ids'], batch_size=16):
                outputs = self.bert_model(batch)
                loss = outputs.loss
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()

    def save_models(self, path: str):
        joblib.dump((self.interpretation_model, self.recommendation_model, self.scaler, 
                     self.imputer, self.label_encoder, self.feature_names, 
                     self.tfidf_vectorizer, self.interpretation_corpus, 
                     self.recommendation_corpus, self.vectorized_interpretations, 
                     self.vectorized_recommendations), path)
        
        # Save BERT model
        torch.save(self.bert_model.state_dict(), path + '_bert.pth')

    def load_models(self, path: str):
        (self.interpretation_model, self.recommendation_model, self.scaler, 
         self.imputer, self.label_encoder, self.feature_names, 
         self.tfidf_vectorizer, self.interpretation_corpus, 
         self.recommendation_corpus, self.vectorized_interpretations, 
         self.vectorized_recommendations) = joblib.load(path)
        
        # Load BERT model
        self.bert_model = BertModel.from_pretrained('bert-base-uncased')
        self.bert_model.load_state_dict(torch.load(path + '_bert.pth'))
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    def interpret(self, lab_results: Dict[str, str], patient_info: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        interpretations = {}
        for test, value_str in lab_results.items():
            value, unit, reference_range = self.parse_result(value_str)
            features = self.prepare_features(test, value, reference_range, patient_info)
            interpretation = self.predict_interpretation(features)
            recommendation = self.predict_recommendation(features)
            confidence_score = self.calculate_confidence_score(features)

            interpretations[test] = {
                'value': value_str,
                'numeric_value': value,
                'unit': unit,
                'category': self.categorize_test(test),
                'reference_range': f"{reference_range[0]}-{reference_range[1]} {unit}" if reference_range else "Unknown",
                'status': self.determine_status(value, reference_range) if reference_range else "Unknown",
                'interpretation': interpretation,
                'recommendation': recommendation,
                'confidence_score': confidence_score
            }
        return interpretations

    def parse_result(self, value_str: str) -> Tuple[float, str, Optional[Tuple[float, float]]]:
        patterns = [
            r'([-+]?\d*\.\d+|\d+)\s*(\S+)\s*\(Reference Range:\s*([-+]?\d*\.\d+|\d+)\s*-\s*([-+]?\d*\.\d+|\d+)\s*(\S+)\)',
            r'([-+]?\d*\.\d+|\d+)\s*(\S+)\s*\(Normal:\s*([-+]?\d*\.\d+|\d+)\s*-\s*([-+]?\d*\.\d+|\d+)\s*(\S+)\)',
            r'([-+]?\d*\.\d+|\d+)\s*(\S+)\s*\(([-+]?\d*\.\d+|\d+)\s*-\s*([-+]?\d*\.\d+|\d+)\s*(\S+)\)',
            r'([-+]?\d*\.\d+|\d+)\s*(\S+)'
        ]

        for pattern in patterns:
            match = re.match(pattern, value_str)
            if match:
                groups = match.groups()
                value = float(groups[0])
                unit = groups[1]
                if len(groups) > 2:
                    ref_low = float(groups[2])
                    ref_high = float(groups[3])
                    return value, unit, (ref_low, ref_high)
                else:
                    return value, unit, None

        raise ValueError(f"Unable to parse result: {value_str}")

    def categorize_test(self, test_name: str) -> str:
        categories = {
            'Complete Blood Count': ['WBC', 'RBC', 'Hemoglobin', 'Hematocrit', 'Platelets'],
            'Lipid Profile': ['Cholesterol', 'LDL', 'HDL', 'Triglycerides'],
            'Liver Function Tests': ['ALT', 'AST', 'ALP', 'Bilirubin'],
            'Renal Function Tests': ['BUN', 'Creatinine', 'GFR'],
            'Metabolic Tests': ['Glucose', 'HbA1c', 'Insulin'],
            'Electrolytes': ['Sodium', 'Potassium', 'Chloride', 'Bicarbonate'],
            'Thyroid Function Tests': ['TSH', 'T3', 'T4'],
            'Cardiac Markers': ['Troponin', 'CK-MB', 'BNP'],
            'Tumor Markers': ['PSA', 'CEA', 'CA-125'],
            'Vitamins and Minerals': ['Vitamin D', 'Vitamin B12', 'Ferritin', 'Folate']
        }
        for category, tests in categories.items():
            if any(t.lower() in test_name.lower() for t in tests):
                return category
        return 'Other Tests'

    def determine_status(self, value: float, reference_range: tuple) -> str:
        if value < reference_range[0]:
            return "Low"
        elif value > reference_range[1]:
            return "High"
        else:
            return "Normal"

    def prepare_features(self, test: str, value: float, reference_range: Optional[Tuple[float, float]], patient_info: Dict[str, str]) -> np.array:
        features = {
            'value': value,
            'ref_low': reference_range[0] if reference_range else np.nan,
            'ref_high': reference_range[1] if reference_range else np.nan,
            'ratio_to_low': value / reference_range[0] if reference_range else np.nan,
            'ratio_to_high': value / reference_range[1] if reference_range else np.nan,
            'z_score': ((value - np.mean(reference_range)) / (np.std(reference_range) / np.sqrt(2))) 
                       if reference_range else np.nan,
            'age': patient_info.get('age', np.nan),
            'is_male': 1 if patient_info.get('gender', '').lower() == 'male' else 0,
            'is_female': 1 if patient_info.get('gender', '').lower() == 'female' else 0
        }
        
        for feature in self.feature_names:
            if feature.startswith('test_'):
                features[feature] = 1 if feature == f'test_{test}' else 0
        
        for feature in self.feature_names:
            if feature not in features:
                features[feature] = 0
        
        return np.array([features[f] for f in self.feature_names]).reshape(1, -1)

    def predict_interpretation(self, features: np.array) -> str:
        features_imputed = self.imputer.transform(features)
        features_scaled = self.scaler.transform(features_imputed)
        interpretation_index = self.interpretation_model.predict(features_scaled)[0]
        interpretation = self.label_encoder.inverse_transform([interpretation_index])[0]
        
        # Use BERT for more nuanced interpretation
        bert_input = self.bert_tokenizer(interpretation, return_tensors="pt")
        with torch.no_grad():
            bert_output = self.bert_model(**bert_input)
        
        bert_features = bert_output.last_hidden_state.mean(dim=1)
        
        similar_interpretations = self.find_similar_texts(interpretation, self.vectorized_interpretations, self.interpretation_corpus)
        
        final_interpretation = f"{interpretation}\n\nAdditional insights:\n"
        final_interpretation += "\n".join(f"- {interp}" for interp in similar_interpretations[:2])
        
        return final_interpretation

    def predict_recommendation(self, features: np.array) -> str:
        features_imputed = self.imputer.transform(features)
        features_scaled = self.scaler.transform(features_imputed)
        recommendation = self.recommendation_model.predict(features_scaled)[0]
        
        similar_recommendations = self.find_similar_texts(recommendation, self.vectorized_recommendations, self.recommendation_corpus)
        
        final_recommendation = f"{recommendation}\n\nAdditional recommendations:\n"
        final_recommendation += "\n".join(f"- {rec}" for rec in similar_recommendations[:2])
        
        return final_recommendation

    def find_similar_texts(self, text: str, vectorized_corpus, corpus: List[str]) -> List[str]:
        text_vector = self.tfidf_vectorizer.transform([text])
        similarities = cosine_similarity(text_vector, vectorized_corpus)
        most_similar_indices = similarities.argsort()[0][-3:-1][::-1]  # Get top 2 most similar
        return [corpus[i] for i in most_similar_indices]

    def get_low_indication(self, test_name: str) -> str:
        indications = {
            "White Blood Cell": "a weakened immune system or bone marrow issues",
            "Red Blood Cell": "anemia or blood loss",
            "Hemoglobin": "iron deficiency or chronic diseases",
            "Platelets": "a bleeding disorder or bone marrow problem",
            "Sodium": "dehydration or certain medications",
            "Potassium": "kidney problems or excessive sweating",
            "Calcium": "vitamin D deficiency or parathyroid issues",
            "Glucose": "hypoglycemia or certain medications",
            "default": "a deficiency or underlying health condition"
        }
        return indications.get(test_name, indications["default"])

    def get_high_indication(self, test_name: str) -> str:
        indications = {
            "White Blood Cell": "an infection, inflammation, or certain blood disorders",
            "Red Blood Cell": "dehydration or a bone marrow disorder",
            "Hemoglobin": "polycythemia or living at high altitudes",
            "Platelets": "a bone marrow disorder or certain medications",
            "Sodium": "dehydration or certain endocrine disorders",
            "Potassium": "kidney problems or excessive intake",
            "Calcium": "hyperparathyroidism or certain cancers",
            "Glucose": "diabetes or certain medications",
            "default": "an excess or underlying health condition"
        }
        return indications.get(test_name, indications["default"])

    def calculate_confidence_score(self, features: np.array) -> float:
        features_imputed = self.imputer.transform(features)
        features_scaled = self.scaler.transform(features_imputed)
        probabilities = self.interpretation_model.predict_proba(features_scaled)[0]
        return max(probabilities)

    def parse_pdf_report(self, pdf_path: str) -> Dict[str, str]:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        # Use regex to extract lab results
        pattern = r"(\w+)\s*:\s*([\d.]+)\s*(\w+/\w+)"
        matches = re.findall(pattern, text)
        
        results = {}
        for match in matches:
            test_name, value, unit = match
            results[test_name] = f"{value} {unit}"
        
        return results

    def parse_image_report(self, image_path: str) -> Dict[str, str]:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        
        # Use regex to extract lab results
        pattern = r"(\w+)\s*:\s*([\d.]+)\s*(\w+/\w+)"
        matches = re.findall(pattern, text)
        
        results = {}
        for match in matches:
            test_name, value, unit = match
            results[test_name] = f"{value} {unit}"
        
        return results


    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @retry(wait=wait_random_exponential(multiplier=1, max=60), stop=stop_after_attempt(3))
    async def fetch_medical_guidelines(self) -> List[Dict[str, Any]]:
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.medical_api_url}/latest_guidelines") as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            self.logger.error(f"Failed to fetch medical guidelines. Status: {response.status}")
                            return []
            except aiohttp.ClientError as e:
                self.logger.error(f"Network error while fetching medical guidelines: {str(e)}")
                raise
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding medical guidelines JSON: {str(e)}")
                raise
            except Exception as e:
                self.logger.error(f"Unexpected error in fetch_medical_guidelines: {str(e)}")
                raise

    async def update_medical_guidelines(self):
        try:
            guidelines = await self.fetch_medical_guidelines()
            
            async with self.AsyncSession() as session:
                for guideline in guidelines:
                    db_guideline = MedicalGuideline(
                        test_name=guideline['test_name'],
                        guideline=guideline['content'],
                        source=guideline['source'],
                        last_updated=datetime.now()
                    )
                    session.merge(db_guideline)
                
                await session.commit()
            
            self.logger.info(f"Successfully updated {len(guidelines)} medical guidelines.")
        except Exception as e:
            self.logger.error(f"Error in update_medical_guidelines: {str(e)}")
            
            raise

    async def get_medical_guideline(self, test_name: str) -> Dict[str, Any]:
        async with self.AsyncSession() as session:
            result = await session.execute(select(MedicalGuideline).where(MedicalGuideline.test_name == test_name))
            guideline = result.scalars().first()
            
            if guideline:
                return {
                    'test_name': guideline.test_name,
                    'guideline': guideline.guideline,
                    'source': guideline.source,
                    'last_updated': guideline.last_updated
                }
            else:
                return None

    async def generate_narrative_report(self, interpretations: Dict[str, Dict[str, Any]], patient_info: Dict[str, str]) -> str:
        try:
            template = self.jinja_env.get_template('lab_report_template.jinja2')
            
            # Fetch relevant medical guidelines
            guidelines = {}
            for test in interpretations.keys():
                guideline = await self.get_medical_guideline(test)
                if guideline:
                    guidelines[test] = guideline

            report = template.render(
                patient_info=patient_info,
                interpretations=interpretations,
                guidelines=guidelines,
                generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            return report

        except Exception as e:
            self.logger.error(f"Error in generate_narrative_report: {str(e)}")
            # Fallback to a basic report generation if template rendering fails
            return self.generate_basic_report(interpretations, patient_info)

    def generate_basic_report(self, interpretations: Dict[str, Dict[str, Any]], patient_info: Dict[str, str]) -> str:
        report = f"Lab Report for {patient_info['name']} (Age: {patient_info['age']}, Gender: {patient_info['gender']})\n\n"
        
        for test, data in interpretations.items():
            report += f"{test}:\n"
            report += f"Value: {data['value']}\n"
            report += f"Status: {data['status']}\n"
            report += f"Interpretation: {data['interpretation']}\n"
            report += f"Recommendation: {data['recommendation']}\n\n"
        
        report += f"\nReport generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return report

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def explain_interpretation(self, test_name: str, interpretation: str, patient_info: dict) -> str:
        try:
            medical_context = self.medical_context.get(test_name, f"A medical test called {test_name}")
            age = patient_info.get('age', 'unknown age')
            gender = patient_info.get('gender', 'unknown gender')

            prompt = f"""As a medical professional, explain the following lab test interpretation 
            for a {age}-year-old {gender} patient in simple terms:

            Test: {test_name}
            Context: {medical_context}
            Interpretation: {interpretation}

            Provide a clear, concise explanation in simple terms that a patient can understand:"""

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful medical assistant, explaining lab results in simple terms."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                n=1,
                temperature=0.7,
            )

            explanation = response.choices[0].message['content'].strip()
            explanation = self.post_process_explanation(explanation)

            return explanation

        except Exception as e:
            logging.error(f"Error in explain_interpretation: {str(e)}")
            return f"The {test_name} test result suggests {interpretation}. Please consult with your healthcare provider for a detailed explanation."

    async def initialize_federated_model(self):
        # Fetch historical data from the database
        historical_data = await self.fetch_historical_data()
        self.federated_model = train_federated_model(historical_data)

    async def fetch_historical_data(self) -> List[Dict[str, Any]]:
        try:
            async with self.AsyncSession() as session:
             # Fetch lab test results from the database
            query = select(LabTest, LabResult).join(LabResult)
            result = await session.execute(query)
            lab_data = result.fetchall()

            historical_data = []
            for lab_test, lab_result in lab_data:
                historical_data.append({
                    'text': f"{lab_test.test_name}: {lab_result.result} {lab_test.unit}",
                    'label': lab_result.interpretation_label,
                    'patient_id': lab_result.patient_id,
                    'timestamp': lab_result.timestamp
                })

            # Sort data by timestamp to ensure chronological order
            historical_data.sort(key=lambda x: x['timestamp'])

            return historical_data
    except SQLAlchemyError as e:
        self.logger.error(f"Database error while fetching historical data: {e}")
        return []
    except Exception as e:
        self.logger.error(f"Unexpected error while fetching historical data: {e}")
        return []

    @ethical_ai_wrapper
    async def interpret_lab_results(self, input_data: Dict[str, Any], patient_id: str, use_voice: bool = False, target_lang: str = 'en') -> Dict[str, Any]:
        try:
            # Process expanded input
            if 'file_path' in input_data:
                extracted_data = await process_expanded_input(input_data['file_path'])
                text = extracted_data.get('extracted_text', '')
            else:
                text = input_data.get('text', '')

            # Preprocess and translate text
            preprocessed_text = await self.preprocess_text(text)
            translated_text = await self.language_processor.translate(preprocessed_text, target_lang)

            # Use federated model for prediction
            prediction = (await predict_with_federated_model([translated_text]))[0]

            # Get interpretation and explanation from ensemble model
            interpretation, explanation = await self.ensemble_model.predict(translated_text)

            # Extract lab results
            lab_results = await self.extract_lab_results(translated_text)

            # Check for critical results
            is_critical = await check_critical_results(interpretation, lab_results, patient_id)
            if is_critical:
                await send_alert(patient_id, lab_results, interpretation)

            # Calculate health score and check achievements
            health_score = await self.calculate_health_score(lab_results)
            new_achievements = await self.check_achievements(patient_id, health_score)

            interpretation_result = {
                'interpretation': interpretation,
                'explanation': explanation,
                'is_critical': is_critical,
                'health_score': health_score,
                'new_achievements': new_achievements,
                'prediction': prediction
            }

            if use_voice:
                audio_file = await self.voice_interface.text_to_speech(interpretation)
                return send_file(audio_file, mimetype='audio/mp3')
            else:
                return jsonify(interpretation_result)

        except Exception as e:
            logging.error(f"Error in lab result interpretation: {str(e)}")
            return {'error': str(e)}

    async def handle_expert_feedback(self, input_data: Dict[str, Any], expert_interpretation: str) -> Dict[str, Any]:
        try:
            # Process input data
            if 'file_path' in input_data:
                extracted_data = await process_expanded_input(input_data['file_path'])
                text = extracted_data.get('extracted_text', '')
            else:
                text = input_data.get('text', '')

            # Add data to continuous learning
            await self.continuous_learning.add_data(text, expert_interpretation)
            update_status = await self.continuous_learning.update_model()

            # Update federated model
            await self.update_federated_model(text, expert_interpretation)

            return {'update_status': update_status, 'federated_model_updated': True}
        except Exception as e:
            logging.error(f"Error in handling expert feedback: {str(e)}")
            return {'error': str(e)}

    async def update_federated_model(self, text: str, expert_interpretation: str):
        try:
            # Preprocess the text and expert interpretation
            preprocessed_text = await self.preprocess_text(text)
            preprocessed_interpretation = await self.preprocess_text(expert_interpretation)

            # Prepare the data for federated learning
            new_data = {
                'input': preprocessed_text,
                'label': preprocessed_interpretation
            }

            # Update local dataset
            await self.update_local_dataset(new_data)

            # Trigger federated learning round
            await self.trigger_federated_learning()

            logging.info(f"Federated model updated with new data: {new_data}")
            return True
        except Exception as e:
            logging.error(f"Error updating federated model: {str(e)}")
            return False

    async def update_local_dataset(self, new_data: Dict[str, Any]):
        # Add new data to local dataset
        self.local_dataset.append(new_data)
        
        # If local dataset exceeds a certain size, remove oldest entries
        max_local_dataset_size = 1000  # Adjust as needed
        if len(self.local_dataset) > max_local_dataset_size:
            self.local_dataset = self.local_dataset[-max_local_dataset_size:]

    async def trigger_federated_learning(self):
        # Check if it's time to trigger a federated learning round
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_federated_update > self.federated_update_interval:
            # Prepare local updates
            local_updates = self.prepare_local_updates()

            # Perform federated learning
            updated_model = await train_federated_model(self.federated_model, local_updates)

            # Update local model
            self.federated_model = updated_model

            # Reset local dataset after update
            self.local_dataset = []

            # Update last federated update time
            self.last_federated_update = current_time

            logging.info("Federated learning round completed")

    def prepare_local_updates(self):
        # Convert local dataset to format expected by federated learning algorithm
        return {
            'inputs': [data['input'] for data in self.local_dataset],
            'labels': [data['label'] for data in self.local_dataset]
        }


    async def initialize_federated_model(self) -> EnsembleModel:
        try:
            # Try to load an existing model
            model = await load_model()
            if model:
                logging.info("Loaded existing federated model")
                return model

            # If no existing model, initialize a new one
            logging.info("Initializing new federated model")
            federated_learning = FederatedLearning()
            
            # Load initial training data
            initial_data = await load_initial_data()
            if not initial_data:
                logging.warning("No initial data available for federated model training")
                return federated_learning.get_global_model()

            # Prepare data for federated learning
            prepared_data = await prepare_data_for_federated_learning(initial_data)

            # Train the initial model
            await federated_learning.train([prepared_data['train']])

            # Save the initial model
            model = federated_learning.get_global_model()
            await save_model(model)

            logging.info("Initial federated model trained and saved")
            return model

        except Exception as e:
            logging.error(f"Error initializing federated model: {str(e)}")
            # In case of error, return a new untrained model
            return EnsembleModel()


    async def load_initial_data(self) -> Optional[List[Dict[str, Any]]]:
        try:
            data = []

            # Load data from JSON file
            file_data = await self._load_from_file('initial_data.json')
            if file_data:
                data.extend(file_data)

            # Load data from database
            db_data = await self._load_from_database()
            if db_data:
                data.extend(db_data)

            # Load data from API
            api_data = await self._load_from_api('https://api.example.com/training-data')
            if api_data:
                data.extend(api_data)

            if not data:
                logging.warning("No initial data found for federated model training")
                return None

            logging.info(f"Loaded {len(data)} initial data points")
            return data

        except Exception as e:
            logging.error(f"Error loading initial data: {str(e)}")
            return None

    async def _load_from_file(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            async with aiofiles.open(file_path, mode='r') as f:
                content = await f.read()
                data = json.loads(content)
            logging.info(f"Loaded {len(data)} data points from file")
            return data
        except FileNotFoundError:
            logging.warning(f"File {file_path} not found")
            return []
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from {file_path}")
            return []

    async def _load_from_database(self) -> List[Dict[str, Any]]:
        try:
            async with AsyncSession(self.engine) as session:
                result = await session.execute(select(TrainingData))
                data = [{"text": row.text, "label": row.label} for row in result.scalars()]
            logging.info(f"Loaded {len(data)} data points from database")
            return data
        except Exception as e:
            logging.error(f"Error loading data from database: {str(e)}")
            return []

    async def _load_from_api(self, api_url: str) -> List[Dict[str, Any]]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        logging.info(f"Loaded {len(data)} data points from API")
                        return data
                    else:
                        logging.warning(f"API request failed with status {response.status}")
                        return []
        except aiohttp.ClientError as e:
            logging.error(f"Error fetching data from API: {str(e)}")
            return []

# OutputFormatter class
class OutputFormatter:
    @staticmethod
    def to_plain_text(interpretations: Dict[str, Dict[str, Any]]) -> str:
        output = ""
        for test, data in interpretations.items():
            output += f"{test}:\n"
            output += f"Value: {data['value']}\n"
            output += f"Status: {data['status']}\n"
            output += f"Interpretation: {data['interpretation']}\n"
            output += f"Recommendation: {data['recommendation']}\n\n"
        return output

    @staticmethod
    def to_html(interpretations: Dict[str, Dict[str, Any]]) -> str:
        html = "<html><body>"
        for test, data in interpretations.items():
            html += f"<h2>{test}</h2>"
            html += f"<p><strong>Value:</strong> {data['value']}</p>"
            html += f"<p><strong>Status:</strong> {data['status']}</p>"
            html += f"<p><strong>Interpretation:</strong> {data['interpretation']}</p>"
            html += f"<p><strong>Recommendation:</strong> {data['recommendation']}</p>"
        html += "</body></html>"
        return html

    @staticmethod
    def to_pdf(interpretations: Dict[str, Dict[str, Any]], output_path: str, patient_info: Dict[str, str]):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Create story (content) for the PDF
        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceBefore=12, spaceAfter=6))
        styles.add(ParagraphStyle(name='BodyText', fontSize=11, spaceBefore=6, spaceAfter=6))

        # Add title
        story.append(Paragraph("Lab Test Results Report", styles['Heading1']))
        story.append(Spacer(1, 12))

        # Add patient information
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

        # Add interpretations
        for test_name, data in interpretations.items():
            story.append(Paragraph(test_name, styles['Heading2']))
            story.append(Paragraph(f"Value: {data['value']}", styles['BodyText']))
            story.append(Paragraph(f"Status: {data['status']}", styles['BodyText']))
            story.append(Paragraph("Interpretation:", styles['BodyText']))
            story.append(Paragraph(data['interpretation'], styles['BodyText']))
            story.append(Paragraph("Recommendation:", styles['BodyText']))
            story.append(Paragraph(data['recommendation'], styles['BodyText']))
            story.append(Spacer(1, 12))

        # Add disclaimer
        disclaimer = ("This report is generated by an AI system and should not replace professional medical advice. "
                      "Always consult with your healthcare provider for a comprehensive interpretation of your test "
                      "results and appropriate medical care.")
        story.append(Paragraph(disclaimer, ParagraphStyle(name='Disclaimer', fontSize=8, textColor=colors.grey)))

        # Build the PDF
        doc.build(story)

        # Get the value of the BytesIO buffer and write it to the output file
        pdf = buffer.getvalue()
        buffer.close()
        with open(output_path, 'wb') as f:
            f.write(pdf)

# API class
class LabReportAPI:
    def __init__(self, interpreter: AILabInterpreter, database: Database):
        self.interpreter = interpreter
        self.database = database
        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/interpret', methods=['POST'])
        def interpret_report():
            data = request.json
            lab_results = data['lab_results']
            patient_info = data['patient_info']
            interpretations = self.interpreter.interpret(lab_results, patient_info)
            return jsonify(interpretations)

        @self.app.route('/update_guidelines', methods=['POST'])
        def update_guidelines():
            self.interpreter.update_medical_guidelines()
            return jsonify({"message": "Guidelines updated successfully"})

        @self.app.route('/explain', methods=['GET'])
        def explain_interpretation():
            test_name = request.args.get('test_name')
            interpretation = request.args.get('interpretation')
            explanation = self.interpreter.explain_interpretation(test_name, interpretation)
            return jsonify({"explanation": explanation})

        @self.app.route('/submit_feedback', methods=['POST'])
        async def submit_feedback():
            data = request.json
            await self.interpreter.submit_feedback(
                data['lab_test_id'],
                data['original_interpretation'],
                data['corrected_interpretation'],
                data['feedback_provider']
            )
            return jsonify({"status": "success"})

           # API endpoints
        @app.route('/interpret', methods=['POST'])
        async def interpret_lab_results():
            data = request.json
            patient_id = data.get('patient_id')
            
            if not patient_id:
                return jsonify({'error': 'Patient ID is required'}), 400

            interpreter = AILabInterpreter()
            await interpreter.initialize()
    
            result = await interpreter.interpret_lab_results(data, patient_id)
            return jsonify(result)

    async def interpret_lab_results(self, text: str, patient_id: str, use_voice: bool = False, target_lang: str = 'en') -> Dict[str, Any]:
        preprocessed_text = await self.preprocess_text(text)
        translated_text = await self.language_processor.translate(preprocessed_text, target_lang)
        
        interpretation, explanation = await self.ensemble_model.predict(translated_text)
        lab_results = await self.extract_lab_results(translated_text)
        
        is_critical = await check_critical_results(interpretation, lab_results, patient_id)
        if is_critical:
            await send_alert(patient_id, lab_results, interpretation)

        health_score = await self.calculate_health_score(lab_results)
        new_achievements = await self.check_achievements(patient_id, health_score)

        response = {
            'interpretation': interpretation,
            'explanation': explanation,
            'is_critical': is_critical,
            'health_score': health_score,
            'new_achievements': new_achievements
        }

        if use_voice:
            audio_file = await self.voice_interface.text_to_speech(interpretation)
            return send_file(audio_file, mimetype='audio/mp3')
        else:
            return jsonify(response)

    async def handle_expert_feedback(self, text: str, expert_interpretation: str) -> Dict[str, Any]:
        await self.continuous_learning.add_data(text, expert_interpretation)
        update_status = await self.continuous_learning.update_model()
        return {'update_status': update_status}

# Initialize AILabInterpreter
interpreter = AILabInterpreter()

@app.before_first_request
def before_first_request():
    asyncio.run(interpreter.initialize())

@app.route('/interpret', methods=['POST'])
async def interpret_lab_results():
    data = await request.get_json()
    text = data['text']
    patient_id = data['patient_id']
    use_voice = data.get('use_voice', False)
    target_lang = data.get('target_lang', 'en')

    result = await interpreter.interpret_lab_results(text, patient_id, use_voice, target_lang)
    return result

@app.route('/voice_input', methods=['POST'])
async def voice_input():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename, {'wav', 'mp3'}):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = await interpreter.voice_interface.speech_to_text(filepath)
        os.remove(filepath)  # Clean up the uploaded file
        
        return jsonify({'text': text})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/expert_feedback', methods=['POST'])
async def expert_feedback():
    data = await request.get_json()
    text = data['text']
    expert_interpretation = data['expert_interpretation']

    result = await interpreter.handle_expert_feedback(text, expert_interpretation)
    return jsonify(result)

# Initialize AILabInterpreter
interpreter = AILabInterpreter()

@app.before_first_request
def before_first_request():
    asyncio.run(interpreter.initialize())

@app.route('/interpret', methods=['POST'])
async def interpret_lab_results():
    data = await request.get_json()
    text = data['text']
    patient_id = data['patient_id']
    use_voice = data.get('use_voice', False)
    target_lang = data.get('target_lang', 'en')

    result = await interpreter.interpret_lab_results(text, patient_id, use_voice, target_lang)
    return result

@app.route('/voice_input', methods=['POST'])
async def voice_input():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename, {'wav', 'mp3'}):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        text = await interpreter.voice_interface.speech_to_text(filepath)
        os.remove(filepath)  # Clean up the uploaded file
        
        return jsonify({'text': text})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/expert_feedback', methods=['POST'])
async def expert_feedback():
    data = await request.get_json()
    text = data['text']
    expert_interpretation = data['expert_interpretation']

    result = await interpreter.handle_expert_feedback(text, expert_interpretation)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)


    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

async def main():
    # Load environment variables
    load_dotenv()

    # Initialize the interpreter
    interpreter = AILabInterpreter()

    # Initialize the interpreter
    await interpreter.initialize()

    # Train the interpreter (if needed)
    await interpreter.train(os.getenv('TRAINING_DATA_PATH'))

    # Save the trained models
    await interpreter.save_models(os.getenv('MODELS_DIR'))

    # Update medical guidelines
    await interpreter.update_medical_guidelines()

    # Process a lab report
    lab_report = {
        "patient_info": {
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

    interpretations = await interpreter.process_lab_report(lab_report)
    print("Lab Report Interpretations:")
    print(json.dumps(interpretations, indent=2))

    # Generate a narrative report
    report = await interpreter.generate_narrative_report(interpretations, lab_report["patient_info"])
    print("\nNarrative Report:")
    print(report)

    # Initialize and run the API (if needed)
    api = LabReportAPI(interpreter, interpreter.db)
    await api.start()

if __name__ == "__main__":
    asyncio.run(main())


