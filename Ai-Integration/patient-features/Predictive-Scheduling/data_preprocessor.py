import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from config import Config
import logging
import requests
from datetime import datetime
from workalendar.usa import UnitedStates

logger = logging.getLogger(__name__)

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
        self.imputer = SimpleImputer(strategy='mean')
        self.cal = UnitedStates()
        self.weather_api_key = Config.WEATHER_API_KEY

    def preprocess_data(self, data):
        try:
            data = self._handle_missing_values(data)
            X = self._extract_features(data)
            y = data['no_show'].astype(int)
            X_encoded = self._encode_categorical_variables(X)
            X_normalized = self._normalize_numerical_features(X_encoded)
            return X_normalized, y
        except Exception as e:
            logger.error(f"Error in preprocess_data: {str(e)}")
            raise

    def _handle_missing_values(self, data):
        numerical_columns = data.select_dtypes(include=[np.number]).columns
        data[numerical_columns] = self.imputer.fit_transform(data[numerical_columns])
        categorical_columns = data.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            data[col].fillna(data[col].mode()[0], inplace=True)
        return data

    def _extract_features(self, data):
        features = pd.DataFrame()
        features['age'] = data['age']
        features['gender'] = data['gender']
        features['day_of_week'] = pd.to_datetime(data['date']).dt.dayofweek
        features['month'] = pd.to_datetime(data['date']).dt.month
        features['hour'] = pd.to_datetime(data['time']).dt.hour
        features['duration'] = data['duration']
        features['appointment_type'] = data['type']
        features['specialization'] = data['specialization']
        features['previous_no_shows'] = data.groupby('patient_id')['no_show'].transform('sum')
        features['previous_cancellations'] = data.groupby('patient_id')['cancellation'].transform('sum')
        features['is_holiday'] = data['date'].apply(self._is_holiday)
        features['temperature'] = data.apply(lambda row: self._get_temperature(row['date'], row['zip_code']), axis=1)
        return features

    def _encode_categorical_variables(self, X):
        categorical_columns = X.select_dtypes(include=['object']).columns
        X_encoded = X.copy()
        X_encoded[categorical_columns] = self.encoder.fit_transform(X[categorical_columns])
        return X_encoded

    def _normalize_numerical_features(self, X):
        return self.scaler.fit_transform(X)

    def _is_holiday(self, date):
        return int(self.cal.is_holiday(date))

    def _get_temperature(self, date, zip_code):
        url = f"http://api.openweathermap.org/data/2.5/forecast?zip={zip_code},us&appid={self.weather_api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for forecast in data['list']:
                forecast_date = datetime.fromtimestamp(forecast['dt'])
                if forecast_date.date() == date.date():
                    return forecast['main']['temp']
        logger.warning(f"Could not fetch temperature for {date} and zip code {zip_code}")
        return None

    def create_features(self, patient_data, appointment_type, preferred_dates):
        features = []
        for date in preferred_dates:
            for hour in range(Config.WORKING_HOURS_START, Config.WORKING_HOURS_END):
                feature = [
                    patient_data['age'],
                    1 if patient_data['gender'] == 'F' else 0,
                    pd.Timestamp(date).dayofweek,
                    pd.Timestamp(date).month,
                    hour,
                    patient_data['appointment_duration'],
                    1 if appointment_type == 'checkup' else 0,
                    self._encode_specialization(patient_data['provider_specialization']),
                    patient_data['previous_no_shows'],
                    patient_data['previous_cancellations'],
                    self._is_holiday(pd.Timestamp(date)),
                    self._get_temperature(pd.Timestamp(date), patient_data['zip_code'])
                ]
                features.append(feature)
        return self.scaler.transform(features)

    def _encode_specialization(self, specialization):
        specialization_encoding = {
            'General Practice': 0,
            'Internal Medicine': 1,
            'Pediatrics': 2,
            'Obstetrics and Gynecology': 3,
            'Surgery': 4,
            'Psychiatry': 5,
            'Other': 6
        }
        return specialization_encoding.get(specialization, 6)
