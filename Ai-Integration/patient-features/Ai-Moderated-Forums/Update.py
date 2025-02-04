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


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/telemedicine_app')
    
    # SMTP configuration for email notifications. Use App Password to make it easier
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.example.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', 'noreply@example.com')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'your_smtp_password')
    
    # Firebase configuration for push notifications
    FIREBASE_CREDENTIALS = os.getenv('FIREBASE_CREDENTIALS', 'path/to/firebase_credentials.json')
    
    # AI model configurations
    BERT_MODEL = os.getenv('BERT_MODEL', 'bert-base-uncased')
    GPT2_MODEL = os.getenv('GPT2_MODEL', 'gpt2')
    T5_MODEL = os.getenv('T5_MODEL', 't5-small')
    
    # API keys and external service configurations
    GOOGLE_TRANSLATE_API_KEY = os.getenv('GOOGLE_TRANSLATE_API_KEY', 'your_google_translate_api_key')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here')
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

class TestingConfig(Config):
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/telemedicine_app_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from textblob import TextBlob
import language_tool_python
import gensim
from gensim.summarization import summarize
import difflib
import json
import uuid
from datetime import datetime
import logging
from pymongo import MongoClient
from bson.objectid import ObjectId
from nltk.corpus import cmudict
import re

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.classifier = MultinomialNB()
        self.language_tool = language_tool_python.LanguageTool('en-US')
        # Download the CMU Pronouncing Dictionary
        nltk.download('cmudict')
        self.cmu_dict = cmudict.dict()
        self.custom_exceptions = {
            'area': 3, 'idea': 3, 'real': 2, 'create': 2, 'being': 2,
            'doing': 2, 'going': 2, 'saying': 2, 'seeing': 2,
            'business': 2, 'evening': 2, 'interesting': 3,
            'everything': 3, 'beautiful': 3, 'science': 2
        }

    def preprocess_text(self, text):
        tokens = word_tokenize(text.lower())
        return ' '.join([word for word in tokens if word not in self.stop_words])

    def train_classifier(self, training_data):
        texts, labels = zip(*training_data)
        X = self.vectorizer.fit_transform([self.preprocess_text(text) for text in texts])
        self.classifier.fit(X, labels)

    def classify_content(self, text):
        preprocessed = self.preprocess_text(text)
        X = self.vectorizer.transform([preprocessed])
        return self.classifier.predict(X)[0]

    def create_post(self, user_id, forum_id, title, content):
        try:
            post_id = str(uuid.uuid4())
            preprocessed_content = self.preprocess_text(content)
            category = self.classify_content(preprocessed_content)
            tags = self.generate_tags(preprocessed_content)
            
            improved_content = self.improve_writing(content)
            summary = self.summarize_content(content)
            quality_score = self.calculate_content_quality(content)
            
            post_data = {
                'post_id': post_id,
                'user_id': user_id,
                'forum_id': forum_id,
                'title': title,
                'content': content,
                'improved_content': improved_content,
                'summary': summary,
                'category': category,
                'tags': tags,
                'quality_score': quality_score,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version_history': [{
                    'version': 1,
                    'content': content,
                    'timestamp': datetime.now()
                }]
            }
            
            self.db.posts.insert_one(post_data)
            return post_id
        except Exception as e:
            logger.error(f"Error in create_post: {str(e)}")
            raise

    def update_post(self, post_id, title=None, content=None):
        try:
            post_data = self.db.posts.find_one({'post_id': post_id})
            if not post_data:
                raise ValueError("Post not found")
            
            update_data = {}
            if title:
                update_data['title'] = title
            if content:
                preprocessed_content = self.preprocess_text(content)
                update_data['content'] = content
                update_data['improved_content'] = self.improve_writing(content)
                update_data['summary'] = self.summarize_content(content)
                update_data['category'] = self.classify_content(preprocessed_content)
                update_data['tags'] = self.generate_tags(preprocessed_content)
                update_data['quality_score'] = self.calculate_content_quality(content)
                update_data['updated_at'] = datetime.now()
                
                # Update version history
                new_version = len(post_data['version_history']) + 1
                post_data['version_history'].append({
                    'version': new_version,
                    'content': content,
                    'timestamp': datetime.now()
                })
                update_data['version_history'] = post_data['version_history']
            
            self.db.posts.update_one({'post_id': post_id}, {'$set': update_data})
            return True
        except Exception as e:
            logger.error(f"Error in update_post: {str(e)}")
            return False

    def delete_post(self, post_id):
        try:
            result = self.db.posts.delete_one({'post_id': post_id})
            if result.deleted_count == 0:
                raise ValueError("Post not found")
            self.db.comments.delete_many({'post_id': post_id})
            return True
        except Exception as e:
            logger.error(f"Error in delete_post: {str(e)}")
            return False

    def create_comment(self, user_id, post_id, content):
        try:
            comment_id = str(uuid.uuid4())
            preprocessed_content = self.preprocess_text(content)
            category = self.classify_content(preprocessed_content)
            improved_content = self.improve_writing(content)
            quality_score = self.calculate_content_quality(content)
            
            comment_data = {
                'comment_id': comment_id,
                'user_id': user_id,
                'post_id': post_id,
                'content': content,
                'improved_content': improved_content,
                'category': category,
                'quality_score': quality_score,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'version_history': [{
                    'version': 1,
                    'content': content,
                    'timestamp': datetime.now()
                }]
            }
            
            self.db.comments.insert_one(comment_data)
            return comment_id
        except Exception as e:
            logger.error(f"Error in create_comment: {str(e)}")
            raise

    def update_comment(self, comment_id, content):
        try:
            comment_data = self.db.comments.find_one({'comment_id': comment_id})
            if not comment_data:
                raise ValueError("Comment not found")
            
            preprocessed_content = self.preprocess_text(content)
            update_data = {
                'content': content,
                'improved_content': self.improve_writing(content),
                'category': self.classify_content(preprocessed_content),
                'quality_score': self.calculate_content_quality(content),
                'updated_at': datetime.now()
            }
            
            # Update version history
            new_version = len(comment_data['version_history']) + 1
            comment_data['version_history'].append({
                'version': new_version,
                'content': content,
                'timestamp': datetime.now()
            })
            update_data['version_history'] = comment_data['version_history']
            
            self.db.comments.update_one({'comment_id': comment_id}, {'$set': update_data})
            return True
        except Exception as e:
            logger.error(f"Error in update_comment: {str(e)}")
            return False

    def delete_comment(self, comment_id):
        try:
            result = self.db.comments.delete_one({'comment_id': comment_id})
            if result.deleted_count == 0:
                raise ValueError("Comment not found")
            return True
        except Exception as e:
            logger.error(f"Error in delete_comment: {str(e)}")
            return False

    def generate_tags(self, text):
        tfidf = TfidfVectorizer(max_features=5)
        tfidf_matrix = tfidf.fit_transform([text])
        feature_names = tfidf.get_feature_names_out()
        tags = [feature_names[i] for i in tfidf_matrix.sum(axis=0).argsort()[0, -5:]]
        return tags

    def improve_writing(self, text):
        # Use LanguageTool for grammar and style improvements
        matches = self.language_tool.check(text)
        improved_text = language_tool_python.utils.correct(text, matches)
        
        # Use TextBlob for sentiment analysis and subjectivity detection
        blob = TextBlob(improved_text)
        if blob.sentiment.polarity < 0:
            improved_text += "\n\nNote: This content may have a negative tone. Consider revising for a more positive approach."
        if blob.sentiment.subjectivity > 0.5:
            improved_text += "\n\nNote: This content may be overly subjective. Consider adding more factual information."
        
        return improved_text

    def summarize_content(self, text):
        try:
            # Use gensim for text summarization
            summary = summarize(text, ratio=0.6)  # Summarize to 60% of original length
            return summary if summary else "Unable to generate summary."
        except Exception as e:
            logger.error(f"Error in summarize_content: {str(e)}")
            return "Unable to generate summary."

    def calculate_content_quality(self, text):
        try:
            # Readability score (using Flesch Reading Ease)
            blob = TextBlob(text)
            readability = self.flesch_reading_ease(text)
            
            # Informativeness (using unique word count)
            unique_words = set(word_tokenize(text.lower()))
            informativeness = len(unique_words) / len(word_tokenize(text))
            
            # Engagement (using sentiment polarity)
            engagement = abs(blob.sentiment.polarity)
            
            # Calculate overall quality score
            quality_score = (readability * 0.4) + (informativeness * 0.3) + (engagement * 0.3)
            return min(max(quality_score * 100, 0), 100)  # Normalize to 0-100 range
        except Exception as e:
            logger.error(f"Error in calculate_content_quality: {str(e)}")
            return 50  

    def flesch_reading_ease(self, text):
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        syllables = sum(self.count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
        return max(min(score, 100), 0) / 100  # Normalize to 0-1 range

    def count_syllables(self, word):
        word = word.lower().strip()
        
        # Check custom exceptions first
        if word in self.custom_exceptions:
            return self.custom_exceptions[word]
        
        # Try to use CMU Pronouncing Dictionary
        if word in self.cmu_dict:
            return max([len(list(y for y in x if y[-1].isdigit())) for x in self.cmu_dict[word]])
        
        # If word not in CMU dict, use advanced rule-based method
        return self.rule_based_syllable_count(word)

    def rule_based_syllable_count(self, word):
        word = word.lower()
        word = word.replace('\'', '')  # Remove apostrophes
        
        # Exception: Ends with "le" or "les"
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiou':
            return self.rule_based_syllable_count(word[:-2]) + 1
        if word.endswith('les') and len(word) > 3 and word[-4] not in 'aeiou':
            return self.rule_based_syllable_count(word[:-3]) + 1
        
        # Exception: Ends with "es" or "ed", but not "les" or "ded"
        if word.endswith(('es', 'ed')) and not word.endswith(('les', 'ded', 'ies')):
            word = word[:-2]
        
        # Count vowel groups
        count = len(re.findall(r'[aeiou]+', word))
        
        # Adjust for silent 'e' at the end
        if word.endswith('e'):
            count -= 1
        
        # Adjust for words ending with 'le'
        if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiou':
            count += 1
        
        # Adjust for 'io' and 'ia' which often form two syllables
        count += len(re.findall(r'[aeiou][io]', word))
        
        # Ensure at least one syllable
        return max(1, count)                

    def get_post_version_diff(self, post_id, version1, version2):
        try:
            post_data = self.db.posts.find_one({'post_id': post_id})
            if not post_data:
                raise ValueError("Post not found")
            
            version_history = post_data['version_history']
            content1 = next((v['content'] for v in version_history if v['version'] == version1), None)
            content2 = next((v['content'] for v in version_history if v['version'] == version2), None)
            
            if content1 is None or content2 is None:
                raise ValueError("Invalid version numbers")
            
            diff = difflib.unified_diff(content1.splitlines(), content2.splitlines(), lineterm='')
            return '\n'.join(diff)
        except Exception as e:
            logger.error(f"Error in get_post_version_diff: {str(e)}")
            return None

# Initialize the ContentManager with a database connection
client = MongoClient('mongodb://localhost:27017/')
db = client['telemedicine_app']
content_manager = ContentManager(db)

# Train the classifier with sample data
sample_data = [
    ("This is a post about diabetes management", "health"),
    ("Looking for advice on heart disease prevention", "health"),
    ("Spam message about miracle cures", "spam"),
    # We Would Add more training data as needed
]
content_manager.train_classifier(sample_data)

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from config import Config

logger = logging.getLogger(__name__)

class Database:
    _instance = None

    @staticmethod
    def get_instance():
        if Database._instance is None:
            Database()
        return Database._instance

    def __init__(self):
        if Database._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Database._instance = self
            self.client = None
            self.db = None
            self.connect()

    def connect(self):
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client.get_database()
            self.client.admin.command('ismaster')
            logger.info("Successfully connected to the database")
        except ConnectionFailure:
            logger.error("Server not available")
            raise

    def close(self):
        if self.client:
            self.client.close()
            logger.info("Database connection closed")

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_one(self, collection_name, document):
        collection = self.get_collection(collection_name)
        return collection.insert_one(document)

    def find_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find(query)

    def update_one(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        return collection.update_one(query, update)

    def delete_one(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.delete_one(query)

    def create_index(self, collection_name, keys, **kwargs):
        collection = self.get_collection(collection_name)
        return collection.create_index(keys, **kwargs)

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import networkx as nx
from datetime import datetime, timedelta
import logging  
import torch
from transformers import AutoTokenizer, AutoModel
from pymedtermino import *
from pymedtermino.snomedct import *
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForumManager:
    def __init__(self, db_connection):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.kmeans = KMeans(n_clusters=10, random_state=42)
        self.db = db_connection
        self.health_condition_model = self.load_health_condition_model()
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
        self.model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
        self.snomed = SNOMEDCT()
        self.logger = logging.getLogger(__name__)
     
    def load_health_condition_model(self):
        try:
            # Load SNOMED CT concepts for major health conditions
            major_conditions = [
                'Diabetes mellitus', 'Cardiovascular disease', 'Neoplastic disease', 
                'Respiratory disease', 'Neurological disorder', 'Mental disorder',
                'Gastrointestinal disease', 'Musculoskeletal disorder', 'Endocrine system disorder',
                'Infectious disease', 'Autoimmune disease', 'Renal disorder'
            ]

            health_condition_model = {}

            for condition in major_conditions:
                concepts = self.snomed.search(condition)
                if concepts:
                    main_concept = concepts[0]
                    related_terms = self.get_related_terms(main_concept)
                    health_condition_model[condition] = related_terms

            # Enrich the model with data from external medical APIs
            self.enrich_model_with_external_data(health_condition_model)

            return health_condition_model

        except Exception as e:
            self.logger.error(f"Error loading health condition model: {str(e)}")
            raise

    def get_related_terms(self, concept, max_depth=2):
        related_terms = set()
        queue = [(concept, 0)]

        while queue:
            current_concept, depth = queue.pop(0)
            if depth > max_depth:
                continue

            related_terms.add(current_concept.term)

            # Add synonyms
            related_terms.update(current_concept.synonyms)

            # Add children concepts
            for child in current_concept.children:
                queue.append((child, depth + 1))

        return list(related_terms)

    def enrich_model_with_external_data(self, health_condition_model):
        try:
            # Using the MedlinePlus API to enrich our model
            base_url = "https://connect.medlineplus.gov/service" ## I will move this to .env file

            for condition, terms in health_condition_model.items():
                params = {
                    "mainSearchCriteria.v.cs": "2.16.840.1.113883.6.96",
                    "mainSearchCriteria.v.c": self.snomed.search(condition)[0].code,
                    "knowledgeResponseType": "application/json",
                }
                response = requests.get(base_url, params=params)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    for entry in data.get('feed', {}).get('entry', []):
                        title = entry.get('title', '')
                        if title and title not in terms:
                            terms.append(title)

        except Exception as e:
            self.logger.error(f"Error enriching model with external data: {str(e)}")

    def categorize_forum(self, forum_description):
        try:
            # Encode the forum description
            inputs = self.tokenizer(forum_description, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
            with torch.no_grad():
                outputs = self.model(**inputs)
            forum_embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

            # Compare with each health condition
            similarities = {}
            for condition, terms in self.health_condition_model.items():
                condition_embeddings = []
                for term in terms:
                    inputs = self.tokenizer(term, return_tensors="pt", max_length=512, truncation=True, padding="max_length")
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                    condition_embeddings.append(outputs.last_hidden_state.mean(dim=1).squeeze().numpy())
                
                avg_condition_embedding = np.mean(condition_embeddings, axis=0)
                similarity = cosine_similarity([forum_embedding], [avg_condition_embedding])[0][0]
                similarities[condition] = similarity

            # Get the most similar condition
            best_match = max(similarities, key=similarities.get)
            confidence = similarities[best_match]

            return best_match, confidence

        except Exception as e:
            self.logger.error(f"Error categorizing forum: {str(e)}")
            return "Uncategorized", 0.0

    def suggest_forum_topics(self, existing_topics, new_posts):
        try:
            all_text = existing_topics + new_posts
            tfidf_matrix = self.vectorizer.fit_transform(all_text)
            self.kmeans.fit(tfidf_matrix)
            cluster_centers = self.kmeans.cluster_centers_
            order_centroids = cluster_centers.argsort()[:, ::-1]
            terms = self.vectorizer.get_feature_names_out()

            suggested_topics = []
            for i in range(self.kmeans.n_clusters):
                topic_terms = [terms[ind] for ind in order_centroids[i, :5]]
                suggested_topics.append(" ".join(topic_terms))

            return suggested_topics
        except Exception as e:
            logger.error(f"Error in suggest_forum_topics: {str(e)}")
            return []

    def categorize_forum(self, forum_description):
        try:
            processed_description = self.preprocess_text(forum_description)
            scores = {}
            for category, keywords in self.health_model.items():
                score = sum(1 for keyword in keywords if keyword in processed_description)
                scores[category] = score
            return max(scores, key=scores.get)
        except Exception as e:
            logger.error(f"Error in categorize_forum: {str(e)}")
            return "Uncategorized"

    def preprocess_text(self, text):
        return text.lower()

    def create_forum(self, title, description, parent_forum_id=None):
        try:
            forum_id = self.generate_unique_id()
            category = self.categorize_forum(description)
            tags = self.extract_tags(description)
            
            forum_data = {
                'id': forum_id,
                'title': title,
                'description': description,
                'category': category,
                'tags': tags,
                'parent_forum_id': parent_forum_id,
                'created_at': datetime.now(),
                'health_score': 100  # Initial perfect health score
            }
            
            self.db.forums.insert_one(forum_data)
            
            if parent_forum_id:
                self.db.forums.update_one(
                    {'id': parent_forum_id},
                    {'$push': {'sub_forums': forum_id}}
                )
            
            return forum_id
        except Exception as e:
            logger.error(f"Error in create_forum: {str(e)}")
            return None

    def update_forum(self, forum_id, title=None, description=None):
        try:
            update_data = {}
            if title:
                update_data['title'] = title
            if description:
                update_data['description'] = description
                update_data['category'] = self.categorize_forum(description)
                update_data['tags'] = self.extract_tags(description)
            
            self.db.forums.update_one({'id': forum_id}, {'$set': update_data})
            return True
        except Exception as e:
            logger.error(f"Error in update_forum: {str(e)}")
            return False

    def delete_forum(self, forum_id):
        try:
            # Get all sub-forums
            sub_forums = self.db.forums.find({'parent_forum_id': forum_id})
            
            # Recursively delete sub-forums
            for sub_forum in sub_forums:
                self.delete_forum(sub_forum['id'])
            
            # Delete all associated posts and comments
            self.db.posts.delete_many({'forum_id': forum_id})
            self.db.comments.delete_many({'forum_id': forum_id})
            
            # Delete the forum itself
            self.db.forums.delete_one({'id': forum_id})
            
            # Remove reference from parent forum if exists
            self.db.forums.update_one(
                {'sub_forums': forum_id},
                {'$pull': {'sub_forums': forum_id}}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error in delete_forum: {str(e)}")
            return False

    def generate_unique_id(self):
        return str(uuid.uuid4())

    def extract_tags(self, text):
        blob = TextBlob(text)
        return [word for word, pos in blob.tags if pos.startswith('NN')][:5]  # Extract up to 5 nouns as tags

    def merge_similar_forums(self, similarity_threshold=0.8):
        try:
            forums = list(self.db.forums.find({}))
            forum_descriptions = [forum['description'] for forum in forums]
            
            tfidf_matrix = self.vectorizer.fit_transform(forum_descriptions)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            for i in range(len(forums)):
                for j in range(i + 1, len(forums)):
                    if similarity_matrix[i][j] > similarity_threshold:
                        self.merge_forums(forums[i]['id'], forums[j]['id'])
            
            return True
        except Exception as e:
            logger.error(f"Error in merge_similar_forums: {str(e)}")
            return False

    def merge_forums(self, forum_id1, forum_id2):
        try:
            forum1 = self.db.forums.find_one({'id': forum_id1})
            forum2 = self.db.forums.find_one({'id': forum_id2})
            
            merged_title = f"{forum1['title']} & {forum2['title']}"
            merged_description = f"{forum1['description']}\n\n{forum2['description']}"
            merged_tags = list(set(forum1['tags'] + forum2['tags']))
            
            merged_forum_id = self.create_forum(merged_title, merged_description)
            
            # Move all posts and comments to the new merged forum
            self.db.posts.update_many({'forum_id': {'$in': [forum_id1, forum_id2]}}, {'$set': {'forum_id': merged_forum_id}})
            self.db.comments.update_many({'forum_id': {'$in': [forum_id1, forum_id2]}}, {'$set': {'forum_id': merged_forum_id}})
            
            # Delete the old forums
            self.delete_forum(forum_id1)
            self.delete_forum(forum_id2)
            
            return merged_forum_id
        except Exception as e:
            logger.error(f"Error in merge_forums: {str(e)}")
            return None

    def calculate_forum_health_score(self, forum_id):
        try:
            forum = self.db.forums.find_one({'id': forum_id})
            posts = list(self.db.posts.find({'forum_id': forum_id}))
            comments = list(self.db.comments.find({'forum_id': forum_id}))
            
            # Activity score
            post_count = len(posts)
            comment_count = len(comments)
            activity_score = min(post_count + comment_count, 100)  # Cap at 100
            
            # Quality score
            sentiment_scores = [TextBlob(post['content']).sentiment.polarity for post in posts]
            sentiment_scores += [TextBlob(comment['content']).sentiment.polarity for comment in comments]
            quality_score = ((np.mean(sentiment_scores) + 1) / 2) * 100 if sentiment_scores else 50
            
            # Engagement score
            unique_users = set([post['user_id'] for post in posts] + [comment['user_id'] for comment in comments])
            engagement_score = min(len(unique_users) * 10, 100)  # 10 points per unique user, cap at 100
            
            # Calculate overall health score
            health_score = (activity_score * 0.4) + (quality_score * 0.3) + (engagement_score * 0.3)
            
            # Update forum health score
            self.db.forums.update_one({'id': forum_id}, {'$set': {'health_score': health_score}})
            
            return health_score
        except Exception as e:
            logger.error(f"Error in calculate_forum_health_score: {str(e)}")
            return 0

    def get_trending_topics(self, time_period=timedelta(days=7)):
        try:
            cutoff_date = datetime.now() - time_period
            recent_posts = self.db.posts.find({'created_at': {'$gte': cutoff_date}})
            post_contents = [post['content'] for post in recent_posts]
            
            if not post_contents:
                return []
            
            tfidf_matrix = self.vectorizer.fit_transform(post_contents)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Calculate average TF-IDF scores
            avg_tfidf = np.array(tfidf_matrix.mean(axis=0)).flatten()
            trending_indices = avg_tfidf.argsort()[-10:][::-1]  # Top 10 trending topics
            
            return [feature_names[i] for i in trending_indices]
        except Exception as e:
            logger.error(f"Error in get_trending_topics: {str(e)}")
            return []

    def create_dynamic_forum(self, user_interests):
        try:
            trending_topics = self.get_trending_topics()
            relevant_topics = [topic for topic in trending_topics if any(interest in topic for interest in user_interests)]
            
            if relevant_topics:
                title = f"Trending: {' & '.join(relevant_topics[:3])}"
                description = f"A forum for discussing trending topics related to {', '.join(relevant_topics)}"
                return self.create_forum(title, description)
            else:
                return None
        except Exception as e:
            logger.error(f"Error in create_dynamic_forum: {str(e)}")
            return None

forum_manager = ForumManager(db_connection)


import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from config import config, Config
from database import Database
from forum_manager import ForumManager
from user_manager import UserManager
from content_manager import ContentManager
from ai_moderator import AIModeratorSystem
from search_discovery import SearchAndDiscoverySystem
from notification_system import NotificationSystem

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Set up logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Telemedicine app startup')

    # Initialize database
    db = Database.get_instance()

    # Initialize all system components
    forum_manager = ForumManager(db)
    user_manager = UserManager(db)
    content_manager = ContentManager(db)
    ai_moderator = AIModeratorSystem(db)
    search_discovery = SearchAndDiscoverySystem(db)
    notification_system = NotificationSystem(db, {
        'server': Config.SMTP_SERVER,
        'port': Config.SMTP_PORT,
        'username': Config.SMTP_USERNAME,
        'password': Config.SMTP_PASSWORD
    }, Config.FIREBASE_CREDENTIALS)

## WE TAKE NOTE OF THIS:
    # Register blueprints (routes) here
    # from .api import api as api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.close()

    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(debug=Config.DEBUG)
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from config import config, Config
from database import Database
from forum_manager import ForumManager
from user_manager import UserManager
from content_manager import ContentManager
from ai_moderator import AIModeratorSystem
from search_discovery import SearchAndDiscoverySystem
from notification_system import NotificationSystem

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Set up logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Telemedicine app startup')

    # Initialize database
    db = Database.get_instance()

    # Initialize all system components
    forum_manager = ForumManager(db)
    user_manager = UserManager(db)
    content_manager = ContentManager(db)
    ai_moderator = AIModeratorSystem(db)
    search_discovery = SearchAndDiscoverySystem(db)
    notification_system = NotificationSystem(db, {
        'server': Config.SMTP_SERVER,
        'port': Config.SMTP_PORT,
        'username': Config.SMTP_USERNAME,
        'password': Config.SMTP_PASSWORD
    }, Config.FIREBASE_CREDENTIALS)

## WE TAKE NOTE OF THIS:
    # Register blueprints (routes) here
    # from .api import api as api_blueprint
    # app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.close()

    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.run(debug=Config.DEBUG)

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

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import nltk
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from pymongo import MongoClient
from datetime import datetime, timedelta
import logging
import re

nltk.download('punkt')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchAndDiscoverySystem:
    def __init__(self, db_connection):
        self.db = db_connection
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        self.word2vec_model = None
        self.doc2vec_model = None
        self.post_vectors = None
        self.post_ids = None
        self.user_item_matrix = None
        self.als_model = AlternatingLeastSquares(factors=50, regularization=0.01, iterations=50)
        self.t5_tokenizer = T5Tokenizer.from_pretrained('t5-small')
        self.t5_model = T5ForConditionalGeneration.from_pretrained('t5-small')

    def preprocess_text(self, text):
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Convert to lowercase and tokenize
        return word_tokenize(text.lower())

    def train_word_embeddings(self):
        all_posts = list(self.db.posts.find({}, {'content': 1}))
        sentences = [self.preprocess_text(post['content']) for post in all_posts]
        self.word2vec_model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

    def train_document_embeddings(self):
        all_posts = list(self.db.posts.find({}, {'_id': 1, 'content': 1}))
        tagged_data = [TaggedDocument(words=self.preprocess_text(post['content']), tags=[str(post['_id'])]) for post in all_posts]
        self.doc2vec_model = Doc2Vec(vector_size=100, min_count=2, epochs=40)
        self.doc2vec_model.build_vocab(tagged_data)
        self.doc2vec_model.train(tagged_data, total_examples=self.doc2vec_model.corpus_count, epochs=self.doc2vec_model.epochs)

    def index_posts(self):
        all_posts = list(self.db.posts.find({}, {'_id': 1, 'content': 1}))
        post_contents = [post['content'] for post in all_posts]
        self.post_ids = [str(post['_id']) for post in all_posts]
        self.post_vectors = self.tfidf_vectorizer.fit_transform(post_contents)

    def semantic_search(self, query, top_n=10):
        query_vector = self.doc2vec_model.infer_vector(self.preprocess_text(query))
        sims = self.doc2vec_model.dv.most_similar([query_vector], topn=top_n)
        return [(post_id, score) for post_id, score in sims]

    def hybrid_search(self, query, top_n=10):
        tfidf_results = self.tfidf_search(query, top_n)
        semantic_results = self.semantic_search(query, top_n)
        
        # Combine and normalize scores
        combined_results = {}
        for post_id, score in tfidf_results + semantic_results:
            if post_id in combined_results:
                combined_results[post_id] += score
            else:
                combined_results[post_id] = score
        
        # Normalize and sort results
        max_score = max(combined_results.values())
        normalized_results = [(post_id, score/max_score) for post_id, score in combined_results.items()]
        return sorted(normalized_results, key=lambda x: x[1], reverse=True)[:top_n]

    def tfidf_search(self, query, top_n=10):
        query_vector = self.tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.post_vectors).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]
        return [(self.post_ids[i], similarities[i]) for i in top_indices]

    def build_user_item_matrix(self):
        interactions = list(self.db.interactions.find({}))
        users = list(self.db.users.find({}, {'_id': 1}))
        posts = list(self.db.posts.find({}, {'_id': 1}))
        
        user_dict = {str(user['_id']): i for i, user in enumerate(users)}
        post_dict = {str(post['_id']): i for i, post in enumerate(posts)}
        
        matrix = np.zeros((len(users), len(posts)))
        
        for interaction in interactions:
            user_idx = user_dict.get(str(interaction['user_id']))
            post_idx = post_dict.get(str(interaction['post_id']))
            if user_idx is not None and post_idx is not None:
                matrix[user_idx, post_idx] = interaction['score']
        
        self.user_item_matrix = csr_matrix(matrix)
        self.als_model.fit(self.user_item_matrix)

    def get_collaborative_recommendations(self, user_id, top_n=10):
        user_idx = next(i for i, user in enumerate(self.db.users.find()) if str(user['_id']) == user_id)
        posts = list(self.db.posts.find({}, {'_id': 1}))
        
        user_vector = self.user_item_matrix[user_idx]
        recommendations = self.als_model.recommend(user_idx, user_vector, N=top_n, filter_already_liked_items=True)
        
        return [(str(posts[post_idx]['_id']), score) for post_idx, score in recommendations]

    def get_personalized_feed(self, user_id, top_n=20):
        user_data = self.db.users.find_one({'_id': user_id})
        user_interests = ' '.join(user_data.get('health_interests', []) + user_data.get('conditions', []))
        
        # Combine different recommendation methods
        content_based = self.hybrid_search(user_interests, top_n)
        collaborative = self.get_collaborative_recommendations(user_id, top_n)
        
        # Merge and deduplicate results
        combined_results = {}
        for post_id, score in content_based + collaborative:
            if post_id in combined_results:
                combined_results[post_id] = max(combined_results[post_id], score)
            else:
                combined_results[post_id] = score
        
        # Sort and return top results
        return sorted(combined_results.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def identify_trending_topics(self, time_period=24):
        cutoff_time = datetime.now() - timedelta(hours=time_period)
        recent_posts = list(self.db.posts.find({'created_at': {'$gte': cutoff_time}}, {'content': 1}))
        
        if not recent_posts:
            return []
        
        post_contents = [post['content'] for post in recent_posts]
        vectorized_posts = self.tfidf_vectorizer.fit_transform(post_contents)
        
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        tfidf_sums = vectorized_posts.sum(axis=0).A1
        
        top_n = 10
        top_indices = tfidf_sums.argsort()[-top_n:][::-1]
        trending_topics = [feature_names[i] for i in top_indices]
        
        return trending_topics

    def generate_faq(self, topic, num_questions=5):
        # Fetch relevant posts
        relevant_posts = list(self.db.posts.find({'$text': {'$search': topic}}, {'content': 1}).limit(20))
        
        if not relevant_posts:
            return []
        
        # Combine post contents
        combined_content = " ".join([post['content'] for post in relevant_posts])
        
        # Generate questions using T5
        input_text = f"generate {num_questions} questions: {combined_content}"
        input_ids = self.t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).input_ids
        
        outputs = self.t5_model.generate(
            input_ids,
            max_length=64,
            num_return_sequences=num_questions,
            num_beams=4,
            no_repeat_ngram_size=2,
            early_stopping=True
        )
        
        questions = [self.t5_tokenizer.decode(output, skip_special_tokens=True) for output in outputs]
        
        # Generate answers
        faq = []
        for question in questions:
            input_text = f"answer: {question} context: {combined_content}"
            input_ids = self.t5_tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True).input_ids
            
            outputs = self.t5_model.generate(
                input_ids,
                max_length=128,
                num_beams=4,
                no_repeat_ngram_size=3,
                early_stopping=True
            )
            
            answer = self.t5_tokenizer.decode(outputs[0], skip_special_tokens=True)
            faq.append({"question": question, "answer": answer})
        
        return faq

    def update_models(self):
        self.train_word_embeddings()
        self.train_document_embeddings()
        self.index_posts()
        self.build_user_item_matrix()

# Initialize the SearchAndDiscoverySystem with a database connection
client = MongoClient('mongodb://localhost:27017/')
db = client['telemedicine_app']
search_system = SearchAndDiscoverySystem(db)

##  Initial training and indexing
search_system.update_models()

import bcrypt
import pyotp
import qrcode
import io
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import numpy as np
from datetime import datetime, timedelta
import logging
import uuid
from pymongo import MongoClient
from bson.objectid import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(self, db_connection):
        self.db = db_connection
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def register_user(self, username, email, password, health_interests):
        try:
            if self.user_exists(username, email):
                raise ValueError("Username or email already exists")
            
            user_id = str(uuid.uuid4())
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            totp_secret = pyotp.random_base32()
            
            user_data = {
                'user_id': user_id,
                'username': username,
                'email': email,
                'password': hashed_password,
                'health_interests': health_interests,
                'totp_secret': totp_secret,
                'trust_score': 50,  # Initial trust score
                'level': 1,
                'experience_points': 0,
                'badges': [],
                'mentor_id': None,
                'mentee_ids': [],
                'created_at': datetime.now()
            }
            
            self.db.users.insert_one(user_data)
            return user_id
        except Exception as e:
            logger.error(f"Error in register_user: {str(e)}")
            raise

    def user_exists(self, username, email):
        return self.db.users.find_one({'$or': [{'username': username}, {'email': email}]}) is not None

    def authenticate_user(self, username, password, totp_code):
        try:
            user_data = self.db.users.find_one({'username': username})
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password']):
                totp = pyotp.TOTP(user_data['totp_secret'])
                if totp.verify(totp_code):
                    return user_data['user_id']
            return None
        except Exception as e:
            logger.error(f"Error in authenticate_user: {str(e)}")
            return None

    def get_totp_qr_code(self, user_id):
        try:
            user_data = self.db.users.find_one({'user_id': user_id})
            if user_data:
                totp = pyotp.TOTP(user_data['totp_secret'])
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(totp.provisioning_uri(user_data['email'], issuer_name="Telemedicine App"))
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                return base64.b64encode(buffered.getvalue()).decode()
            return None
        except Exception as e:
            logger.error(f"Error in get_totp_qr_code: {str(e)}")
            return None

    def update_user_profile(self, user_id, health_interests=None, conditions=None):
        try:
            update_data = {}
            if health_interests:
                update_data['health_interests'] = health_interests
            if conditions:
                update_data['conditions'] = conditions
            
            self.db.users.update_one({'user_id': user_id}, {'$set': update_data})
            return True
        except Exception as e:
            logger.error(f"Error in update_user_profile: {str(e)}")
            return False

    def calculate_user_trust_score(self, user_id):
        try:
            user_content = self.get_user_content(user_id)
            post_count = len(user_content['posts'])
            comment_count = len(user_content['comments'])
            upvotes = sum(post['upvotes'] for post in user_content['posts'])
            downvotes = sum(post['downvotes'] for post in user_content['posts'])
            
            # Content quality score
            content_scores = [TextBlob(post['content']).sentiment.polarity for post in user_content['posts']]
            content_scores += [TextBlob(comment['content']).sentiment.polarity for comment in user_content['comments']]
            avg_content_score = np.mean(content_scores) if content_scores else 0
            
            # Peer review score
            peer_reviews = self.db.peer_reviews.find({'reviewed_user_id': user_id})
            avg_peer_score = np.mean([review['score'] for review in peer_reviews]) if peer_reviews.count() > 0 else 0
            
            # Calculate trust score
            activity_score = min((post_count + comment_count) / 10, 10)  # Cap at 10
            quality_score = ((upvotes - downvotes) / max(upvotes + downvotes, 1)) * 10
            content_quality_score = (avg_content_score + 1) * 5  # Scale to 0-10
            peer_score = avg_peer_score
            
            trust_score = (activity_score * 0.3) + (quality_score * 0.3) + (content_quality_score * 0.2) + (peer_score * 0.2)
            trust_score = max(min(trust_score * 10, 100), 0)  # Scale to 0-100 and clamp
            
            self.db.users.update_one({'user_id': user_id}, {'$set': {'trust_score': trust_score}})
            return trust_score
        except Exception as e:
            logger.error(f"Error in calculate_user_trust_score: {str(e)}")
            return 0

    def get_user_content(self, user_id):
        posts = list(self.db.posts.find({'user_id': user_id}))
        comments = list(self.db.comments.find({'user_id': user_id}))
        return {'posts': posts, 'comments': comments}

    def update_user_experience(self, user_id, action):
        try:
            user_data = self.db.users.find_one({'user_id': user_id})
            if not user_data:
                return False
            
            experience_points = user_data['experience_points']
            level = user_data['level']
            
            # Define experience points for different actions
            action_points = {
                'post': 10,
                'comment': 5,
                'upvote_received': 2,
                'best_answer': 15
            }
            
            if action in action_points:
                experience_points += action_points[action]
                
                # Check for level up
                new_level = 1 + (experience_points // 100)  # Level up every 100 points
                if new_level > level:
                    level = new_level
                    self.award_badge(user_id, f"Level {level}")
                
                self.db.users.update_one(
                    {'user_id': user_id},
                    {'$set': {'experience_points': experience_points, 'level': level}}
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error in update_user_experience: {str(e)}")
            return False

    def award_badge(self, user_id, badge_name):
        try:
            self.db.users.update_one(
                {'user_id': user_id},
                {'$addToSet': {'badges': badge_name}}
            )
            return True
        except Exception as e:
            logger.error(f"Error in award_badge: {str(e)}")
            return False

    def get_similar_users(self, user_id):
        try:
            all_users = list(self.db.users.find({}, {'user_id': 1, 'health_interests': 1, 'conditions': 1}))
            corpus = [' '.join(user.get('health_interests', []) + user.get('conditions', [])) for user in all_users]
            
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            user_index = next(i for i, user in enumerate(all_users) if user['user_id'] == user_id)
            cosine_similarities = cosine_similarity(tfidf_matrix[user_index], tfidf_matrix).flatten()
            
            similar_users = sorted(list(enumerate(cosine_similarities)), key=lambda x: x[1], reverse=True)[1:6]
            return [all_users[i]['user_id'] for i, _ in similar_users]
        except Exception as e:
            logger.error(f"Error in get_similar_users: {str(e)}")
            return []

    def assign_mentor(self, mentee_id):
        try:
            mentee = self.db.users.find_one({'user_id': mentee_id})
            if not mentee:
                return False
            
            potential_mentors = self.db.users.find({
                'level': {'$gt': mentee['level']},
                'health_interests': {'$in': mentee['health_interests']},
                'mentee_ids': {'$not': {'$size': 3}}  # Limit to mentors with less than 3 mentees
            }).sort('trust_score', -1).limit(1)
            
            if potential_mentors.count() > 0:
                mentor = potential_mentors[0]
                self.db.users.update_one(
                    {'user_id': mentor['user_id']},
                    {'$addToSet': {'mentee_ids': mentee_id}}
                )
                self.db.users.update_one(
                    {'user_id': mentee_id},
                    {'$set': {'mentor_id': mentor['user_id']}}
                )
                return True
            return False
        except Exception as e:
            logger.error(f"Error in assign_mentor: {str(e)}")
            return False

# Initialize the UserManager with a database connection
client = MongoClient('mongodb://localhost:27017/')
db = client['telemedicine_app']
user_manager = UserManager(db)
