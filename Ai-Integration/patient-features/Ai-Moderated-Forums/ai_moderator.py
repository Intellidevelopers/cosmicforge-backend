import tensorflow as tf
from transformers import BertTokenizer, TFBertForSequenceClassification, GPT2LMHeadModel, GPT2Tokenizer
from googletrans import Translator
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from textblob import TextBlob
import torch
import logging
from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.ensemble import RandomForestClassifier
import joblib
from scipy.special import softmax
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIModeratorSystem:
    def __init__(self, db_connection):
        self.db = db_connection
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = TFBertForSequenceClassification.from_pretrained('bert-base-uncased')
        self.gpt_tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self.gpt_model = GPT2LMHeadModel.from_pretrained('gpt2')
        self.translator = Translator()
        self.sentiment_model = self.load_sentiment_model()
        self.behavior_model = self.load_behavior_model()
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        
    def load_sentiment_model(self):
        try:
            model_path = os.getenv('SENTIMENT_MODEL_PATH', 'models/sentiment_model')
            if os.path.exists(model_path):
                model = AutoModelForSequenceClassification.from_pretrained(model_path)
                logging.info("Loaded sentiment model from local path")
            else:
                model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
                model.save_pretrained(model_path)
                logging.info("Downloaded and saved sentiment model")
            
            model.eval()
            return model
        except Exception as e:
            logging.error(f"Error loading sentiment model: {str(e)}")
            raise

    def load_behavior_model(self):
        try:
            model_path = os.getenv('BEHAVIOR_MODEL_PATH', 'models/behavior_model.joblib')
            if os.path.exists(model_path):
                model = joblib.load(model_path)
                logging.info("Loaded behavior model from local path")
            else:
                # If no pre-trained model exists, create and train a new one
                model = self.train_behavior_model()
                joblib.dump(model, model_path)
                logging.info("Trained and saved new behavior model")
            return model
        except Exception as e:
            logging.error(f"Error loading behavior model: {str(e)}")
            raise

    def train_behavior_model(self):
        # Fetch historical user behavior data
        user_data = self.fetch_user_behavior_data()
        
        if len(user_data) == 0:
            logging.warning("No user behavior data available for training")
            return RandomForestClassifier(n_estimators=100, random_state=42)

        X = np.array([
            [
                d['post_frequency'],
                d['avg_post_length'],
                d['comment_frequency'],
                d['avg_comment_length'],
                d['report_count'],
                d['upvote_ratio'],
                d['avg_sentiment_score']
            ] for d in user_data
        ])
        y = np.array([d['is_problematic'] for d in user_data])

        model = RandomForestClassifier(
            n_estimators=200, 
            max_depth=10, 
            min_samples_split=5, 
            min_samples_leaf=2, 
            random_state=42,
            class_weight='balanced'
        )
        model.fit(X, y)
        return model

    def fetch_user_behavior_data(self):
        # Fetch and preprocess user behavior data from the database
        user_data = list(self.db.users.find({}, {
            'post_count': 1, 
            'comment_count': 1, 
            'total_post_length': 1, 
            'total_comment_length': 1, 
            'report_count': 1, 
            'upvotes': 1, 
            'downvotes': 1, 
            'is_banned': 1
        }))

        processed_data = []
        for user in user_data:
            post_count = user.get('post_count', 0)
            comment_count = user.get('comment_count', 0)
            total_post_length = user.get('total_post_length', 0)
            total_comment_length = user.get('total_comment_length', 0)
            report_count = user.get('report_count', 0)
            upvotes = user.get('upvotes', 0)
            downvotes = user.get('downvotes', 1)  

            processed_data.append({
                'post_frequency': post_count / 30,  # if data is for last 30 days
                'avg_post_length': total_post_length / post_count if post_count > 0 else 0,
                'comment_frequency': comment_count / 30,
                'avg_comment_length': total_comment_length / comment_count if comment_count > 0 else 0,
                'report_count': report_count,
                'upvote_ratio': upvotes / (upvotes + downvotes),
                'avg_sentiment_score': self.calculate_avg_sentiment_score(user['_id']),
                'is_problematic': user.get('is_banned', False)
            })

        return processed_data

    def calculate_avg_sentiment_score(self, user_id):
        # Calculate average sentiment score for user's recent posts and comments
        recent_content = list(self.db.posts.find({'user_id': user_id}).sort('created_at', -1).limit(10))
        recent_content.extend(list(self.db.comments.find({'user_id': user_id}).sort('created_at', -1).limit(10)))

        if not recent_content:
            return 0.5  # Neutral score if no recent content

        sentiment_scores = []
        for content in recent_content:
            inputs = self.sentiment_tokenizer(content['text'], return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)
            scores = outputs.logits.squeeze().numpy()
            sentiment_scores.append(softmax(scores)[1])  # Positive sentiment score

        return np.mean(sentiment_scores)

    def moderate_content(self, text, user_id):
        try:
            # Translate text to English if it's not in English
            detected_lang = self.translator.detect(text).lang
            if detected_lang != 'en':
                text = self.translator.translate(text, dest='en').text

            # BERT moderation
            bert_inputs = self.bert_tokenizer(text, return_tensors='tf', truncation=True, padding=True, max_length=512)
            bert_outputs = self.bert_model(bert_inputs)
            bert_probabilities = tf.nn.softmax(bert_outputs.logits, axis=-1)
            bert_inappropriate_prob = bert_probabilities[0][1].numpy()

            # GPT-2 perplexity check
            gpt_inputs = self.gpt_tokenizer.encode(text, return_tensors='pt')
            with torch.no_grad():
                gpt_outputs = self.gpt_model(gpt_inputs, labels=gpt_inputs)
                gpt_perplexity = torch.exp(gpt_outputs.loss).item()

            # Sentiment analysis
            sentiment_score = self.analyze_sentiment(text)

            # User behavior analysis
            user_behavior_score = self.analyze_user_behavior(user_id)

            # Combine all scores for final decision
            inappropriate_score = (
                bert_inappropriate_prob * 0.4 +
                min(gpt_perplexity / 100, 1) * 0.2 +
                (1 - sentiment_score) * 0.2 +
                user_behavior_score * 0.2
            )

            is_inappropriate = inappropriate_score > 0.6  # Adjust threshold as needed

            # Store moderation result
            self.store_moderation_result(user_id, text, is_inappropriate, inappropriate_score)

            return is_inappropriate, inappropriate_score

        except Exception as e:
            logger.error(f"Error in moderate_content: {str(e)}")
            return True, 1.0  # Err on the side of caution

    def analyze_sentiment(self, text):
        sentiment = self.sentiment_model(text).sentiment.polarity
        return (sentiment + 1) / 2  # Normalize to 0-1 range

    def analyze_user_behavior(self, user_id):
        try:
            user_history = self.get_user_content_history(user_id, days=30)
            if not user_history:
                return 0.5  # Neutral score for new users

            features = self.extract_behavior_features(user_history)
            behavior_score = self.behavior_model.predict_proba(features)[0][1]
            return behavior_score

        except Exception as e:
            logger.error(f"Error in analyze_user_behavior: {str(e)}")
            return 0.5  # Neutral score in case of error

    def get_user_content_history(self, user_id, days):
        cutoff_date = datetime.now() - timedelta(days=days)
        posts = list(self.db.posts.find({'user_id': user_id, 'created_at': {'$gte': cutoff_date}}))
        comments = list(self.db.comments.find({'user_id': user_id, 'created_at': {'$gte': cutoff_date}}))
        return posts + comments

    def extract_behavior_features(self, user_history):
        total_content = len(user_history)
        flagged_content = sum(1 for item in user_history if item.get('flagged', False))
        avg_sentiment = np.mean([self.analyze_sentiment(item['content']) for item in user_history])
        
        return pd.DataFrame({
            'total_content': [total_content],
            'flagged_ratio': [flagged_content / total_content if total_content > 0 else 0],
            'avg_sentiment': [avg_sentiment]
        })

    def store_moderation_result(self, user_id, content, is_inappropriate, inappropriate_score):
        moderation_result = {
            'user_id': user_id,
            'content': content,
            'is_inappropriate': is_inappropriate,
            'inappropriate_score': inappropriate_score,
            'timestamp': datetime.now()
        }
        self.db.moderation_results.insert_one(moderation_result)

    def moderate_post(self, post_id):
        try:
            post_data = self.db.posts.find_one({'post_id': post_id})
            if not post_data:
                raise ValueError("Post not found")

            is_inappropriate, inappropriate_score = self.moderate_content(post_data['content'], post_data['user_id'])

            if is_inappropriate:
                self.flag_content('post', post_id)
                self.notify_user(post_data['user_id'], "Your post has been flagged for review.")

            if inappropriate_score > 0.8:
                self.ban_user(post_data['user_id'])
                self.notify_user(post_data['user_id'], "Your account has been banned due to severe violations.")

            return is_inappropriate, inappropriate_score

        except Exception as e:
            logger.error(f"Error in moderate_post: {str(e)}")
            return True, 1.0  # Err on the side of caution

    def moderate_comment(self, comment_id):
        try:
            comment_data = self.db.comments.find_one({'comment_id': comment_id})
            if not comment_data:
                raise ValueError("Comment not found")

            is_inappropriate, inappropriate_score = self.moderate_content(comment_data['content'], comment_data['user_id'])

            if is_inappropriate:
                self.flag_content('comment', comment_id)
                self.notify_user(comment_data['user_id'], "Your comment has been flagged for review.")

            if inappropriate_score > 0.8:
                self.ban_user(comment_data['user_id'])
                self.notify_user(comment_data['user_id'], "Your account has been banned due to severe violations.")

            return is_inappropriate, inappropriate_score

        except Exception as e:
            logger.error(f"Error in moderate_comment: {str(e)}")
            return True, 1.0  # Err on the side of caution

    def flag_content(self, content_type, content_id):
        if content_type == 'post':
            self.db.posts.update_one({'post_id': content_id}, {'$set': {'flagged': True}})
        elif content_type == 'comment':
            self.db.comments.update_one({'comment_id': content_id}, {'$set': {'flagged': True}})

    def ban_user(self, user_id):
        self.db.users.update_one({'user_id': user_id}, {'$set': {'banned': True, 'ban_date': datetime.now()}})

    def notify_user(self, user_id, message):
        notification = {
            'user_id': user_id,
            'message': message,
            'timestamp': datetime.now(),
            'read': False
        }
        self.db.notifications.insert_one(notification)

    def appeal_moderation(self, content_type, content_id, user_id, appeal_reason):
        try:
            appeal_id = str(uuid.uuid4())
            appeal = {
                'appeal_id': appeal_id,
                'content_type': content_type,
                'content_id': content_id,
                'user_id': user_id,
                'appeal_reason': appeal_reason,
                'status': 'pending',
                'created_at': datetime.now()
            }
            self.db.appeals.insert_one(appeal)
            return appeal_id
        except Exception as e:
            logger.error(f"Error in appeal_moderation: {str(e)}")
            return None

    def review_appeal(self, appeal_id, moderator_id, decision, reason):
        try:
            appeal = self.db.appeals.find_one({'appeal_id': appeal_id})
            if not appeal:
                raise ValueError("Appeal not found")

            update_data = {
                'status': 'approved' if decision else 'rejected',
                'moderator_id': moderator_id,
                'decision_reason': reason,
                'reviewed_at': datetime.now()
            }
            self.db.appeals.update_one({'appeal_id': appeal_id}, {'$set': update_data})

            if decision:  # If appeal is approved
                if appeal['content_type'] == 'post':
                    self.db.posts.update_one({'post_id': appeal['content_id']}, {'$set': {'flagged': False}})
                elif appeal['content_type'] == 'comment':
                    self.db.comments.update_one({'comment_id': appeal['content_id']}, {'$set': {'flagged': False}})

            self.notify_user(appeal['user_id'], f"Your appeal has been {'approved' if decision else 'rejected'}. Reason: {reason}")

            return True
        except Exception as e:
            logger.error(f"Error in review_appeal: {str(e)}")
            return False

    def train_behavior_model(self):
        try:
            # Collect historical data
            user_data = list(self.db.users.find({}))
            features = []
            labels = []

            for user in user_data:
                user_history = self.get_user_content_history(user['user_id'], days=90)
                if user_history:
                    features.append(self.extract_behavior_features(user_history))
                    labels.append(1 if user.get('banned', False) else 0)

            if not features:
                logger.warning("No data available to train behavior model")
                return

            X = pd.concat(features, ignore_index=True)
            y = np.array(labels)

            # Split data and train model
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.behavior_model.fit(X_train, y_train)

            # Evaluate model
            accuracy = self.behavior_model.score(X_test, y_test)
            logger.info(f"Behavior model trained. Accuracy: {accuracy}")

        except Exception as e:
            logger.error(f"Error in train_behavior_model: {str(e)}")

# Initialize the AIModeratorSystem with a database connection
client = MongoClient('mongodb://localhost:27017/')
db = client['telemedicine_app']
ai_moderator = AIModeratorSystem(db)

# Train the behavior model
ai_moderator.train_behavior_model()
