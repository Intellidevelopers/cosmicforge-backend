import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from textblob import TextBlob
import networkx as nx
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ForumManager:
    def __init__(self, db_connection):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.kmeans = KMeans(n_clusters=10, random_state=42)
        self.db = db_connection
        self.health_model = self.load_health_condition_model()

    def load_health_condition_model(self):
        # In a real-world scenario, this would load a pre-trained model
        # For this example, we'll use a simple keyword-based approach
        return {
            'diabetes': ['diabetes', 'insulin', 'glucose'],
            'heart disease': ['heart', 'cardiovascular', 'cholesterol'],
            'cancer': ['cancer', 'tumor', 'oncology'],
            # Add more health conditions and related keywords
        }

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
