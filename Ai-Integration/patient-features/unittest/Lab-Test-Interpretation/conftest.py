 
import pytest
from app import app as flask_app
from model_update import update_model
from feedback_handler import process_feedback
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from feedback_handler import Base

@pytest.fixture
def app():
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_model(mocker):
    return mocker.patch('interpret_lab_results.interpret_lab_results')

@pytest.fixture
def mock_update_model(mocker):
    return mocker.patch('model_update.update_model')

@pytest.fixture
def mock_process_feedback(mocker):
    return mocker.patch('feedback_handler.process_feedback')

@pytest.fixture(scope='function')
def db_session():
    engine = create_engine('sqlite:///test.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
