# core/Database.py

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
