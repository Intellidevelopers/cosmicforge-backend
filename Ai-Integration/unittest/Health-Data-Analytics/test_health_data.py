import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, classification_report
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from scipy.stats import pearsonr
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
from typing import Dict, Any, List

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    def __init__(self):
        self.model = None
        self.feature_columns = None

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        numeric_features = data.select_dtypes(include=[np.number]).columns
        categorical_features = data.select_dtypes(include=['object']).columns

        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', pd.get_dummies)
        ])

        data[numeric_features] = numeric_transformer.fit_transform(data[numeric_features])
        data = pd.get_dummies(data, columns=categorical_features)

        return data

    def train_model(self, data: pd.DataFrame, target_column: str) -> None:
        logger.info("Starting model training")
        try:
            X = data.drop(target_column, axis=1)
            y = data[target_column]

            self.feature_columns = X.columns

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Model trained successfully. Accuracy: {accuracy:.2f}")
            logger.info("\nClassification Report:\n" + classification_report(y_test, y_pred))
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise

    def predict_health_issues(self, patient_data: pd.DataFrame) -> Dict[str, Any]:
        try:
            patient_data = patient_data.reindex(columns=self.feature_columns, fill_value=0)
            probabilities = self.model.predict_proba(patient_data)
            predicted_class = self.model.predict(patient_data)
            feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                'predicted_class': predicted_class[0],
                'probability': probabilities[0].max(),
                'top_factors': top_factors
            }
        except Exception as e:
            logger.error(f"Error during health issue prediction: {str(e)}")
            raise

class GeneticIntegration:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def process_genetic_data(self, genetic_data: pd.DataFrame) -> np.ndarray:
        return self.scaler.fit_transform(genetic_data)

    def train_genetic_model(self, genetic_data: pd.DataFrame, health_outcomes: np.ndarray) -> None:
        logger.info("Starting genetic model training")
        try:
            processed_data = self.process_genetic_data(genetic_data)
            X_train, X_test, y_train, y_test = train_test_split(processed_data, health_outcomes, test_size=0.2, random_state=42)

            self.model = Sequential([
                Dense(64, activation='relu', input_shape=(genetic_data.shape[1],)),
                Dropout(0.2),
                Dense(32, activation='relu'),
                Dropout(0.2),
                Dense(16, activation='relu'),
                Dense(1, activation='sigmoid')
            ])

            self.model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
            history = self.model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=32, verbose=0)

            loss, accuracy = self.model.evaluate(X_test, y_test, verbose=0)
            logger.info(f"Genetic model trained successfully. Test accuracy: {accuracy:.2f}")
        except Exception as e:
            logger.error(f"Error during genetic model training: {str(e)}")
            raise

    def get_genetic_recommendations(self, genetic_data: pd.DataFrame) -> List[Dict[str, Any]]:
        try:
            processed_data = self.process_genetic_data(genetic_data)
            predictions = self.model.predict(processed_data)

            thresholds = {
                'high_risk': 0.7,
                'moderate_risk': 0.4,
                'low_risk': 0.1
            }

            recommendations = []
            for i, prob in enumerate(predictions):
                if prob > thresholds['high_risk']:
                    risk_level = 'High'
                    action = 'Immediate consultation with a specialist is recommended.'
                elif prob > thresholds['moderate_risk']:
                    risk_level = 'Moderate'
                    action = 'Regular check-ups and lifestyle modifications are advised.'
                elif prob > thresholds['low_risk']:
                    risk_level = 'Low'
                    action = 'Maintain a healthy lifestyle and follow general health guidelines.'
                else:
                    risk_level = 'Very Low'
                    action = 'Continue with routine health maintenance.'

                recommendations.append({
                    'genetic_marker': f'Marker_{i+1}',
                    'risk_level': risk_level,
                    'probability': float(prob),
                    'recommended_action': action
                })

            return recommendations
        except Exception as e:
            logger.error(f"Error getting genetic recommendations: {str(e)}")
            raise

class LifestyleInsights:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()

    def analyze_medication_adherence(self, prescription_data: pd.DataFrame, patient_reports: List[str]) -> float:
        try:
            total_doses = prescription_data['daily_doses'].sum() * (prescription_data['end_date'] - prescription_data['start_date']).dt.days.sum()
            reported_doses = sum(report.lower().count('took') for report in patient_reports)
            adherence_score = reported_doses / total_doses
            return min(adherence_score, 1.0)
        except Exception as e:
            logger.error(f"Error analyzing medication adherence: {str(e)}")
            raise

    def extract_symptom_insights(self, patient_reports: List[str]) -> List[Dict[str, Any]]:
        try:
            processed_reports = [self.preprocess_text(report) for report in patient_reports]
            tfidf_matrix = self.vectorizer.fit_transform(processed_reports)
            self.kmeans.fit(tfidf_matrix)
            cluster_centers = self.kmeans.cluster_centers_
            terms = self.vectorizer.get_feature_names()

            insights = []
            for i, center in enumerate(cluster_centers):
                top_terms = [terms[j] for j in center.argsort()[-10:]]
                insights.append({
                    'cluster': i,
                    'top_terms': top_terms,
                    'interpretation': self.interpret_cluster(top_terms)
                })

            return insights
        except Exception as e:
            logger.error(f"Error extracting symptom insights: {str(e)}")
            raise

    def preprocess_text(self, text: str) -> str:
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [token for token in tokens if token not in stop_words and token.isalnum()]
        return ' '.join(filtered_tokens)

    def interpret_cluster(self, top_terms: List[str]) -> str:
        if any(term in ['pain', 'ache', 'sore'] for term in top_terms):
            return "This cluster seems to be related to pain or discomfort."
        elif any(term in ['tired', 'fatigue', 'exhausted'] for term in top_terms):
            return "This cluster appears to be associated with fatigue or low energy."
        elif any(term in ['anxious', 'worried', 'stress'] for term in top_terms):
            return "This cluster might be indicating anxiety or stress-related symptoms."
        else:
            return "This cluster represents a group of related symptoms or experiences."

    def analyze_lifestyle_impact(self, lifestyle_data: pd.DataFrame, medication_effectiveness: pd.Series) -> List[Dict[str, Any]]:
        try:
            normalized_lifestyle_data = self.scaler.fit_transform(lifestyle_data)
            correlations = []
            for i, factor in enumerate(lifestyle_data.columns):
                correlation, p_value = pearsonr(normalized_lifestyle_data[:, i], medication_effectiveness)
                correlations.append({
                    'factor': factor,
                    'correlation': correlation,
                    'p_value': p_value,
                    'interpretation': self.interpret_correlation(correlation, p_value)
                })

            return sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)
        except Exception as e:
            logger.error(f"Error analyzing lifestyle impact: {str(e)}")
            raise

    def interpret_correlation(self, correlation: float, p_value: float) -> str:
        if p_value > 0.05:
            return "No significant relationship found."
        elif abs(correlation) > 0.7:
            direction = "positive" if correlation > 0 else "negative"
            return f"Strong {direction} relationship with medication effectiveness."
        elif abs(correlation) > 0.3:
            direction = "positive" if correlation > 0 else "negative"
            return f"Moderate {direction} relationship with medication effectiveness."
        else:
            direction = "positive" if correlation > 0 else "negative"
            return f"Weak {direction} relationship with medication effectiveness."

def run_comprehensive_health_analysis(patient_id: int):
    logger.info(f"Starting comprehensive health analysis for patient {patient_id}")

    # Predictive Analytics
    logger.info("Running Predictive Analytics")
    predictive_analytics = PredictiveAnalytics()
    
    # Generate sample data for training
    np.random.seed(42)
    n_samples = 1000
    data = pd.DataFrame({
        'age': np.random.randint(18, 80, n_samples),
        'bmi': np.random.uniform(18.5, 35, n_samples),
        'blood_pressure': np.random.randint(90, 180, n_samples),
        'cholesterol': np.random.randint(120, 300, n_samples),
        'glucose': np.random.randint(70, 150, n_samples),
        'smoking': np.random.choice([0, 1], n_samples),
        'alcohol_consumption': np.random.randint(0, 7, n_samples),
        'physical_activity': np.random.randint(0, 7, n_samples),
        'family_history': np.random.choice([0, 1], n_samples),
        'health_issue': np.random.choice([0, 1], n_samples)
    })

    preprocessed_data = predictive_analytics.preprocess_data(data)
    predictive_analytics.train_model(preprocessed_data, 'health_issue')

    patient_data = pd.DataFrame({
        'age': [35],
        'bmi': [22.5],
        'blood_pressure': [120],
        'cholesterol': [180],
        'glucose': [85],
        'smoking': [0],
        'alcohol_consumption': [2],
        'physical_activity': [3],
        'family_history': [1]
    })
    health_predictions = predictive_analytics.predict_health_issues(patient_data)
    logger.info(f"Predictive Analytics Results: {health_predictions}")

    # Genetic Data Integration
    logger.info("Running Genetic Data Integration")
    genetic_integration = GeneticIntegration()
    
    # Generate sample genetic data
    n_genetic_samples = 1000
    n_genetic_features = 100
    genetic_data = pd.DataFrame(np.random.rand(n_genetic_samples, n_genetic_features))
    health_outcomes = np.random.randint(0, 2, n_genetic_samples)

    genetic_integration.train_genetic_model(genetic_data, health_outcomes)
    
    patient_genetic_data = pd.DataFrame(np.random.rand(1, n_genetic_features))
    genetic_recommendations = genetic_integration.get_genetic_recommendations(patient_genetic_data)
    logger.info(f"Genetic Data Integration Results: {genetic_recommendations}")

    # Lifestyle Insights
    logger.info("Running Lifestyle Insights")
    lifestyle_insights = LifestyleInsights()
    
    prescription_data = pd.DataFrame({
        'medication': ['Med A', 'Med B'],
        'daily_doses': [2, 1],
        'start_date': pd.to_datetime(['2023-01-01', '2023-02-01']),
        'end_date': pd.to_datetime(['2023-03-01', '2023-04-01'])
    })

    patient_reports = [
        "Took medication as prescribed. Feeling better.",
        "Missed a dose yesterday. Experiencing some pain.",
        "Took all doses. Noticing improvement in symptoms."
    ]

    lifestyle_data = pd.DataFrame({
        'sleep_hours': [7, 6, 8, 7, 6],
        'exercise_minutes': [30, 0, 45, 60, 30],
        'stress_level': [3, 5, 2, 4, 3],
        'diet_quality': [4, 3, 5, 4, 3]
    })

    medication_effectiveness = pd.Series([0.8, 0.6, 0.9, 0.7, 0.75])

    adherence_score = lifestyle_insights.analyze_medication_adherence(prescription_data, patient_reports)
    symptom_insights = lifestyle_insights.extract_symptom_insights(patient_reports)
    lifestyle_impact = lifestyle_insights.analyze_lifestyle_impact(lifestyle_data, medication_effectiveness)

    logger.info(f"Lifestyle Insights Results:")
    logger.info(f"Adherence Score: {adherence_score}")
    logger.info(f"Symptom Insights: {symptom_insights}")
    logger.info(f"Lifestyle Impact: {lifestyle_impact}")

    logger.info(f"Comprehensive health analysis completed for patient {patient_id}")

if __name__ == "__main__":
    run_comprehensive_health_analysis(1)
