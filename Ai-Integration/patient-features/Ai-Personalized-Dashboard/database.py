import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
from databases import Database
from sqlalchemy.engine.url import URL
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "health_app")
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# Construct database URL
DATABASE_URL = URL.create(
    drivername=DB_DRIVER,
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)

# Create a database instance
database = Database(str(DATABASE_URL))

# Create a SQLAlchemy engine with connection pooling
engine = create_engine(str(DATABASE_URL), pool_size=20, max_overflow=0)

# Create a metadata instance
metadata = MetaData()

# Define tables with improved schema
users = Table(
    "users",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("username", String(50), unique=True, nullable=False, index=True),
    Column("email", String(100), unique=True, nullable=False, index=True),
    Column("hashed_password", String(255), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
)

health_data = Table(
    "health_data",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("data_type", String(50), nullable=False),
    Column("value", Float, nullable=False),
    Column("timestamp", DateTime, default=datetime.utcnow, nullable=False),
    Column("source", String(50), nullable=False)
)

health_plans = Table(
    "health_plans",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("plan_type", String(50), nullable=False),
    Column("details", JSON, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False)
)

health_goals = Table(
    "health_goals",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("goal_type", String(50), nullable=False),
    Column("target_value", Float, nullable=False),
    Column("current_value", Float, nullable=False),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    Column("deadline", DateTime),
    Column("status", String(20), default="In Progress", nullable=False)
)

user_preferences = Table(
    "user_preferences",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
    Column("preferences", JSON, nullable=False),
    Column("last_updated", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
)

user_preferences_history = Table(
    "user_preferences_history",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("preferences", JSON, nullable=False),
    Column("updated_at", DateTime, default=datetime.utcnow, nullable=False)
)

ai_models = Table(
    "ai_models",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("model_name", String(100), nullable=False),
    Column("version", String(20), nullable=False),
    Column("performance_metric", Float, nullable=False),
    Column("last_updated", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    Column("model_path", String(255), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False)
)

# Function to create all tables in the database
def create_tables():
    metadata.create_all(engine)

# Function to drop all tables in the database
def drop_tables():
    metadata.drop_all(engine)

if __name__ == "__main__":
    create_tables()
