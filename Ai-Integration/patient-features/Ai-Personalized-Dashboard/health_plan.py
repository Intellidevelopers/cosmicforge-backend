import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Dict, Any, List
import joblib
import logging
from huggingface_hub import hf_hub_download
from database import database, health_plans, user_feedback, health_data
import json
from datetime import datetime
from fastapi import HTTPException
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HealthPlanGenerator:
    def __init__(self):
        self.model = self.load_model()
        self.scaler = self.load_scaler()
        self.repo_id = os.getenv("HEALTH_PLAN_MODEL_REPO")

    def load_model(self):
        try:
            model_path = hf_hub_download(repo_id=self.repo_id, filename="model.joblib")
            return joblib.load(model_path)
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            return RandomForestClassifier(n_estimators=100, random_state=42)

    def load_scaler(self):
        try:
            scaler_path = hf_hub_download(repo_id=self.repo_id, filename="scaler.joblib")
            return joblib.load(scaler_path)
        except Exception as e:
            logger.error(f"Error loading scaler: {str(e)}")
            return StandardScaler()

    async def generate_plan(self, user_data: Dict[str, float]) -> Dict[str, Any]:
        try:
            features = self.preprocess_data(user_data)
            plan_code = self.model.predict(features)[0]
            plan = self.decode_plan(plan_code)
            await self.store_plan(user_data['user_id'], plan)
            return plan
        except Exception as e:
            logger.error(f"Error generating health plan: {str(e)}")
            return await self.generate_fallback_plan(user_data)

    def preprocess_data(self, user_data: Dict[str, float]) -> np.ndarray:
        feature_order = ['age', 'weight', 'height', 'bmi', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                         'cholesterol', 'glucose', 'smoking', 'alcohol_consumption', 'physical_activity']
        
        features = [user_data.get(feature, 0) for feature in feature_order]
        features = np.array(features).reshape(1, -1)
        return self.scaler.transform(features)

    def decode_plan(self, plan_code: int) -> Dict[str, Any]:
        plan_types = ["diet", "exercise", "chronic_condition"]
        plan_details = {}
        for i, plan_type in enumerate(plan_types):
            plan_details[plan_type] = self.decode_plan_component(plan_code, plan_type)
        return plan_details

    def decode_plan_component(self, plan_code: int, plan_type: str) -> Dict[str, Any]:
        if plan_type == "diet":
            return self.decode_diet_plan(plan_code)
        elif plan_type == "exercise":
            return self.decode_exercise_plan(plan_code)
        elif plan_type == "chronic_condition":
            return self.decode_chronic_condition_plan(plan_code)
        else:
            logger.warning(f"Unknown plan type: {plan_type}")
            return {}

    def decode_diet_plan(self, plan_code: int) -> Dict[str, Any]:
        diet_plans = {
            0: {"name": "Balanced Diet", "calorie_target": 2000, "macronutrient_ratio": "40/30/30"},
            1: {"name": "Low-Carb Diet", "calorie_target": 1800, "macronutrient_ratio": "20/40/40"},
            2: {"name": "Mediterranean Diet", "calorie_target": 2200, "macronutrient_ratio": "45/35/20"},
            3: {"name": "Plant-Based Diet", "calorie_target": 2000, "macronutrient_ratio": "50/30/20"}
        }
        return diet_plans.get(plan_code % len(diet_plans), diet_plans[0])

    def decode_exercise_plan(self, plan_code: int) -> Dict[str, Any]:
        exercise_plans = {
            0: {"name": "Beginner Fitness", "weekly_target": 150, "focus": "Cardio"},
            1: {"name": "Intermediate Fitness", "weekly_target": 225, "focus": "Mixed"},
            2: {"name": "Advanced Fitness", "weekly_target": 300, "focus": "Strength"},
            3: {"name": "High-Intensity Training", "weekly_target": 200, "focus": "HIIT"}
        }
        return exercise_plans.get(plan_code % len(exercise_plans), exercise_plans[0])

    def decode_chronic_condition_plan(self, plan_code: int) -> Dict[str, Any]:
        chronic_condition_plans = {
            0: {"name": "General Health", "focus": "Preventive Care"},
            1: {"name": "Diabetes Management", "focus": "Blood Sugar Control"},
            2: {"name": "Heart Health", "focus": "Cardiovascular Fitness"},
            3: {"name": "Weight Management", "focus": "Calorie Control"}
        }
        return chronic_condition_plans.get(plan_code % len(chronic_condition_plans), chronic_condition_plans[0])

    async def generate_fallback_plan(self, user_data: Dict[str, float]) -> Dict[str, Any]:
        logger.info("Generating fallback health plan")
        fallback_plan = {
            "diet": self.decode_diet_plan(0),
            "exercise": self.decode_exercise_plan(0),
            "chronic_condition": self.decode_chronic_condition_plan(0)
        }
        await self.store_plan(user_data['user_id'], fallback_plan)
        return fallback_plan

    async def store_plan(self, user_id: int, plan: Dict[str, Any]):
        try:
            query = health_plans.insert().values(
                user_id=user_id,
                plan_type="comprehensive",
                details=json.dumps(plan),
                created_at=datetime.utcnow()
            )
            await database.execute(query)
        except Exception as e:
            logger.error(f"Error storing health plan: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to store health plan")

    async def get_user_plan(self, user_id: int) -> Dict[str, Any]:
        query = health_plans.select().where(health_plans.c.user_id == user_id).order_by(health_plans.c.created_at.desc())
        result = await database.fetch_one(query)
        if result:
            return json.loads(result['details'])
        else:
            logger.warning(f"No health plan found for user {user_id}")
            return None

    async def update_plan(self, user_id: int, updated_plan: Dict[str, Any]):
        try:
            query = health_plans.update().where(health_plans.c.user_id == user_id).values(
                details=json.dumps(updated_plan),
                created_at=datetime.utcnow()
            )
            await database.execute(query)
        except Exception as e:
            logger.error(f"Error updating health plan: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update health plan")

    async def train_model(self, training_data: pd.DataFrame):
        try:
            X = training_data.drop('plan_code', axis=1)
            y = training_data['plan_code']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train_scaled, y_train)

            accuracy = self.model.score(X_test_scaled, y_test)
            logger.info(f"Model trained with accuracy: {accuracy}")

            # Save the model and scaler
            joblib.dump(self.model, 'model.joblib')
            joblib.dump(self.scaler, 'scaler.joblib')
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to train model")

    async def evaluate_plan(self, user_id: int, plan: Dict[str, Any]) -> float:
        try:
            feedback = await self.get_user_feedback(user_id)
            health_data = await self.get_user_health_data(user_id)

            adherence_score = self.calculate_adherence_score(feedback)
            health_improvement_score = self.calculate_health_improvement_score(health_data)

            effectiveness_score = (adherence_score + health_improvement_score) / 2
            return effectiveness_score
        except Exception as e:
            logger.error(f"Error evaluating plan: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to evaluate plan")

    async def get_user_feedback(self, user_id: int) -> List[Dict[str, Any]]:
        query = user_feedback.select().where(user_feedback.c.user_id == user_id)
        results = await database.fetch_all(query)
        return [dict(result) for result in results]

    async def get_user_health_data(self, user_id: int) -> List[Dict[str, Any]]:
        query = health_data.select().where(health_data.c.user_id == user_id)
        results = await database.fetch_all(query)
        return [dict(result) for result in results]

    def calculate_adherence_score(self, feedback: List[Dict[str, Any]]) -> float:
        if not feedback:
            return 0.5  # Default score if no feedback

        adherence_scores = [f['adherence_rating'] for f in feedback if 'adherence_rating' in f]
        return sum(adherence_scores) / len(adherence_scores) if adherence_scores else 0.5

    def calculate_health_improvement_score(self, health_data: List[Dict[str, Any]]) -> float:
        if not health_data:
            return 0.5  # Default score if no health data

        # Calculate health improvement based on the most recent and oldest health data points
        oldest_data = min(health_data, key=lambda x: x['timestamp'])
        newest_data = max(health_data, key=lambda x: x['timestamp'])

        improvement_factors = {
            'weight': -1,  # Negative because lower is better
            'blood_pressure_systolic': -1,
            'blood_pressure_diastolic': -1,
            'cholesterol': -1,
            'glucose': -1
        }

        total_improvement = 0
        factors_count = 0

        for factor, direction in improvement_factors.items():
            if factor in oldest_data and factor in newest_data:
                change = (newest_data[factor] - oldest_data[factor]) * direction
                total_improvement += 1 if change < 0 else (0 if change == 0 else -1)
                factors_count += 1

        return (total_improvement / factors_count + 1) / 2 if factors_count > 0 else 0.5

    async def adjust_plan(self, user_id: int, feedback: Dict[str, Any]):
        try:
            current_plan = await self.get_user_plan(user_id)
            if not current_plan:
                logger.warning(f"No existing plan found for user {user_id}")
                raise HTTPException(status_code=404, detail="No existing plan found")

            for component, component_feedback in feedback.items():
                if component in current_plan:
                    current_plan[component] = self.adjust_component(current_plan[component], component_feedback)

            await self.update_plan(user_id, current_plan)
            logger.info(f"Plan adjusted for user {user_id}")
        except Exception as e:
            logger.error(f"Error adjusting plan: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to adjust plan")

    def adjust_component(self, component: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        for key, value in feedback.items():
            if key in component:
                if isinstance(component[key], (int, float)) and isinstance(value, (int, float)):
                    component[key] = (component[key] + value) / 2
                elif isinstance(component[key], str):
                    component[key] = value
        return component

    async def get_plan_history(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            query = health_plans.select().where(health_plans.c.user_id == user_id).order_by(health_plans.c.created_at.desc())
            results = await database.fetch_all(query)
            return [{"created_at": result['created_at'], "plan": json.loads(result['details'])} for result in results]
        except Exception as e:
            logger.error(f"Error fetching plan history: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch plan history")

# Initialize the HealthPlanGenerator
health_plan_generator = HealthPlanGenerator()

# Startup and shutdown events
async def startup_event():
    await database.connect()

async def shutdown_event():
    await database.disconnect()
