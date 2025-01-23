from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import asyncio
from Config import config

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

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

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
    async def initialize(self) -> None:
        pass

    @abstractmethod
    async def add_test(self, test_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_test_info(self, test_name: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def add_interpretation(self, interpretation_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_interpretation(self, test_name: str, value: float) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def add_medical_guideline(self, guideline_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_medical_guideline(self, test_name: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_knowledge_base(self, update_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def add_feedback(self, feedback_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_feedback(self, test_name: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def add_lab_test_expansion(self, expansion_data: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def get_lab_test_expansion(self, test_name: str) -> Optional[Dict[str, Any]]:
        pass

class PostgreSQLDatabase(Database):
    def __init__(self, db_url: str):
        self.engine = create_async_engine(db_url, pool_size=20, max_overflow=0)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.logger = logging.getLogger(__name__)

    @asynccontextmanager
    async def get_session(self):
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                self.logger.error(f"Database error: {str(e)}")
                raise
            finally:
                await session.close()

    async def initialize(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.logger.info("Database initialized successfully")

    async def add_test(self, test_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            lab_test = LabTest(**test_data)
            session.add(lab_test)
            await session.flush()
            self.logger.info(f"Added new lab test: {test_data['test_name']}")

    async def get_test_info(self, test_name: str) -> Optional[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(select(LabTest).filter_by(test_name=test_name))
            lab_test = result.scalar_one_or_none()
            return lab_test.to_dict() if lab_test else None

    async def add_interpretation(self, interpretation_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            interpretation = Interpretation(**interpretation_data)
            session.add(interpretation)
            await session.flush()
            self.logger.info(f"Added new interpretation for test ID: {interpretation_data['test_id']}")

    async def get_interpretation(self, test_name: str, value: float) -> Optional[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(
                select(Interpretation)
                .join(LabTest)
                .filter(
                    LabTest.test_name == test_name,
                    Interpretation.range_start <= value,
                    Interpretation.range_end >= value
                )
            )
            interpretation = result.scalar_one_or_none()
            return interpretation.to_dict() if interpretation else None

    async def add_medical_guideline(self, guideline_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            guideline = MedicalGuideline(**guideline_data)
            session.add(guideline)
            await session.flush()
            self.logger.info(f"Added new medical guideline for test ID: {guideline_data['test_id']}")

    async def get_medical_guideline(self, test_name: str) -> Optional[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(
                select(MedicalGuideline)
                .join(LabTest)
                .filter(LabTest.test_name == test_name)
            )
            guideline = result.scalar_one_or_none()
            return guideline.to_dict() if guideline else None

        async def update_knowledge_base(self, update_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            context = MedicalContext(**update_data)
            await session.merge(context)
            await session.flush()
            self.logger.info(f"Updated medical context for test: {update_data['test_name']}")

    async def add_feedback(self, feedback_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            feedback = FeedbackEntry(**feedback_data)
            session.add(feedback)
            await session.flush()
            self.logger.info(f"Added new feedback for lab test ID: {feedback_data['lab_test_id']}")

    async def get_feedback(self, test_name: str) -> List[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(
                select(FeedbackEntry)
                .join(LabTest)
                .filter(LabTest.test_name == test_name)
            )
            feedbacks = result.scalars().all()
            return [feedback.to_dict() for feedback in feedbacks]

    async def add_lab_test_expansion(self, expansion_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            expansion = LabTestExpansion(**expansion_data)
            session.add(expansion)
            await session.flush()
            self.logger.info(f"Added lab test expansion for: {expansion_data['test_name']}")

    async def get_lab_test_expansion(self, test_name: str) -> Optional[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(select(LabTestExpansion).filter_by(test_name=test_name))
            expansion = result.scalar_one_or_none()
            return expansion.to_dict() if expansion else None

    async def add_training_data(self, training_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            data = TrainingData(**training_data)
            session.add(data)
            await session.flush()
            self.logger.info(f"Added new training data: {training_data['text'][:50]}...")

    async def get_training_data(self, limit: int = 1000) -> List[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(select(TrainingData).limit(limit))
            data = result.scalars().all()
            return [item.to_dict() for item in data]

    async def update_test(self, test_name: str, update_data: Dict[str, Any]) -> None:
        async with self.get_session() as session:
            result = await session.execute(select(LabTest).filter_by(test_name=test_name))
            lab_test = result.scalar_one_or_none()
            if lab_test:
                for key, value in update_data.items():
                    setattr(lab_test, key, value)
                await session.flush()
                self.logger.info(f"Updated lab test: {test_name}")
            else:
                self.logger.warning(f"Lab test not found: {test_name}")

    async def delete_test(self, test_name: str) -> None:
        async with self.get_session() as session:
            result = await session.execute(select(LabTest).filter_by(test_name=test_name))
            lab_test = result.scalar_one_or_none()
            if lab_test:
                await session.delete(lab_test)
                await session.flush()
                self.logger.info(f"Deleted lab test: {test_name}")
            else:
                self.logger.warning(f"Lab test not found: {test_name}")

    async def get_all_tests(self) -> List[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(select(LabTest))
            tests = result.scalars().all()
            return [test.to_dict() for test in tests]

    async def get_tests_by_category(self, category: str) -> List[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(select(LabTest).filter_by(category=category))
            tests = result.scalars().all()
            return [test.to_dict() for test in tests]

    async def update_reference_range(self, test_name: str, low: float, high: float, unit: str) -> None:
        async with self.get_session() as session:
            result = await session.execute(select(ReferenceRange).filter_by(test_name=test_name))
            ref_range = result.scalar_one_or_none()
            if ref_range:
                ref_range.low = low
                ref_range.high = high
                ref_range.unit = unit
                ref_range.last_updated = datetime.utcnow()
            else:
                new_range = ReferenceRange(test_name=test_name, low=low, high=high, unit=unit)
                session.add(new_range)
            await session.flush()
            self.logger.info(f"Updated reference range for test: {test_name}")

    async def get_reference_range(self, test_name: str) -> Optional[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(select(ReferenceRange).filter_by(test_name=test_name))
            ref_range = result.scalar_one_or_none()
            return ref_range.to_dict() if ref_range else None

    async def add_bulk_tests(self, tests_data: List[Dict[str, Any]]) -> None:
        async with self.get_session() as session:
            for test_data in tests_data:
                lab_test = LabTest(**test_data)
                session.add(lab_test)
            await session.flush()
            self.logger.info(f"Added {len(tests_data)} new lab tests in bulk")

    async def get_recent_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        async with self.get_session() as session:
            result = await session.execute(
                select(FeedbackEntry)
                .order_by(FeedbackEntry.feedback_time.desc())
                .limit(limit)
            )
            feedbacks = result.scalars().all()
            return [feedback.to_dict() for feedback in feedbacks]

    async def get_test_statistics(self) -> Dict[str, Any]:
        async with self.get_session() as session:
            total_tests = await session.scalar(select(func.count()).select_from(LabTest))
            total_interpretations = await session.scalar(select(func.count()).select_from(Interpretation))
            total_guidelines = await session.scalar(select(func.count()).select_from(MedicalGuideline))
            total_feedback = await session.scalar(select(func.count()).select_from(FeedbackEntry))
            
            return {
                "total_tests": total_tests,
                "total_interpretations": total_interpretations,
                "total_guidelines": total_guidelines,
                "total_feedback": total_feedback
            }

# Initialize the database
db_url = config.get_db_url()
database = PostgreSQLDatabase(db_url)

async def init_db():
    await database.initialize()

# Run the initialization
asyncio.run(init_db())

