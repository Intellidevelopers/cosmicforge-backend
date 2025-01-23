 
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

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

    def to_dict(self):
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

class MedicalGuideline(Base):
    __tablename__ = 'medical_guidelines'
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('lab_tests.id'))
    guideline = Column(Text)
    source = Column(String)
    last_updated = Column(DateTime)

class MedicalContext(Base):
    __tablename__ = 'medical_context'
    test_name = Column(String, primary_key=True)
    description = Column(Text)
    common_interpretations = Column(Text)
    related_conditions = Column(Text)
    last_updated = Column(DateTime)

class ReferenceRange(Base):
    __tablename__ = 'reference_ranges'
    test_name = Column(String, primary_key=True)
    low = Column(Float)
    high = Column(Float)
    unit = Column(String)
    last_updated = Column(String)

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
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    label = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingData(id={self.id}, text='{self.text[:50]}...', label='{self.label}')>"

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'label': self.label,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
