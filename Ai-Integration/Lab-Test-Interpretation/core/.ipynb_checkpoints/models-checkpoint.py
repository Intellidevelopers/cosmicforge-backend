# core/models.py

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
        reliability_weights = [1 / (score + 1e-8) for score in brier_scores]  # Avoid division by zero
        
        combined_conf = sum(conf * weight for conf, weight in zip(confidences, reliability_weights))
        combined_conf /= sum(reliability_weights)
        
        return combined_conf
    except Exception as e:
        self.logger.error(f"Error in combine_confidences: {str(e)}")
        raise

def apply_domain_rules(self, interp: str, rec: str, conf: float, features: np.array) -> Tuple[str, str, float]:
    try:
        # Apply domain-specific rules to refine the ensemble prediction
        if self.is_critical_value(features):
            interp = f"CRITICAL: {interp}"
            conf = max(conf, 0.95)  # Increase confidence for critical values
        
        if self.is_contradictory(interp, rec):
            self.logger.warning(f"Contradictory interpretation and recommendation detected: {interp}, {rec}")
            conf *= 0.9  
        
        return interp, rec, conf
    except Exception as e:
        self.logger.error(f"Error in apply_domain_rules: {str(e)}")
        raise

def log_ensemble_decision(self, features: np.array, interpretations: List[str], 
                          recommendations: List[str], confidences: List[float], 
                          final_interp: str, final_rec: str, final_conf: float):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "features": features.tolist(),
            "individual_interpretations": interpretations,
            "individual_recommendations": recommendations,
            "individual_confidences": confidences,
            "final_interpretation": final_interp,
            "final_recommendation": final_rec,
            "final_confidence": final_conf
        }
        
        # Asynchronously log the decision
        asyncio.create_task(self.async_log_to_database(log_entry))
    except Exception as e:
        self.logger.error(f"Error in log_ensemble_decision: {str(e)}")
        
    @ethical_ai_wrapper
    async def interpret_lab_result(self, test_name: str, value: float) -> Dict[str, Any]:
        try:
            features = np.array([[value]])
            features = self.imputer.transform(features)
            features = self.scaler.transform(features)
            
            interpretation, recommendation, confidence = self.ensemble_model(features)
            
            # Check for critical results
            is_critical = await check_critical_results(test_name, value)
            if is_critical:
                await send_alert(test_name, value, interpretation)
            
            # Get expanded context
            context = await self.get_expanded_info(test_name)
            
            result = {
                'test_name': test_name,
                'value': value,
                'interpretation': interpretation,
                'recommendation': recommendation,
                'confidence': confidence,
                'is_critical': is_critical,
                'context': context
            }
            
            # Log the interpretation for continuous learning
            await self.continuous_learning.log_interpretation(result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error in interpret_lab_result: {str(e)}")
            raise

    async def process_lab_report(self, report_path: str) -> List[Dict[str, Any]]:
        try:
            # Extract text from the lab report (PDF or image)
            if report_path.endswith('.pdf'):
                text = self.extract_text_from_pdf(report_path)
            else:
                text = self.extract_text_from_image(report_path)
            
            # Process the extracted text
            lab_results = self.parse_lab_results(text)
            
            interpretations = []
            for result in lab_results:
                interpretation = await self.interpret_lab_result(result['test_name'], result['value'])
                interpretations.append(interpretation)
            
            return interpretations
        except Exception as e:
            self.logger.error(f"Error in process_lab_report: {str(e)}")
            raise

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        try:
            text = ""
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def extract_text_from_image(self, image_path: str) -> str:
        try:
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray)
            return text
        except Exception as e:
            self.logger.error(f"Error extracting text from image: {str(e)}")
            raise

def parse_lab_results(self, text: str) -> List[Dict[str, Any]]:
    try:
        results = []
        lines = text.split('\n')
        current_section = None
        current_test = {}

        # Regular expressions for different patterns
        section_pattern = re.compile(r'^([\w\s]+):$')
        test_pattern = re.compile(r'^(\w+(?:\s+\w+)*)\s*:\s*([\d.]+)\s*(\w+/?\w*)?(?:\s*\(([^)]+)\))?$')
        reference_pattern = re.compile(r'Reference Range:\s*([\d.-]+)\s*-\s*([\d.-]+)')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line is a new section
            section_match = section_pattern.match(line)
            if section_match:
                current_section = section_match.group(1)
                continue

            # Check if this line is a test result
            test_match = test_pattern.match(line)
            if test_match:
                if current_test:
                    results.append(current_test)
                current_test = {
                    'section': current_section,
                    'test_name': test_match.group(1),
                    'value': float(test_match.group(2)),
                    'unit': test_match.group(3) if test_match.group(3) else '',
                    'flag': test_match.group(4) if test_match.group(4) else ''
                }
                continue

            # Check if this line is a reference range
            ref_match = reference_pattern.search(line)
            if ref_match and current_test:
                current_test['reference_low'] = float(ref_match.group(1))
                current_test['reference_high'] = float(ref_match.group(2))

        # Add the last test if exists
        if current_test:
            results.append(current_test)

        return results
    except Exception as e:
        self.logger.error(f"Error parsing lab results: {str(e)}")
        raise
  @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    async def get_llm_interpretation(self, test_name: str, value: float, context: Dict[str, Any]) -> str:
        try:
            prompt = f"Interpret the following lab test result:\nTest: {test_name}\nValue: {value}\nContext: {json.dumps(context)}"
            response = await openai.Completion.acreate(
                engine="text-davinci-002",
                prompt=prompt,
                max_tokens=150,
                n=1,
                stop=None,
                temperature=0.5,
            )
            return response.choices[0].text.strip()
        except Exception as e:
            self.logger.error(f"Error getting LLM interpretation: {str(e)}")
            raise

    async def handle_voice_input(self, audio_file_path: str) -> Dict[str, Any]:
        try:
            text = await self.voice_interface.transcribe(audio_file_path)
            processed_input = await process_expanded_input(text)
            interpretation = await self.interpret_lab_result(processed_input['test_name'], processed_input['value'])
            voice_response = await self.voice_interface.synthesize(interpretation['interpretation'])
            return {
                'transcription': text,
                'interpretation': interpretation,
                'voice_response': voice_response
            }
        except Exception as e:
            self.logger.error(f"Error handling voice input: {str(e)}")
            raise

    async def translate_interpretation(self, interpretation: str, target_language: str) -> str:
        try:
            translated_text = await self.language_processor.translate(interpretation, target_language)
            return translated_text
        except Exception as e:
            self.logger.error(f"Error translating interpretation: {str(e)}")
            raise

    async def generate_report(self, interpretations: List[Dict[str, Any]], format: str = 'pdf') -> str:
        try:
            if format == 'pdf':
                report_path = f"reports/lab_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                await self.generate_pdf_report(interpretations, report_path)
            elif format == 'json':
                report_path = f"reports/lab_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
                await self.generate_json_report(interpretations, report_path)
            else:
                raise ValueError(f"Unsupported report format: {format}")
            
            return report_path
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            raise
     
async def generate_pdf_report(self, interpretations: List[Dict[str, Any]], report_path: str) -> None:
    try:
        doc = SimpleDocTemplate(report_path, pagesize=letter,
                                rightMargin=72, leftMargin=72,
                                topMargin=72, bottomMargin=18)

        story = []
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Heading1', fontSize=16, spaceAfter=12))
        styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceBefore=12, spaceAfter=6))
        styles.add(ParagraphStyle(name='BodyText', fontSize=11, spaceBefore=6, spaceAfter=6))

        # Title
        story.append(Paragraph("Laboratory Test Results Report", styles['Heading1']))
        story.append(Spacer(1, 12))

        # Patient Information (if it's available in the first interpretation)
        if interpretations:
            patient_info = interpretations[0].get('patient_info', {})
            patient_data = [
                ["Patient Name:", patient_info.get('name', 'N/A')],
                ["Patient ID:", patient_info.get('id', 'N/A')],
                ["Date of Birth:", patient_info.get('dob', 'N/A')],
                ["Report Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            ]
            patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
            patient_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (1, 0), (-1, -1), colors.beige),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 12))

        # Test Results
        story.append(Paragraph("Test Results", styles['Heading2']))
        for interp in interpretations:
            story.append(Paragraph(f"{interp['test_name']}", styles['Heading2']))
            result_data = [
                ["Value:", f"{interp['value']} {interp.get('unit', '')}"],
                ["Reference Range:", f"{interp.get('reference_low', 'N/A')} - {interp.get('reference_high', 'N/A')}"],
                ["Status:", interp.get('status', 'N/A')],
            ]
            result_table = Table(result_data, colWidths=[2*inch, 4*inch])
            result_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (1, 0), (-1, -1), colors.white),
            ]))
            story.append(result_table)
            story.append(Spacer(1, 6))
            story.append(Paragraph("Interpretation:", styles['BodyText']))
            story.append(Paragraph(interp['interpretation'], styles['BodyText']))
            story.append(Paragraph("Recommendation:", styles['BodyText']))
            story.append(Paragraph(interp['recommendation'], styles['BodyText']))
            story.append(Spacer(1, 12))

        # Disclaimer
        story.append(Paragraph("Disclaimer:", styles['Heading2']))
        disclaimer_text = ("This report is generated by an AI-assisted system and should be reviewed by a qualified healthcare professional. "
                           "It is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of your "
                           "physician or other qualified health provider with any questions you may have regarding a medical condition.")
        story.append(Paragraph(disclaimer_text, styles['BodyText']))

        # Build the PDF
        await asyncio.to_thread(doc.build, story)

        self.logger.info(f"PDF report generated successfully: {report_path}")
    except Exception as e:
        self.logger.error(f"Error generating PDF report: {str(e)}")
        raise

    async def generate_json_report(self, interpretations: List[Dict[str, Any]], report_path: str) -> None:
        try:
            async with aiofiles.open(report_path, mode='w') as f:
                await f.write(json.dumps(interpretations, indent=2))
        except Exception as e:
            self.logger.error(f"Error generating JSON report: {str(e)}")
            raise

# Initialize the models
models = Models()
asyncio.run(models.initialize())

        