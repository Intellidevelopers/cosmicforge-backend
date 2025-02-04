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
