import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import logging
from typing import Dict, Any, List
from huggingface_hub import hf_hub_download, upload_file
from databases import Database
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData
import asyncio
import aiohttp
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
from database import database, ai_models

class AIModelManager:
    def __init__(self):
        self.models = {
            "health_score": None,
            "health_plan": None
        }
        self.scalers = {
            "health_score": None,
            "health_plan": None
        }
        self.repo_id = os.getenv("HUGGINGFACE_REPO_ID")
        self.api_url = "https://huggingface.co/api/models"
        self.token = os.getenv("HUGGINGFACE_TOKEN")

    async def initialize(self):
        await self.load_models()

    async def load_models(self):
        try:
            for model_name in self.models.keys():
                model_path = await self.download_from_huggingface(f"{model_name}_model.joblib")
                scaler_path = await self.download_from_huggingface(f"{model_name}_scaler.joblib")
                
                self.models[model_name] = joblib.load(model_path)
                self.scalers[model_name] = joblib.load(scaler_path)
                
                logger.info(f"Loaded {model_name} model and scaler successfully")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            self.initialize_default_models()

    def initialize_default_models(self):
        self.models["health_score"] = RandomForestRegressor(n_estimators=100, random_state=42)
        self.models["health_plan"] = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scalers["health_score"] = StandardScaler()
        self.scalers["health_plan"] = StandardScaler()
        logger.info("Initialized default models")

    async def download_from_huggingface(self, filename: str) -> str:
        try:
            return hf_hub_download(repo_id=self.repo_id, filename=filename, token=self.token)
        except Exception as e:
            logger.error(f"Error downloading {filename} from Hugging Face: {str(e)}")
            raise

    async def upload_to_huggingface(self, local_path: str, filename: str):
        try:
            upload_file(
                path_or_fileobj=local_path,
                path_in_repo=filename,
                repo_id=self.repo_id,
                token=self.token
            )
            logger.info(f"Uploaded {filename} to Hugging Face successfully")
        except Exception as e:
            logger.error(f"Error uploading {filename} to Hugging Face: {str(e)}")
            raise

    async def train_models(self):
        try:
            for model_name in self.models.keys():
                logger.info(f"Training {model_name} model")
                data = await self.stream_training_data(f"{model_name}_dataset")
                X = data.drop('target', axis=1)
                y = data['target']
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                self.scalers[model_name] = StandardScaler()
                X_train_scaled = self.scalers[model_name].fit_transform(X_train)
                X_test_scaled = self.scalers[model_name].transform(X_test)

                if model_name == "health_score":
                    self.models[model_name] = RandomForestRegressor(n_estimators=100, random_state=42)
                    self.models[model_name].fit(X_train_scaled, y_train)
                    y_pred = self.models[model_name].predict(X_test_scaled)
                    mse = mean_squared_error(y_test, y_pred)
                    logger.info(f"{model_name} model MSE: {mse}")
                    performance_metric = mse
                elif model_name == "health_plan":
                    self.models[model_name] = RandomForestClassifier(n_estimators=100, random_state=42)
                    self.models[model_name].fit(X_train_scaled, y_train)
                    y_pred = self.models[model_name].predict(X_test_scaled)
                    accuracy = accuracy_score(y_test, y_pred)
                    logger.info(f"{model_name} model accuracy: {accuracy}")
                    performance_metric = accuracy

                # Save models locally
                joblib.dump(self.models[model_name], f"{model_name}_model.joblib")
                joblib.dump(self.scalers[model_name], f"{model_name}_scaler.joblib")

                # Upload models to Hugging Face
                await self.upload_to_huggingface(f"{model_name}_model.joblib", f"{model_name}_model.joblib")
                await self.upload_to_huggingface(f"{model_name}_scaler.joblib", f"{model_name}_scaler.joblib")

                # Update model metadata in the database
                await self.update_model_metadata(model_name, performance_metric)

            logger.info("All models trained and uploaded successfully")
        except Exception as e:
            logger.error(f"Error training models: {str(e)}")
            raise

    async def update_model_metadata(self, model_name: str, performance_metric: float):
        try:
            query = ai_models.insert().values(
                model_name=model_name,
                version=datetime.utcnow().isoformat(),
                performance_metric=performance_metric,
                last_updated=datetime.utcnow()
            )
            await database.execute(query)
            logger.info(f"Updated metadata for {model_name} model")
        except Exception as e:
            logger.error(f"Error updating model metadata: {str(e)}")
            raise

    async def get_model_status(self) -> Dict[str, Any]:
        try:
            status = {}
            for model_name in self.models.keys():
                query = ai_models.select().where(ai_models.c.model_name == model_name).order_by(ai_models.c.last_updated.desc())
                result = await database.fetch_one(query)
                if result:
                    status[model_name] = {
                        "version": result['version'],
                        "performance_metric": result['performance_metric'],
                        "last_updated": result['last_updated']
                    }
                else:
                    status[model_name] = "No data available"
            return status
        except Exception as e:
            logger.error(f"Error getting model status: {str(e)}")
            raise

    async def predict(self, model_name: str, input_data: Dict[str, float]) -> Any:
        try:
            model = self.models.get(model_name)
            scaler = self.scalers.get(model_name)
            if model is None or scaler is None:
                raise ValueError(f"Model or scaler not found for {model_name}")

            feature_order = ['age', 'weight', 'height', 'bmi', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                             'cholesterol', 'glucose', 'steps', 'sleep_hours', 'heart_rate']
            features = [input_data.get(feature, 0) for feature in feature_order]
            features = np.array(features).reshape(1, -1)
            scaled_features = scaler.transform(features)

            prediction = model.predict(scaled_features)[0]
            return prediction
        except Exception as e:
            logger.error(f"Error making prediction with {model_name} model: {str(e)}")
            raise

    async def stream_training_data(self, dataset_name: str) -> pd.DataFrame:
        try:
            chunk_size = 1000
            data_chunks = []

            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/{self.repo_id}/datasets/{dataset_name}", headers={"Authorization": f"Bearer {self.token}"}) as response:
                    while True:
                        chunk = await response.content.read(chunk_size)
                        if not chunk:
                            break
                        data_chunks.append(pd.read_csv(pd.compat.StringIO(chunk.decode())))

            return pd.concat(data_chunks, ignore_index=True)
        except Exception as e:
            logger.error(f"Error streaming training data: {str(e)}")
            raise

    async def evaluate_model_performance(self, model_name: str, test_data: pd.DataFrame) -> float:
        try:
            model = self.models.get(model_name)
            scaler = self.scalers.get(model_name)
            if model is None or scaler is None:
                raise ValueError(f"Model or scaler not found for {model_name}")

            X_test = test_data.drop('target', axis=1)
            y_test = test_data['target']
            X_test_scaled = scaler.transform(X_test)

            if model_name == "health_score":
                y_pred = model.predict(X_test_scaled)
                return mean_squared_error(y_test, y_pred)
            elif model_name == "health_plan":
                y_pred = model.predict(X_test_scaled)
                return accuracy_score(y_test, y_pred)
        except Exception as e:
            logger.error(f"Error evaluating {model_name} model performance: {str(e)}")
            raise

    async def update_model(self, model_name: str):
        try:
            new_data = await self.stream_training_data(f"{model_name}_update_dataset")
            current_model = self.models.get(model_name)
            current_scaler = self.scalers.get(model_name)
            if current_model is None or current_scaler is None:
                raise ValueError(f"Model or scaler not found for {model_name}")

            X_new = new_data.drop('target', axis=1)
            y_new = new_data['target']
            X_new_scaled = current_scaler.transform(X_new)

            current_model.fit(X_new_scaled, y_new)

            joblib.dump(current_model, f"{model_name}_model.joblib")
            await self.upload_to_huggingface(f"{model_name}_model.joblib", f"{model_name}_model.joblib")

            performance_metric = await self.evaluate_model_performance(model_name, new_data)
            await self.update_model_metadata(model_name, performance_metric)

            logger.info(f"Updated {model_name} model with new data")
        except Exception as e:
            logger.error(f"Error updating {model_name} model: {str(e)}")
            raise

    async def get_feature_importance(self, model_name: str) -> Dict[str, float]:
        try:
            model = self.models.get(model_name)
            if model is None:
                raise ValueError(f"Model not found for {model_name}")

            feature_order = ['age', 'weight', 'height', 'bmi', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                             'cholesterol', 'glucose', 'steps', 'sleep_hours', 'heart_rate']
            
            importance = model.feature_importances_
            return dict(zip(feature_order, importance))
        except Exception as e:
            logger.error(f"Error getting feature importance for {model_name} model: {str(e)}")
            raise

# Initialize the AIModelManager
ai_model_manager = AIModelManager()

# Startup and shutdown events
async def startup_event():
    await database.connect()
    await ai_model_manager.initialize()

async def shutdown_event():
    await database.disconnect()
