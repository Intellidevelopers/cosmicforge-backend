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
