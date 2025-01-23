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

