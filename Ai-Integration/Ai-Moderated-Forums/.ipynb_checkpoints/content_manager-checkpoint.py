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
            summary = summarize(text, ratio=0.3)  # Summarize to 30% of original length
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
            return 50  # Default to neutral score in case of error

    def flesch_reading_ease(self, text):
        sentences = sent_tokenize(text)
        words = word_tokenize(text)
        syllables = sum(self.count_syllables(word) for word in words)
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        score = 206.835 - 1.015 * (len(words) / len(sentences)) - 84.6 * (syllables / len(words))
        return max(min(score, 100), 0) / 100  # Normalize to 0-1 range

    def count_syllables(self, word):
        # This is a simple syllable counter and may not be 100% accurate
        vowels = 'aeiou'
        count = 0
        if word[0] in vowels:
            count += 1
        for index in range(1, len(word)):
            if word[index] in vowels and word[index - 1] not in vowels:
                count += 1
        if word.endswith('e'):
            count -= 1
        if count == 0:
            count += 1
        return count

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
    # Add more training data as needed
]
content_manager.train_classifier(sample_data)
