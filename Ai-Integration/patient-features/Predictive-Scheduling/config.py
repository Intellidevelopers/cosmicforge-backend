
class Config:
    PORT = 5000
    DATABASE_URI = 'postgresql://username:password@localhost:5432/appointment_db'
    MODEL_PATH = 'models/appointment_predictor.joblib'
    WORKING_HOURS_START = 8
    WORKING_HOURS_END = 18
    HOURS_PER_DAY = WORKING_HOURS_END - WORKING_HOURS_START
    MAX_SUGGESTIONS = 5
    TEST_SIZE = 0.2
    RANDOM_STATE = 42
    WEATHER_API_KEY = 'your_openweathermap_api_key_here'  # We Add our actual API key here
