# Ai-Integration/database.py

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import asyncio
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from databases import Database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging setup
logger = logging.getLogger(__name__)

# Database configuration
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "health_app")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ai_moderated_forum")

# Construct database URL
DATABASE_URL = URL.create(
    drivername=DB_DRIVER,
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

# Create a SQLAlchemy engine with connection pooling
engine = create_engine(str(DATABASE_URL), pool_size=20, max_overflow=0)

# Create a metadata instance
metadata = MetaData()

# Base class for SQLAlchemy models
Base = declarative_base()

# Import models from individual features
from .Ai_Moderated_Forum.database import Database as ForumDatabase
from .Lab_Test_Interpretation.core.database import PostgreSQLDatabase, LabTest, Interpretation, MedicalGuideline, MedicalContext, ReferenceRange, FeedbackEntry, LabTestExpansion, TrainingData
from .Ai_Personalized_Dashboard.database import users

class CentralDatabase:
    def __init__(self):
        self.forum_db = ForumDatabase.get_instance()
        self.lab_test_db = PostgreSQLDatabase(str(DATABASE_URL))
        self.async_session = sessionmaker(
            bind=create_async_engine(str(DATABASE_URL)),
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.database = Database(str(DATABASE_URL))

    async def connect(self):
        await self.database.connect()
        await self.lab_test_db.initialize()
        self.forum_db.connect()

    async def disconnect(self):
        await self.database.disconnect()
        self.forum_db.close()

    # Ai-Moderated-Forum methods
    def get_forum_collection(self, collection_name):
        return self.forum_db.get_collection(collection_name)

    def forum_insert_one(self, collection_name, document):
        return self.forum_db.insert_one(collection_name, document)

    def forum_find_one(self, collection_name, query):
        return self.forum_db.find_one(collection_name, query)

    def forum_find(self, collection_name, query):
        return self.forum_db.find(collection_name, query)

    def forum_update_one(self, collection_name, query, update):
        return self.forum_db.update_one(collection_name, query, update)

    def forum_delete_one(self, collection_name, query):
        return self.forum_db.delete_one(collection_name, query)

    def forum_create_index(self, collection_name, keys, **kwargs):
        return self.forum_db.create_index(collection_name, keys, **kwargs)

    # Lab-Test-Interpretation methods
    async def add_test(self, test_data: Dict[str, Any]) -> None:
        await self.lab_test_db.add_test(test_data)

    async def get_test_info(self, test_name: str) -> Optional[Dict[str, Any]]:
        return await self.lab_test_db.get_test_info(test_name)

    async def add_interpretation(self, interpretation_data: Dict[str, Any]) -> None:
        await self.lab_test_db.add_interpretation(interpretation_data)

    async def get_interpretation(self, test_name: str, value: float) -> Optional[Dict[str, Any]]:
        return await self.lab_test_db.get_interpretation(test_name, value)

    # Add other Lab-Test-Interpretation methods as needed

    # Ai-Personalized-Dashboard methods
    async def create_user(self, user_data: Dict[str, Any]):
        query = users.insert().values(**user_data)
        return await self.database.execute(query)

    async def get_user(self, user_id: uuid.UUID):
        query = users.select().where(users.c.id == user_id)
        return await self.database.fetch_one(query)

    async def update_user(self, user_id: uuid.UUID, user_data: Dict[str, Any]):
        query = users.update().where(users.c.id == user_id).values(**user_data)
        return await self.database.execute(query)

    async def delete_user(self, user_id: uuid.UUID):
        query = users.delete().where(users.c.id == user_id)
        return await self.database.execute(query)

# Initialize the central database
central_db = CentralDatabase()

# Initialization function
async def init_db():
    await central_db.connect()

# Cleanup function
async def cleanup_db():
    await central_db.disconnect()

# Run the initialization
if __name__ == "__main__":
    asyncio.run(init_db())
