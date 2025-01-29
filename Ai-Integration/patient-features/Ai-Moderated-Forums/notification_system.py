import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import schedule
import time
import threading
import logging
from firebase_admin import messaging, credentials, initialize_app
import numpy as np
from sklearn.cluster import KMeans
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from textblob import TextBlob
from collections import defaultdict
import datetime
from dateutil.parser import parse


class NotificationSystem:
    def __init__(self, db_connection, nlp_model, smtp_config, firebase_config):
        self.db = db_connection
        self.smtp_config = smtp_config
        self.firebase_app = initialize_app(credentials.Certificate(firebase_config))
        self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.nlp_model = nlp_model
        self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        self.logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    def send_email(self, recipient, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.smtp_config['username']
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(msg)
            logger.info(f"Email sent successfully to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")

    def send_push_notification(self, user_id, title, body):
        try:
            user_data = self.db.users.find_one({'_id': user_id})
            if user_data and 'fcm_token' in user_data:
                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    token=user_data['fcm_token'],
                )
                response = messaging.send(message)
                logger.info(f"Successfully sent push notification: {response}")
            else:
                logger.warning(f"User {user_id} does not have an FCM token")
        except Exception as e:
            logger.error(f"Failed to send push notification to user {user_id}: {str(e)}")

    def create_notification(self, user_id, notification_type, content, priority=None):
        try:
            notification = {
                'user_id': user_id,
                'type': notification_type,
                'content': content,
                'created_at': datetime.utcnow(),
                'read': False,
                'priority': priority or self.calculate_priority(user_id, notification_type, content)
            }
            result = self.db.notifications.insert_one(notification)
            logger.info(f"Created notification {result.inserted_id} for user {user_id}")
            return result.inserted_id
        except Exception as e:
            logger.error(f"Failed to create notification for user {user_id}: {str(e)}")
            return None

    def calculate_priority(self, user_id, notification_type, content):
        try:
            user_data = self.db.users.find_one({'_id': user_id})
            user_preferences = user_data.get('notification_preferences', {})
            
            # Type priority based on user preferences
            type_priority = user_preferences.get(notification_type, 0.5)
            
            # Content relevance using NLP
            relevance = self.calculate_content_relevance(user_data, content)
            
            # User engagement score
            engagement_score = self.calculate_user_engagement(user_id)
            
            # Time sensitivity
            time_sensitivity = self.calculate_time_sensitivity(notification_type)
            
            # Notification frequency control
            frequency_factor = self.control_notification_frequency(user_id)
            
            # Calculate weighted priority
            priority = (
                type_priority * 0.3 +
                relevance * 0.3 +
                engagement_score * 0.2 +
                time_sensitivity * 0.1 +
                frequency_factor * 0.1
            )
            
            return min(max(priority, 0), 1)  # Ensure it's between 0 and 1
        except Exception as e:
            self.logger.error(f"Error calculating priority for user {user_id}: {str(e)}")
            return 0.5

    def calculate_content_relevance(self, user_data, content):
        user_interests = set(user_data.get('interests', []))
        content_vector = self.nlp_model.encode(content)
        interest_vectors = [self.nlp_model.encode(interest) for interest in user_interests]
        
        if interest_vectors:
            similarities = [np.dot(content_vector, iv) / (np.linalg.norm(content_vector) * np.linalg.norm(iv)) 
                            for iv in interest_vectors]
            return max(similarities)
        return 0.5

    def calculate_user_engagement(self, user_id):
        recent_notifications = list(self.db.notifications.find({
            'user_id': user_id,
            'created_at': {'$gte': datetime.datetime.utcnow() - datetime.timedelta(days=30)}
        }))
        
        if not recent_notifications:
            return 0.5
        
        read_times = [(n['read_at'] - n['created_at']).total_seconds() 
                      for n in recent_notifications if 'read_at' in n]
        interaction_rate = len(read_times) / len(recent_notifications)
        
        if read_times:
            avg_read_time = np.mean(read_times)
            read_time_score = 1 - min(avg_read_time / 86400, 1)  # Normalize to 0-1
        else:
            read_time_score = 0
        
        return (interaction_rate + read_time_score) / 2

    def calculate_time_sensitivity(self, notification_type):
        sensitivity_map = {
            'urgent_alert': 1.0,
            'appointment_reminder': 0.8,
            'medication_reminder': 0.9,
            'general_update': 0.5,
            'promotional': 0.2
        }
        return sensitivity_map.get(notification_type, 0.5)

    def control_notification_frequency(self, user_id):
        recent_notifications = self.db.notifications.count_documents({
            'user_id': user_id,
            'created_at': {'$gte': datetime.datetime.utcnow() - datetime.timedelta(hours=24)}
        })
        return max(1 - (recent_notifications / 20), 0)  # Reduce priority if many recent notifications

    def get_user_notifications(self, user_id, limit=20):
        try:
            notifications = list(self.db.notifications.find(
                {'user_id': user_id, 'read': False}
            ).sort('priority', -1).limit(limit))
            
            grouped_notifications = self.group_notifications(notifications)
            
            for group in grouped_notifications:
                group['summary'] = self.summarize_content([n['content'] for n in group['notifications']])
            
            return grouped_notifications
        except Exception as e:
            self.logger.error(f"Error fetching notifications for user {user_id}: {str(e)}")
            return []

    def group_notifications(self, notifications):
        if not notifications:
            return []

        features = np.array([[
            n['priority'],
            n['created_at'].timestamp(),
            self.get_content_embedding(n['content'])
        ] for n in notifications])
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Use DBSCAN for more flexible clustering
        dbscan = DBSCAN(eps=0.5, min_samples=2)
        labels = dbscan.fit_predict(scaled_features)
        
        grouped = defaultdict(list)
        for notification, label in zip(notifications, labels):
            grouped[label].append(notification)
        
        result = []
        for label, group in grouped.items():
            if label != -1:  # Exclude noise points
                result.append({
                    'type': self.determine_group_type(group),
                    'notifications': group,
                    'count': len(group)
                })
        
        # Sort groups by priority
        result.sort(key=lambda x: max(n['priority'] for n in x['notifications']), reverse=True)
        
        return result

    def get_content_embedding(self, content):
        # Use the NLP model to get content embedding
        return self.nlp_model.encode(content)

    def determine_group_type(self, group):
        type_counts = defaultdict(int)
        for notification in group:
            type_counts[notification['type']] += 1
        return max(type_counts, key=type_counts.get)

    def summarize_content(self, contents):
        combined_content = " ".join(contents)
        blob = TextBlob(combined_content)
        sentences = blob.sentences
        
        if len(sentences) <= 3:
            return combined_content
        
        # Use TextRank-like algorithm for summarization
        sentence_scores = defaultdict(float)
        for i, sentence1 in enumerate(sentences):
            for sentence2 in sentences[i+1:]:
                similarity = self.sentence_similarity(sentence1, sentence2)
                sentence_scores[sentence1] += similarity
                sentence_scores[sentence2] += similarity
        
        top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:3]
        summary = " ".join(str(sentence) for sentence in top_sentences)
        return summary

    def sentence_similarity(self, sent1, sent2):
        vec1 = self.nlp_model.encode(str(sent1))
        vec2 = self.nlp_model.encode(str(sent2))
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def schedule_digest(self, user_id):
        user_data = self.db.users.find_one({'_id': user_id})
        if not user_data or not user_data.get('email_notifications', False):
            return

        engagement_times = self.get_user_engagement_times(user_id)
        if not engagement_times:
            schedule.every().day.at("09:00").do(self.send_digest, user_id)
        else:
            optimal_time = self.calculate_optimal_time(engagement_times)
            schedule.every().day.at(optimal_time.strftime("%H:%M")).do(self.send_digest, user_id)

    def get_user_engagement_times(self, user_id):
        week_ago = datetime.utcnow() - timedelta(days=7)
        user_activities = self.db.user_activities.find({
            'user_id': user_id,
            'timestamp': {'$gte': week_ago}
        })
        return [activity['timestamp'] for activity in user_activities]

    def calculate_optimal_time(self, engagement_times):
        if not engagement_times:
            return datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)

        # Convert to user's local timezone (if it's stored in user preferences)
        user_tz = pytz.timezone(self.db.users.find_one({'_id': user_id})['timezone'])
        local_times = [t.astimezone(user_tz) for t in engagement_times]

        # Find the hour with the most activity
        hour_counts = [0] * 24
        for t in local_times:
            hour_counts[t.hour] += 1
        optimal_hour = hour_counts.index(max(hour_counts))

        return datetime.now(user_tz).replace(hour=optimal_hour, minute=0, second=0, microsecond=0)

    def send_digest(self, user_id):
        user_data = self.db.users.find_one({'_id': user_id})
        if not user_data or not user_data.get('email_notifications', False):
            return

        notifications = self.get_user_notifications(user_id, limit=10)
        if not notifications:
            return

        subject = "Your Daily Digest"
        body = "<html><body>"
        body += "<h2>Here's your daily summary of activities:</h2>"
        for group in notifications:
            body += f"<h3>{group['count']} {group['type']} Notifications</h3>"
            body += f"<p>{group['summary']}</p>"
        body += "</body></html>"

        self.send_email(user_data['email'], subject, body)
        logger.info(f"Sent digest email to user {user_id}")

    def run_scheduler(self):
        while True:
            schedule.run_pending()
            time.sleep(60)

    def mark_as_read(self, user_id, notification_ids):
        try:
            result = self.db.notifications.update_many(
                {'_id': {'$in': notification_ids}, 'user_id': user_id},
                {'$set': {'read': True, 'read_at': datetime.utcnow()}}
            )
            logger.info(f"Marked {result.modified_count} notifications as read for user {user_id}")
            return result.modified_count
        except Exception as e:
            logger.error(f"Error marking notifications as read for user {user_id}: {str(e)}")
            return 0

# Initialize the NotificationSystem
client = MongoClient('mongodb://localhost:27017/')
db = client['telemedicine_app']

smtp_config = {
    'server': 'smtp.example.com',
    'port': 587,
    'username': 'noreply@example.com',
    'password': 'your_smtp_password'
}

firebase_config = {
    ## We gonna add Firebase configuration here
}

notification_system = NotificationSystem(db, smtp_config, firebase_config)

# Schedule digests for all users
for user in db.users.find({'email_notifications': True}):
    notification_system.schedule_digest(user['_id'])

