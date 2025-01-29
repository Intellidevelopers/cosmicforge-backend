# AILabInterpreter.py

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
            "patient_friendly_explanation": llm_result["patient_friendly_explanation"],
            "recommendations": llm_result["recommendations"],
            "trend_analysis": llm_result["trend_analysis"],
            "differential_diagnosis": llm_result["differential_diagnosis"],
            "confidence_score": self.calculate_confidence_score(combined_interpretation, llm_result["enhanced_interpretation"])
        }

        # Post-process the final result
        final_result = await self.post_process_interpretation(final_result)

        # Apply ethical AI checks
        final_result = await self.ethical_ai_wrapper(final_result)

        # Cache the interpretation
        self.interpretation_cache[cache_key] = final_result

        return final_result

    except Exception as e:
        self.logger.error(f"Error in interpret_lab_results: {str(e)}")
        return {
            "error": "We apologize, but an error occurred while interpreting the lab results. Please consult with your healthcare provider for accurate interpretation."
        }

    def generate_interpretation_prompt(self, test_name: str, value: float, reference_range: Dict[str, float], patient_info: Dict[str, Any]) -> str:
        prompt = f"Interpret the following lab result:\n"
        prompt += f"Test: {test_name}\n"
        prompt += f"Value: {value} {reference_range['unit']}\n"
        prompt += f"Reference Range: {reference_range['low']} - {reference_range['high']} {reference_range['unit']}\n"
        prompt += f"Patient Age: {patient_info.get('age', 'Unknown')}\n"
        prompt += f"Patient Gender: {patient_info.get('gender', 'Unknown')}\n"
        prompt += f"Patient Medical History: {patient_info.get('medical_history', 'Unknown')}\n"
        prompt += "Provide a clear and concise interpretation of this result, including its potential clinical significance."
        return prompt

    async def generate_report(self, lab_results: Dict[str, Any]) -> str:
        interpretations = await self.process_lab_report(lab_results)
        report_template = self.jinja_env.get_template('lab_report_template.html')
        report = report_template.render(
            patient_name=lab_results['patient_info']['name'],
            date=datetime.now().strftime("%Y-%m-%d"),
            results=lab_results['results'],
            interpretations=interpretations
        )
        return report

    async def save_report(self, report: str, patient_id: str) -> str:
        filename = f"report_{patient_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.html"
        try:
            await self.s3.put_object(Bucket='your-report-bucket', Key=filename, Body=report)
            return f"https://your-report-bucket.s3.amazonaws.com/{filename}"
        except Exception as e:
            self.logger.error(f"Error saving report to S3: {e}")
            return None

    async def process_expanded_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        expanded_data = await process_expanded_input(input_data)
        return expanded_data

    @ethical_ai_wrapper
    async def interpret_with_ethical_considerations(self, test_name: str, value: float, patient_info: Dict[str, Any]) -> str:
        interpretation = await self.interpret_lab_result(test_name, value, patient_info)
        return interpretation

    async def train_federated_model(self, local_data: List[Dict[str, Any]]):
        global_model = await train_federated_model(local_data)
        self.federated_model = global_model

    async def predict_with_federated_model(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        prediction = await predict_with_federated_model(self.federated_model, input_data)
        return prediction

    async def schedule_lab_test_expansion(self):
        self.scheduler.schedule(
            scheduled_time=datetime.utcnow(),
            func=self.expand_lab_tests,
            interval=86400  # Run daily
        )

    async def expand_lab_tests(self):
        async with self.AsyncSession() as session:
            result = await session.execute(select(LabTest))
            lab_tests = result.scalars().all()

        for test in lab_tests:
            expanded_info = await self.get_expanded_test_info(test.test_name)
            if expanded_info:
                await self.update_lab_test_expansion(test.test_name, expanded_info)

    async def get_expanded_test_info(self, test_name: str) -> Dict[str, Any]:
        prompt = f"Provide detailed information about the lab test: {test_name}. Include its purpose, normal ranges, and potential implications of abnormal results."
        try:
            response = await self.call_gpt4(prompt)
            expanded_info = json.loads(response)
            return expanded_info
        except Exception as e:
            self.logger.error(f"Error getting expanded info for {test_name}: {e}")
            return None

    async def update_lab_test_expansion(self, test_name: str, expanded_info: Dict[str, Any]):
        async with self.AsyncSession() as session:
            try:
                expansion = LabTestExpansion(
                    test_name=test_name,
                    category=expanded_info.get('category', ''),
                    reference_range=json.dumps(expanded_info.get('reference_range', {})),
                    units=expanded_info.get('units', ''),
                    description=expanded_info.get('description', ''),
                    last_updated=datetime.utcnow()
                )
                session.merge(expansion)
                await session.commit()
            except SQLAlchemyError as e:
                self.logger.error(f"Database error during lab test expansion update: {e}")
                await session.rollback()

    async def load_models(self):
        self.interpretation_model = await load_model('interpretation_model.joblib')
        self.recommendation_model = await load_model('recommendation_model.joblib')

    async def save_models(self):
        await save_model(self.interpretation_model, 'interpretation_model.joblib')
        await save_model(self.recommendation_model, 'recommendation_model.joblib')

    async def train_models(self, training_data: List[TrainingData]):
        X = [data.features for data in training_data]
        y_interp = [data.interpretation for data in training_data]
        y_recom = [data.recommendation for data in training_data]

        X = self.imputer.fit_transform(X)
        X = self.scaler.fit_transform(X)

        self.interp_encoder.fit(y_interp)
        self.recom_encoder.fit(y_recom)

        y_interp_encoded = self.interp_encoder.transform(y_interp)
        y_recom_encoded = self.recom_encoder.transform(y_recom)

        self.interpretation_model.fit(X, y_interp_encoded)
        self.recommendation_model.fit(X, y_recom_encoded)

        await self.save_models()

    async def predict(self, features: List[float]) -> Tuple[str, str]:
        features = self.imputer.transform([features])
        features = self.scaler.transform(features)

        interp_pred = self.interpretation_model.predict(features)
        recom_pred = self.recommendation_model.predict(features)

        interpretation = self.interp_encoder.inverse_transform(interp_pred)[0]
        recommendation = self.recom_encoder.inverse_transform(recom_pred)[0]

        return interpretation, recommendation

    async def initialize_federated_model(self):
        initial_data = await load_initial_data()
        self.federated_model = FederatedLearning(EnsembleModel())
        await self.federated_model.initialize(initial_data)
        return self.federated_model

    async def update_federated_model(self, local_data: List[Dict[str, Any]]):
        current_time = asyncio.get_event_loop().time()
        if current_time - self.last_federated_update >= self.federated_update_interval:
            prepared_data = await prepare_data_for_federated_learning(local_data)
            await self.federated_model.update(prepared_data)
            self.last_federated_update = current_time

    async def get_bert_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()[0]

    async def semantic_search(self, query: str, corpus: List[str], top_k: int = 5) -> List[Tuple[int, float]]:
        query_embedding = await self.get_bert_embedding(query)
        corpus_embeddings = np.array([await self.get_bert_embedding(doc) for doc in corpus])
        similarities = cosine_similarity([query_embedding], corpus_embeddings)[0]
        top_indices = similarities.argsort()[-top_k:][::-1]
        return [(idx, similarities[idx]) for idx in top_indices]

    async def preprocess_text(self, text: str) -> str:
        text = text.lower()
        tokens = word_tokenize(text)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)

    async def extract_medical_entities(self, text: str) -> List[Tuple[str, str]]:
        doc = self.nlp(text)
        return [(ent.text, ent.label_) for ent in doc.ents if ent.label_ in ['DISEASE', 'CHEMICAL', 'BODY_PART']]

    async def generate_lab_report(self, lab_results: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        interpretations = await self.process_lab_report(lab_results)
        
        report = f"Lab Report for {patient_info['name']} (ID: {patient_info['id']})\n"
        report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for test_name, value in lab_results['results'].items():
            report += f"{test_name}: {value}\n"
            report += f"Interpretation: {interpretations[test_name]}\n\n"
        
        report += "This report is generated by an AI system and should be reviewed by a healthcare professional."
        
        return report

    async def save_feedback(self, feedback_data: Dict[str, Any]):
        async with self.AsyncSession() as session:
            try:
                feedback = FeedbackEntry(
                    lab_test_id=feedback_data['lab_test_id'],
                    original_interpretation=feedback_data['original_interpretation'],
                    corrected_interpretation=feedback_data['corrected_interpretation'],
                    feedback_provider=feedback_data['feedback_provider'],
                    confidence_score=feedback_data['confidence_score']
                )
                session.add(feedback)
                await session.commit()
            except SQLAlchemyError as e:
                self.logger.error(f"Database error during feedback saving: {e}")
                await session.rollback()

    async def process_voice_input(self, audio_file_path: str) -> str:
        return await self.voice_interface.transcribe(audio_file_path)

    async def generate_voice_response(self, text: str) -> str:
        return await self.voice_interface.synthesize(text)

    async def translate(self, text: str, target_language: str) -> str:
        return await self.language_processor.translate(text, target_language)

    async def continuous_learning_update(self, new_data: List[Dict[str, Any]]):
        await self.continuous_learning.update(new_data)

    async def llm_interpret(self, lab_result: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        return await self.llm_interpreter.interpret(lab_result, patient_info)

    async def close(self):
        await self.engine.dispose()

