import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from databases import Database
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, JSON
from sqlalchemy.sql import select, insert, update, delete
import json
from pydantic import BaseModel, validator
from fastapi import HTTPException
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import aiocache
from aiocache import Cache
from aiocache.serializers import PickleSerializer

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
from database import database, health_data, data_source_settings

# Encryption key for sensitive data
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY environment variable is not set")
fernet = Fernet(ENCRYPTION_KEY.encode())

# Cache setup
cache = Cache(Cache.MEMORY, serializer=PickleSerializer())

class HealthDataPoint(BaseModel):
    user_id: int
    data_type: str
    value: float
    timestamp: datetime

    @validator('value')
    def validate_value(cls, v):
        if not isinstance(v, (int, float)):
            raise ValueError('Value must be a number')
        return v

class DataSourceSettings(BaseModel):
    user_id: int
    data_type: str
    settings: Dict[str, Any]

class DataIntegrationEngine:
    def __init__(self):
        self.data_sources = {
            "wearables": self.fetch_wearable_data,
            "ehr": self.fetch_ehr_data,
            "lab_results": self.fetch_lab_results,
        }
        self.session: Optional[aiohttp.ClientSession] = None
        self.api_keys = {
            "wearables": os.getenv("WEARABLES_API_KEY"),
            "ehr": os.getenv("EHR_API_KEY"),
            "lab_results": os.getenv("LAB_RESULTS_API_KEY"),
        }

    async def initialize(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_wearable_data(self, user_id: int) -> Dict[str, Any]:
        url = f"https://api.wearabledevice.com/user/{user_id}/data"
        headers = {"Authorization": f"Bearer {self.api_keys['wearables']}"}
        return await self._fetch_data(url, headers, "wearable")

    async def fetch_ehr_data(self, user_id: int) -> Dict[str, Any]:
        url = f"https://api.ehrsystem.com/patient/{user_id}/data"
        headers = {"Authorization": f"Bearer {self.api_keys['ehr']}"}
        return await self._fetch_data(url, headers, "EHR")

    async def fetch_lab_results(self, user_id: int) -> Dict[str, Any]:
        url = f"https://api.labresults.com/patient/{user_id}/results"
        headers = {"Authorization": f"Bearer {self.api_keys['lab_results']}"}
        return await self._fetch_data(url, headers, "lab results")

    async def _fetch_data(self, url: str, headers: Dict[str, str], source_name: str) -> Dict[str, Any]:
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Error fetching {source_name} data: {response.status}")
                    return {}
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching {source_name} data: {str(e)}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding {source_name} data: {str(e)}")
            return {}

    async def collect_data(self, user_id: int) -> Dict[str, Dict[str, Any]]:
        await self.initialize()
        tasks = [source(user_id) for source in self.data_sources.values()]
        results = await asyncio.gather(*tasks)
        return {source: result for source, result in zip(self.data_sources.keys(), results)}

    def normalize_data(self, data: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        normalized_data = {}
        for source, values in data.items():
            for key, value in values.items():
                if isinstance(value, (int, float)):
                    normalized_data[f"{source}_{key}"] = float(value)
                elif isinstance(value, str) and "/" in value:
                    systolic, diastolic = map(int, value.split("/"))
                    normalized_data[f"{source}_{key}_systolic"] = float(systolic)
                    normalized_data[f"{source}_{key}_diastolic"] = float(diastolic)
        return normalized_data

    async def integrate_data(self, user_id: int) -> Dict[str, float]:
        try:
            raw_data = await self.collect_data(user_id)
            normalized_data = self.normalize_data(raw_data)
            validated_data = await self.validate_data(normalized_data)
            preprocessed_data = await self.preprocess_data(validated_data)
            await self.store_integrated_data(user_id, preprocessed_data)
            return preprocessed_data
        except Exception as e:
            logger.error(f"Error integrating data for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error integrating health data")
        finally:
            await self.close()

    async def store_integrated_data(self, user_id: int, data: Dict[str, float]):
        timestamp = datetime.utcnow()
        async with database.transaction():
            for data_type, value in data.items():
                query = health_data.insert().values(
                    user_id=user_id,
                    data_type=data_type,
                    value=value,
                    timestamp=timestamp
                )
                await database.execute(query)

    @aiocache.cached(ttl=300, cache=Cache.MEMORY)
    async def get_latest_integrated_data(self, user_id: int) -> Dict[str, float]:
        query = select([health_data.c.data_type, health_data.c.value]) \
            .where(health_data.c.user_id == user_id) \
            .order_by(health_data.c.timestamp.desc()) \
            .distinct(health_data.c.data_type)
        results = await database.fetch_all(query)
        return {row['data_type']: row['value'] for row in results}

    async def get_data_history(self, user_id: int, data_type: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        query = select([health_data]) \
            .where((health_data.c.user_id == user_id) &
                   (health_data.c.data_type == data_type) &
                   (health_data.c.timestamp.between(start_date, end_date))) \
            .order_by(health_data.c.timestamp.desc())
        results = await database.fetch_all(query)
        return [dict(row) for row in results]

    async def get_data_sources(self, user_id: int) -> List[str]:
        query = select([health_data.c.data_type]).where(health_data.c.user_id == user_id).distinct()
        results = await database.fetch_all(query)
        return [row['data_type'] for row in results]

    async def add_custom_data_source(self, user_id: int, data_type: str, value: float):
        data_point = HealthDataPoint(user_id=user_id, data_type=data_type, value=value, timestamp=datetime.utcnow())
        query = health_data.insert().values(**data_point.dict())
        await database.execute(query)

    async def remove_data_source(self, user_id: int, data_type: str):
        query = health_data.delete().where(
            (health_data.c.user_id == user_id) & (health_data.c.data_type == data_type)
        )
        await database.execute(query)

    async def update_data_source_settings(self, user_id: int, data_type: str, settings: Dict[str, Any]):
        encrypted_settings = fernet.encrypt(json.dumps(settings).encode()).decode()
        query = data_source_settings.insert().values(
            user_id=user_id,
            data_type=data_type,
            settings=encrypted_settings
        ).on_conflict_do_update(
            index_elements=['user_id', 'data_type'],
            set_=dict(settings=encrypted_settings)
        )
        await database.execute(query)

    async def get_data_source_settings(self, user_id: int, data_type: str) -> Dict[str, Any]:
        query = select([data_source_settings.c.settings]).where(
            (data_source_settings.c.user_id == user_id) &
            (data_source_settings.c.data_type == data_type)
        )
        result = await database.fetch_one(query)
        if result:
            decrypted_settings = fernet.decrypt(result['settings'].encode()).decode()
            return json.loads(decrypted_settings)
        return {}

    async def validate_data(self, data: Dict[str, float]) -> Dict[str, float]:
        validated_data = {}
        for key, value in data.items():
            try:
                if key == "steps" and value < 0:
                    logger.warning(f"Invalid step count: {value}. Setting to 0.")
                    validated_data[key] = 0
                elif key in ["heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic"] and value <= 0:
                    logger.warning(f"Invalid {key}: {value}. Skipping.")
                else:
                    validated_data[key] = value
            except ValueError as e:
                logger.error(f"Validation error for {key}: {str(e)}")
        return validated_data

    async def preprocess_data(self, data: Dict[str, float]) -> Dict[str, float]:
        preprocessed_data = data.copy()
        
        if "weight" in preprocessed_data and preprocessed_data["weight"] > 500:
            preprocessed_data["weight"] = preprocessed_data["weight"] * 0.453592
        
        for key in ["steps", "heart_rate", "sleep_hours"]:
            if key not in preprocessed_data or preprocessed_data[key] is None:
                preprocessed_data[key] = 0
        
        return preprocessed_data

    async def detect_anomalies(self, user_id: int, data: Dict[str, float]) -> List[str]:
        anomalies = []
        historical_data = await self.get_latest_integrated_data(user_id)
        
        for key, value in data.items():
            if key in historical_data:
                historical_value = historical_data[key]
                if abs(value - historical_value) / historical_value > 0.5:
                    anomalies.append(f"Anomaly detected in {key}: current value {value}, historical value {historical_value}")
        
        return anomalies

    async def integrate_and_process_data(self, user_id: int) -> Dict[str, Any]:
        raw_data = await self.collect_data(user_id)
        normalized_data = self.normalize_data(raw_data)
        validated_data = await self.validate_data(normalized_data)
        preprocessed_data = await self.preprocess_data(validated_data)
        anomalies = await self.detect_anomalies(user_id, preprocessed_data)
        
        await self.store_integrated_data(user_id, preprocessed_data)
        
        return {
            "integrated_data": preprocessed_data,
            "anomalies": anomalies
        }

    async def get_data_summary(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        query = select([
            health_data.c.data_type,
            func.avg(health_data.c.value).label('average'),
            func.min(health_data.c.value).label('minimum'),
            func.max(health_data.c.value).label('maximum')
        ]).where(
            (health_data.c.user_id == user_id) &
            (health_data.c.timestamp.between(start_date, end_date))
        ).group_by(health_data.c.data_type)
        
        results = await database.fetch_all(query)
        return {row['data_type']: dict(row) for row in results}

    async def get_data_trends(self, user_id: int, data_type: str, days: int) -> List[Dict[str, Any]]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        query = select([
            func.date_trunc('day', health_data.c.timestamp).label('date'),
            func.avg(health_data.c.value).label('average')
        ]).where(
            (health_data.c.user_id == user_id) &
            (health_data.c.data_type == data_type) &
            (health_data.c.timestamp.between(start_date, end_date))
        ).group_by(func.date_trunc('day', health_data.c.timestamp)) \
         .order_by(func.date_trunc('day', health_data.c.timestamp))
        
        results = await database.fetch_all(query)
        return [dict(row) for row in results]

    async def get_correlation_analysis(self, user_id: int, data_type1: str, data_type2: str) -> float:
        query = select([
            func.corr(
                select([health_data.c.value]).where(
                    (health_data.c.user_id == user_id) &
                    (health_data.c.data_type == data_type1)
                ).scalar_subquery(),
                select([health_data.c.value]).where(
                    (health_data.c.user_id == user_id) &
                    (health_data.c.data_type == data_type2)
                ).scalar_subquery()
            )
        ])
        
        result = await database.fetch_one(query)
        return result[0] if result else None
