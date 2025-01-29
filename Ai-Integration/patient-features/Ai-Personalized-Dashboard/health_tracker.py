import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from huggingface_hub import hf_hub_download
from database import database, health_data, health_goals, medications, appointments
import json
import asyncio
from fastapi import HTTPException
from pydantic import BaseModel, validator
import os
from dotenv import load_dotenv
import aiohttp
from aiocache import cached
from aiocache.serializers import PickleSerializer

from sqlalchemy import select, insert
from database import database, medications, appointments, alert_logs
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Pydantic models for data validation
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

class HealthGoal(BaseModel):
    user_id: int
    goal_type: str
    target_value: float

class Medication(BaseModel):
    user_id: int
    name: str
    dosage: str
    frequency: str
    start_date: datetime
    end_date: Optional[datetime]

class Appointment(BaseModel):
    user_id: int
    doctor: str
    date: datetime
    description: str

class HealthTracker:
    def __init__(self):
        self.health_score_model = self.load_health_score_model()
        self.scaler = self.load_scaler()
        self.progress_tracker = ProgressTracker()
        self.alert_system = AlertSystem()
        self.session: Optional[aiohttp.ClientSession] = None

    async def initialize(self):
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()

    def load_health_score_model(self):
        try:
            model_path = hf_hub_download(repo_id="your-repo/health-score-model", filename="model.joblib")
            return joblib.load(model_path)
        except Exception as e:
            logger.error(f"Error loading health score model: {str(e)}")
            return RandomForestRegressor(n_estimators=100, random_state=42)

    def load_scaler(self):
        try:
            scaler_path = hf_hub_download(repo_id="your-repo/health-score-model", filename="scaler.joblib")
            return joblib.load(scaler_path)
        except Exception as e:
            logger.error(f"Error loading scaler: {str(e)}")
            return StandardScaler()

    @cached(ttl=300, serializer=PickleSerializer())
    async def calculate_health_score(self, user_data: Dict[str, float]) -> float:
        try:
            features = self.preprocess_data(user_data)
            health_score = self.health_score_model.predict(features)[0]
            return max(0, min(100, health_score))  # Ensure score is between 0 and 100
        except Exception as e:
            logger.error(f"Error calculating health score: {str(e)}")
            return 50.0  # Return a default score if calculation fails

    def preprocess_data(self, user_data: Dict[str, float]) -> np.ndarray:
        feature_order = ['age', 'weight', 'height', 'bmi', 'blood_pressure_systolic', 'blood_pressure_diastolic', 
                         'cholesterol', 'glucose', 'steps', 'sleep_hours', 'heart_rate']
        
        features = [user_data.get(feature, 0) for feature in feature_order]
        features = np.array(features).reshape(1, -1)
        return self.scaler.transform(features)

    async def process_real_time_data(self, user_id: int, new_data: Dict[str, float]) -> Dict[str, Any]:
        try:
            await self.update_health_data(user_id, new_data)
            user_data = await self.get_user_data(user_id)
            health_score = await self.calculate_health_score(user_data)
            progress = await self.progress_tracker.track_progress(user_id, user_data)
            alerts = await self.alert_system.check_alerts(user_id, user_data, health_score)
            
            return {
                "health_score": health_score,
                "progress": progress,
                "alerts": alerts
            }
        except Exception as e:
            logger.error(f"Error processing real-time data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to process real-time data")

    async def update_health_data(self, user_id: int, new_data: Dict[str, float]):
        try:
            timestamp = datetime.utcnow()
            async with database.transaction():
                for data_type, value in new_data.items():
                    query = health_data.insert().values(
                        user_id=user_id,
                        data_type=data_type,
                        value=value,
                        timestamp=timestamp
                    )
                    await database.execute(query)
        except Exception as e:
            logger.error(f"Error updating health data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update health data")

    async def get_user_data(self, user_id: int) -> Dict[str, float]:
        try:
            query = """
            SELECT data_type, value
            FROM (
                SELECT data_type, value, ROW_NUMBER() OVER (PARTITION BY data_type ORDER BY timestamp DESC) as rn
                FROM health_data
                WHERE user_id = :user_id
            ) subquery
            WHERE rn = 1
            """
            results = await database.fetch_all(query=query, values={"user_id": user_id})
            return {row['data_type']: row['value'] for row in results}
        except Exception as e:
            logger.error(f"Error fetching user data: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch user data")

    async def get_health_trends(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        try:
            query = """
            SELECT data_type, value, timestamp
            FROM health_data
            WHERE user_id = :user_id AND timestamp BETWEEN :start_date AND :end_date
            ORDER BY timestamp ASC
            """
            results = await database.fetch_all(query=query, values={
                "user_id": user_id,
                "start_date": start_date,
                "end_date": end_date
            })
            
            trends = {}
            for row in results:
                if row['data_type'] not in trends:
                    trends[row['data_type']] = []
                trends[row['data_type']].append({
                    "value": row['value'],
                    "timestamp": row['timestamp']
                })
            
            return trends
        except Exception as e:
            logger.error(f"Error fetching health trends: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch health trends")

    async def train_health_score_model(self, training_data: List[Dict[str, Any]]):
        try:
            X = []
            y = []
            for data in training_data:
                features = self.preprocess_data(data['user_data'])
                X.append(features[0])
                y.append(data['health_score'])
            
            X = np.array(X)
            y = np.array(y)
            
            self.health_score_model = RandomForestRegressor(n_estimators=100, random_state=42)
            self.health_score_model.fit(X, y)
            
            # Save the model
            joblib.dump(self.health_score_model, 'health_score_model.joblib')
            joblib.dump(self.scaler, 'health_score_scaler.joblib')
            
            logger.info("Health score model trained successfully")
        except Exception as e:
            logger.error(f"Error training health score model: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to train health score model")

class ProgressTracker:
    async def track_progress(self, user_id: int, user_data: Dict[str, float]) -> Dict[str, float]:
        try:
            goals = await self.get_user_goals(user_id)
            progress = {}
            for goal in goals:
                if goal['goal_type'] in user_data:
                    current_value = user_data[goal['goal_type']]
                    target_value = goal['target_value']
                    progress[goal['goal_type']] = min(100, (current_value / target_value) * 100)
            return progress
        except Exception as e:
            logger.error(f"Error tracking progress: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to track progress")

    async def get_user_goals(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            query = health_goals.select().where(health_goals.c.user_id == user_id)
            results = await database.fetch_all(query)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error fetching user goals: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to fetch user goals")

    async def set_goal(self, user_id: int, goal_type: str, target_value: float):
        try:
            query = health_goals.insert().values(
                user_id=user_id,
                goal_type=goal_type,
                target_value=target_value
            )
            await database.execute(query)
        except Exception as e:
            logger.error(f"Error setting goal: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to set goal")

    async def update_goal(self, user_id: int, goal_type: str, target_value: float):
        try:
            query = health_goals.update().where(
                (health_goals.c.user_id == user_id) & 
                (health_goals.c.goal_type == goal_type)
            ).values(target_value=target_value)
            await database.execute(query)
        except Exception as e:
            logger.error(f"Error updating goal: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update goal")

class AlertSystem:
    async def check_alerts(self, user_id: int, user_data: Dict[str, float], health_score: float) -> List[Dict[str, str]]:
        alerts = []
        try:
            alerts.extend(self.check_health_score_alert(health_score))
            alerts.extend(self.check_vital_signs_alerts(user_data))
            alerts.extend(await self.check_medication_alerts(user_id))
            alerts.extend(await self.check_appointment_alerts(user_id))
            return alerts
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to check alerts")
        self.push_notification_url = os.getenv("PUSH_NOTIFICATION_URL")
        self.push_notification_api_key = os.getenv("PUSH_NOTIFICATION_API_KEY")
        self.email_sender = os.getenv("EMAIL_SENDER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        
    def check_health_score_alert(self, health_score: float) -> List[Dict[str, str]]:
        if health_score < 50:
            return [{"type": "health_score", "message": "Your health score is low. Please consult your doctor."}]
        return []

    def check_vital_signs_alerts(self, user_data: Dict[str, float]) -> List[Dict[str, str]]:
        alerts = []
        if user_data.get('blood_pressure_systolic', 0) > 140 or user_data.get('blood_pressure_diastolic', 0) > 90:
            alerts.append({"type": "blood_pressure", "message": "Your blood pressure is high. Please monitor closely."})
        if user_data.get('heart_rate', 0) > 100:
            alerts.append({"type": "heart_rate", "message": "Your heart rate is elevated. Please check your stress levels."})
        if user_data.get('glucose', 0) > 200:
            alerts.append({"type": "glucose", "message": "Your blood glucose level is high. Please check your diet."})
        return alerts

    async def check_medication_alerts(self, user_id: int) -> List[Dict[str, str]]:
        try:
            current_time = datetime.utcnow()
            query = medications.select().where(
                (medications.c.user_id == user_id) &
                (medications.c.start_date <= current_time) &
                ((medications.c.end_date.is_(None)) | (medications.c.end_date >= current_time))
            )
            results = await database.fetch_all(query)
            
            alerts = []
            for medication in results:
                if self.should_take_medication(medication, current_time):
                    alerts.append({
                        "type": "medication",
                        "message": f"Time to take your {medication['name']} ({medication['dosage']})."
                    })
            return alerts
        except Exception as e:
            logger.error(f"Error checking medication alerts: {str(e)}")
            return []

    def should_take_medication(self, medication: Dict[str, Any], current_time: datetime) -> bool:
        frequency = medication['frequency']
        if frequency == 'daily':
            return True
        elif frequency == 'weekly':
            return current_time.weekday() == medication['start_date'].weekday()
        # Add more frequency checks as needed
        return False

    async def check_appointment_alerts(self, user_id: int) -> List[Dict[str, str]]:
        try:
            current_time = datetime.utcnow()
            one_day_from_now = current_time + timedelta(days=1)
            query = appointments.select().where(
                (appointments.c.user_id == user_id) &
                (appointments.c.date.between(current_time, one_day_from_now))
            )
            results = await database.fetch_all(query)
            
            alerts = []
            for appointment in results:
                alerts.append({
                    "type": "appointment",
                    "message": f"You have an appointment with Dr. {appointment['doctor']} tomorrow at {appointment['date'].strftime('%I:%M %p')}."
                })
            return alerts
        except Exception as e:
            logger.error(f"Error checking appointment alerts: {str(e)}")
            return []

    async def check_alerts(self, user_id: int, user_data: Dict[str, float], health_score: float) -> List[Dict[str, str]]:
        alerts = []
        try:
            alerts.extend(self.check_health_score_alert(health_score))
            alerts.extend(self.check_vital_signs_alerts(user_data))
            alerts.extend(await self.check_medication_alerts(user_id))
            alerts.extend(await self.check_appointment_alerts(user_id))
            return alerts
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to check alerts")

    def check_health_score_alert(self, health_score: float) -> List[Dict[str, str]]:
        if health_score < 50:
            return [{"type": "health_score", "message": "Your health score is low. Please consult your doctor."}]
        return []

    def check_vital_signs_alerts(self, user_data: Dict[str, float]) -> List[Dict[str, str]]:
        alerts = []
        if user_data.get('blood_pressure_systolic', 0) > 140 or user_data.get('blood_pressure_diastolic', 0) > 90:
            alerts.append({"type": "blood_pressure", "message": "Your blood pressure is high. Please monitor closely."})
        if user_data.get('heart_rate', 0) > 100:
            alerts.append({"type": "heart_rate", "message": "Your heart rate is elevated. Please check your stress levels."})
        if user_data.get('glucose', 0) > 200:
            alerts.append({"type": "glucose", "message": "Your blood glucose level is high. Please check your diet."})
        return alerts

    async def check_medication_alerts(self, user_id: int) -> List[Dict[str, str]]:
        try:
            current_time = datetime.utcnow()
            query = select(medications).where(
                (medications.c.user_id == user_id) &
                (medications.c.start_date <= current_time) &
                ((medications.c.end_date.is_(None)) | (medications.c.end_date >= current_time))
            )
            results = await database.fetch_all(query)
            
            alerts = []
            for medication in results:
                if self.should_take_medication(medication, current_time):
                    alerts.append({
                        "type": "medication",
                        "message": f"Time to take your {medication['name']} ({medication['dosage']})."
                    })
            return alerts
        except Exception as e:
            logger.error(f"Error checking medication alerts: {str(e)}")
            return []

    def should_take_medication(self, medication: Dict[str, Any], current_time: datetime) -> bool:
        frequency = medication['frequency']
        if frequency == 'daily':
            return True
        elif frequency == 'weekly':
            return current_time.weekday() == medication['start_date'].weekday()
        elif frequency == 'monthly':
            return current_time.day == medication['start_date'].day
        return False

    async def check_appointment_alerts(self, user_id: int) -> List[Dict[str, str]]:
        try:
            current_time = datetime.utcnow()
            one_day_from_now = current_time + timedelta(days=1)
            query = select(appointments).where(
                (appointments.c.user_id == user_id) &
                (appointments.c.date.between(current_time, one_day_from_now))
            )
            results = await database.fetch_all(query)
            
            alerts = []
            for appointment in results:
                alerts.append({
                    "type": "appointment",
                    "message": f"You have an appointment with Dr. {appointment['doctor']} tomorrow at {appointment['date'].strftime('%I:%M %p')}."
                })
            return alerts
        except Exception as e:
            logger.error(f"Error checking appointment alerts: {str(e)}")
            return []

    async def send_alert(self, user_id: int, alert: Dict[str, str]):
        try:
            logger.info(f"Sending alert to user {user_id}: {alert['message']}")
            
            # Send push notification
            await self.send_push_notification(user_id, alert['message'])
            
            # Send email
            user_email = await self.get_user_email(user_id)
            if user_email:
                await self.send_email(user_email, "Health Alert", alert['message'])
            
            # Log the alert
            await self.log_alert(user_id, alert)
        except Exception as e:
            logger.error(f"Error sending alert: {str(e)}")

    async def send_push_notification(self, user_id: int, message: str):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "user_id": user_id,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat()
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.push_notification_api_key}"
                }
                async with session.post(self.push_notification_url, json=payload, headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send push notification. Status: {response.status}")
                    else:
                        logger.info(f"Push notification sent successfully to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")

    async def send_email(self, recipient: str, subject: str, body: str):
        try:
            message = MIMEMultipart()
            message["From"] = self.email_sender
            message["To"] = recipient
            message["Subject"] = subject
            message.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {recipient}")
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")

    async def log_alert(self, user_id: int, alert: Dict[str, str]):
        try:
            query = insert(alert_logs).values(
                user_id=user_id,
                alert_type=alert['type'],
                message=alert['message'],
                timestamp=datetime.utcnow()
            )
            await database.execute(query)
            logger.info(f"Alert logged for user {user_id}")
        except Exception as e:
            logger.error(f"Error logging alert: {str(e)}")

     async def get_user_email(self, user_id: int) -> str:
    try:
        query = select(users.c.email).where(users.c.id == user_id)
        result = await database.fetch_one(query)
        if result:
            return result['email']
        else:
            logger.error(f"No email found for user_id: {user_id}")
            raise HTTPException(status_code=404, detail="User email not found")
    except Exception as e:
        logger.error(f"Error fetching user email: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user email")



    async def log_alert(self, user_id: int, alert: Dict[str, str]):
        try:
            query = """
            INSERT INTO alert_logs (user_id, alert_type, message, timestamp)
            VALUES (:user_id, :alert_type, :message, :timestamp)
            """
            await database.execute(query, values={
                "user_id": user_id,
                "alert_type": alert['type'],
                "message": alert['message'],
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error logging alert: {str(e)}")

# Additional utility functions

async def get_user_medications(user_id: int) -> List[Dict[str, Any]]:
    try:
        query = medications.select().where(medications.c.user_id == user_id)
        results = await database.fetch_all(query)
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching user medications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user medications")

async def add_medication(medication: Medication):
    try:
        query = medications.insert().values(**medication.dict())
        await database.execute(query)
    except Exception as e:
        logger.error(f"Error adding medication: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add medication")

async def update_medication(medication_id: int, medication: Medication):
    try:
        query = medications.update().where(medications.c.id == medication_id).values(**medication.dict(exclude={'id'}))
        await database.execute(query)
    except Exception as e:
        logger.error(f"Error updating medication: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update medication")

async def delete_medication(medication_id: int):
    try:
        query = medications.delete().where(medications.c.id == medication_id)
        await database.execute(query)
    except Exception as e:
        logger.error(f"Error deleting medication: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete medication")

async def get_user_appointments(user_id: int) -> List[Dict[str, Any]]:
    try:
        query = appointments.select().where(appointments.c.user_id == user_id)
        results = await database.fetch_all(query)
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error fetching user appointments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch user appointments")

async def add_appointment(appointment: Appointment):
    try:
        query = appointments.insert().values(**appointment.dict())
        await database.execute(query)
    except Exception as e:
        logger.error(f"Error adding appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add appointment")

async def update_appointment(appointment_id: int, appointment: Appointment):
    try:
        query = appointments.update().where(appointments.c.id == appointment_id).values(**appointment.dict(exclude={'id'}))
        await database.execute(query)
    except Exception as e:
        logger.error(f"Error updating appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")

async def delete_appointment(appointment_id: int):
    try:
        query = appointments.delete().where(appointments.c.id == appointment_id)
        await database.execute(query)
    except Exception as e:
        logger.error(f"Error deleting appointment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete appointment")

# Initialize the HealthTracker
health_tracker = HealthTracker()

# Startup and shutdown events
async def startup_event():
    await health_tracker.initialize()

async def shutdown_event():
    await health_tracker.close()
