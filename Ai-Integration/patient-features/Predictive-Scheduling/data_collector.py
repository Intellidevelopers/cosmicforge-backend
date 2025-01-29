# data_collector.py

import pandas as pd
from sqlalchemy import create_engine
from config import Config
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    def __init__(self):
        self.engine = create_engine(Config.DATABASE_URI)

    def get_historical_data(self):
        try:
            query = """
            SELECT 
                p.age, p.gender, p.medical_history, p.zip_code,
                a.date, a.time, a.duration as appointment_duration, a.type,
                pr.specialization as provider_specialization,
                a.no_show, a.cancellation
            FROM 
                appointments a
                JOIN patients p ON a.patient_id = p.id
                JOIN providers pr ON a.provider_id = pr.id
            WHERE 
                a.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            """
            df = pd.read_sql(query, self.engine)
            logger.info(f"Retrieved {len(df)} historical appointments")
            return df
        except Exception as e:
            logger.error(f"Error in get_historical_data: {str(e)}")
            raise

    def get_patient_data(self, patient_id):
        try:
            query = f"""
            SELECT 
                p.age, p.gender, p.medical_history, p.zip_code,
                COUNT(CASE WHEN a.no_show = 1 THEN 1 END) as previous_no_shows,
                COUNT(CASE WHEN a.cancellation = 1 THEN 1 END) as previous_cancellations
            FROM 
                patients p
                LEFT JOIN appointments a ON p.id = a.patient_id
            WHERE 
                p.id = {patient_id}
            GROUP BY 
                p.id
            """
            df = pd.read_sql(query, self.engine)
            if df.empty:
                raise ValueError(f"No patient found with id {patient_id}")
            return df.iloc[0].to_dict()
        except Exception as e:
            logger.error(f"Error in get_patient_data: {str(e)}")
            raise

    def get_provider_availability(self, appointment_type, preferred_dates):
        try:
            date_list = ", ".join([f"'{date}'" for date in preferred_dates])
            query = f"""
            SELECT 
                date, time, available, specialization as provider_specialization
            FROM 
                provider_availability pa
                JOIN providers pr ON pa.provider_id = pr.id
            WHERE 
                pa.appointment_type = '{appointment_type}'
                AND pa.date IN ({date_list})
            """
            df = pd.read_sql(query, self.engine)
            availability = []
            for _, row in df.iterrows():
                availability.append({
                    'date': row['date'],
                    'time': row['time'],
                    'available': row['available'],
                    'provider_specialization': row['provider_specialization']
                })
            return availability
        except Exception as e:
            logger.error(f"Error in get_provider_availability: {str(e)}")
            raise

    def save_appointment_data(self, appointment_data):
        try:
            df = pd.DataFrame([appointment_data])
            df.to_sql('appointments', self.engine, if_exists='append', index=False)
            logger.info("Appointment data saved successfully")
        except Exception as e:
            logger.error(f"Error in save_appointment_data: {str(e)}")
            raise
