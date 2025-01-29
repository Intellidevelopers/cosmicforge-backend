import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List
import logging
from tenacity import retry, stop_after_attempt, wait_random_exponential
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import sent_tokenize
import openai

class LLMInterpreter:
    def __init__(self, fetch_medical_guidelines):
        self.logger = logging.getLogger(__name__)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.base_delay = float(os.getenv('BASE_DELAY', 1))
        self.max_delay = float(os.getenv('MAX_DELAY', 60))
        
        # Load pre-trained BERT model for semantic similarity
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')
        self.model = AutoModel.from_pretrained('bert-base-uncased')
        
        # Initialize cache for API calls
        self.cache = {}
        
        # Store the fetch_medical_guidelines function
        self.fetch_medical_guidelines = fetch_medical_guidelines

    @retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=60))
    async def call_gpt4(self, prompt: str) -> str:
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a highly knowledgeable medical AI assistant specializing in interpreting lab results."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                n=1,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error(f"Error calling GPT-4 API: {str(e)}")
            raise

    async def enhance_interpretation(self, combined_interpretation: Dict[str, Any], llm_interpretation: str) -> Dict[str, Any]:
        enhanced = {}
        for test, interp in combined_interpretation.items():
            enhanced[test] = {
                "model_interpretation": interp,
                "llm_interpretation": self.extract_relevant_part(llm_interpretation, test),
                "confidence_score": self.calculate_confidence(interp, self.extract_relevant_part(llm_interpretation, test))
            }
        return enhanced

    def extract_relevant_part(self, full_text: str, test_name: str) -> str:
        sentences = sent_tokenize(full_text)
        relevant_sentences = [s for s in sentences if test_name.lower() in s.lower()]
        return " ".join(relevant_sentences) if relevant_sentences else ""

    def calculate_confidence(self, model_interp: str, llm_interp: str) -> float:
        model_embedding = self.get_bert_embedding(model_interp)
        llm_embedding = self.get_bert_embedding(llm_interp)
        similarity = cosine_similarity(model_embedding, llm_embedding)[0][0]
        return (similarity + 1) / 2  # Normalize to 0-1 range

    def get_bert_embedding(self, text: str) -> np.ndarray:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).numpy()

    async def generate_explanation(self, enhanced_interpretation: Dict[str, Any]) -> str:
        explanation_prompt = self.create_explanation_prompt(enhanced_interpretation)
        explanation = await self.call_gpt4(explanation_prompt)
        return explanation

    def create_explanation_prompt(self, enhanced_interpretation: Dict[str, Any]) -> str:
        prompt = "Based on the following enhanced interpretations of lab results, provide a clear, concise, and patient-friendly explanation:\n\n"
        for test, data in enhanced_interpretation.items():
            prompt += f"Test: {test}\n"
            prompt += f"Interpretation: {data['llm_interpretation']}\n"
            prompt += f"Confidence: {data['confidence_score']:.2f}\n\n"
        prompt += "Please explain these results in simple terms, highlighting any areas of concern and suggesting any necessary follow-up actions."
        return prompt

    async def generate_recommendation(self, enhanced_interpretation: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        recommendation_prompt = self.create_recommendation_prompt(enhanced_interpretation, patient_info)
        recommendation = await self.call_gpt4(recommendation_prompt)
        return recommendation

    def create_recommendation_prompt(self, enhanced_interpretation: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        prompt = "Based on the following lab results and patient information, provide medical recommendations:\n\n"
        prompt += f"Patient Info: {json.dumps(patient_info, indent=2)}\n\n"
        prompt += "Lab Results:\n"
        for test, data in enhanced_interpretation.items():
            prompt += f"Test: {test}\n"
            prompt += f"Interpretation: {data['llm_interpretation']}\n"
            prompt += f"Confidence: {data['confidence_score']:.2f}\n\n"
        prompt += "Please provide specific recommendations for follow-up actions, lifestyle changes, or additional tests if necessary. Consider the patient's medical history and current condition in your recommendations."
        return prompt

    async def analyze_trends(self, historical_results: List[Dict[str, Any]]) -> str:
        trend_prompt = self.create_trend_prompt(historical_results)
        trend_analysis = await self.call_gpt4(trend_prompt)
        return trend_analysis

    def create_trend_prompt(self, historical_results: List[Dict[str, Any]]) -> str:
        prompt = "Analyze the following historical lab results and provide insights on trends:\n\n"
        for result in historical_results:
            prompt += f"Date: {result['date']}\n"
            for test, value in result['results'].items():
                prompt += f"{test}: {value}\n"
            prompt += "\n"
        prompt += "Please identify any significant trends, improvements, or deteriorations in the patient's condition based on these historical results. Highlight any areas that require attention or further investigation."
        return prompt

    async def generate_differential_diagnosis(self, enhanced_interpretation: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        diagnosis_prompt = self.create_differential_diagnosis_prompt(enhanced_interpretation, patient_info)
        differential_diagnosis = await self.call_gpt4(diagnosis_prompt)
        return differential_diagnosis

    def create_differential_diagnosis_prompt(self, enhanced_interpretation: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        prompt = "Based on the following lab results and patient information, provide a differential diagnosis:\n\n"
        prompt += f"Patient Info: {json.dumps(patient_info, indent=2)}\n\n"
        prompt += "Lab Results:\n"
        for test, data in enhanced_interpretation.items():
            prompt += f"Test: {test}\n"
            prompt += f"Interpretation: {data['llm_interpretation']}\n"
            prompt += f"Confidence: {data['confidence_score']:.2f}\n\n"
        prompt += "Please provide a list of potential diagnoses that could explain these lab results and patient symptoms. Rank them in order of likelihood and provide a brief explanation for each."
        return prompt

    async def integrate_guidelines(self, enhanced_interpretation: Dict[str, Any], guidelines: Dict[str, str]) -> Dict[str, Any]:
        for test, data in enhanced_interpretation.items():
            if test in guidelines:
                data['guideline'] = guidelines[test]
        return enhanced_interpretation

    async def process_lab_results(self, lab_results: Dict[str, Any], patient_info: Dict[str, Any], historical_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        initial_prompt = self.create_initial_prompt(lab_results, patient_info)
        llm_interpretation = await self.call_gpt4(initial_prompt)

        enhanced_interpretation = await self.enhance_interpretation(lab_results, llm_interpretation)

        explanation = await self.generate_explanation(enhanced_interpretation)

        recommendations = await self.generate_recommendation(enhanced_interpretation, patient_info)

        trend_analysis = await self.analyze_trends(historical_results) if historical_results else None

        differential_diagnosis = await self.generate_differential_diagnosis(enhanced_interpretation, patient_info)

        guidelines = await self.fetch_medical_guidelines(list(lab_results.keys()))
        enhanced_interpretation = await self.integrate_guidelines(enhanced_interpretation, guidelines)

        return {
            "enhanced_interpretation": enhanced_interpretation,
            "patient_friendly_explanation": explanation,
            "recommendations": recommendations,
            "trend_analysis": trend_analysis,
            "differential_diagnosis": differential_diagnosis
        }

    def create_initial_prompt(self, lab_results: Dict[str, Any], patient_info: Dict[str, Any]) -> str:
        prompt = "Interpret the following lab results for a patient with the given information:\n\n"
        prompt += f"Patient Info: {json.dumps(patient_info, indent=2)}\n\n"
        prompt += "Lab Results:\n"
        for test, value in lab_results.items():
            prompt += f"{test}: {value}\n"
        prompt += "\nPlease provide a detailed medical interpretation of these results, considering the patient's information."
        return prompt
