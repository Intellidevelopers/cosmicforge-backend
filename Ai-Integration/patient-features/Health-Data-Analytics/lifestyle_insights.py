import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_regression
from scipy.stats import pearsonr
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
from typing import Dict, Any, List, Union
import json
import sys
import os
import joblib

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LifestyleInsights:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.kmeans = KMeans(n_clusters=5, random_state=42)
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.feature_selector = SelectKBest(f_regression, k=10)
        self.selected_features = None

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        logger.info("Starting data preprocessing")
        try:
            imputed_data = self.imputer.fit_transform(data)
            scaled_data = self.scaler.fit_transform(imputed_data)
            return pd.DataFrame(scaled_data, columns=data.columns)
        except Exception as e:
            logger.error(f"Error during data preprocessing: {str(e)}")
            raise

    def select_features(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        logger.info("Selecting top features")
        try:
            X_selected = self.feature_selector.fit_transform(X, y)
            self.selected_features = X.columns[self.feature_selector.get_support()].tolist()
            logger.info(f"Selected features: {', '.join(self.selected_features)}")
            return pd.DataFrame(X_selected, columns=self.selected_features)
        except Exception as e:
            logger.error(f"Error during feature selection: {str(e)}")
            raise

    def analyze_medication_adherence(self, prescription_data: pd.DataFrame, patient_reports: List[str]) -> float:
        try:
            total_doses = prescription_data['daily_doses'].sum() * (prescription_data['end_date'] - prescription_data['start_date']).dt.days.sum()
            reported_doses = sum(report.lower().count('took') for report in patient_reports)
            adherence_score = reported_doses / total_doses if total_doses > 0 else 0
            return min(adherence_score, 1.0)  # Cap adherence score at 1.0
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
            preprocessed_data = self.preprocess_data(lifestyle_data)
            selected_data = self.select_features(preprocessed_data, medication_effectiveness)

            correlations = []
            for factor in selected_data.columns:
                correlation, p_value = pearsonr(selected_data[factor], medication_effectiveness)
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

    def save_model(self) -> None:
        joblib.dump(self.vectorizer, 'vectorizer.joblib')
        joblib.dump(self.kmeans, 'kmeans.joblib')
        joblib.dump(self.scaler, 'scaler.joblib')
        joblib.dump(self.imputer, 'imputer.joblib')
        joblib.dump(self.feature_selector, 'feature_selector.joblib')
        logger.info("Model components saved successfully")

    def load_model(self) -> None:
        try:
            self.vectorizer = joblib.load('vectorizer.joblib')
            self.kmeans = joblib.load('kmeans.joblib')
            self.scaler = joblib.load('scaler.joblib')
            self.imputer = joblib.load('imputer.joblib')
            self.feature_selector = joblib.load('feature_selector.joblib')
            logger.info("Model components loaded successfully")
        except FileNotFoundError:
            logger.warning("Model files not found. Using new model components.")

def get_lifestyle_insights(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prescription_data = pd.DataFrame(patient_data['prescription_data'])
        patient_reports = patient_data['patient_reports']
        lifestyle_data = pd.DataFrame(patient_data['lifestyle_data'])
        medication_effectiveness = pd.Series(patient_data['medication_effectiveness'])

        insights = LifestyleInsights()
        insights.load_model()  # Try to load existing model components

        adherence_score = insights.analyze_medication_adherence(prescription_data, patient_reports)
        symptom_insights = insights.extract_symptom_insights(patient_reports)
        lifestyle_impact = insights.analyze_lifestyle_impact(lifestyle_data, medication_effectiveness)

        insights.save_model()  # Save updated model components

        result = {
            'patient_id': patient_data['patient_id'],
            'adherence_score': float(adherence_score),
            'symptom_insights': symptom_insights,
            'lifestyle_impact': lifestyle_impact,
            'used_features': insights.selected_features,
            'missing_features': list(set(lifestyle_data.columns) - set(insights.selected_features))
        }

        if result['missing_features']:
            result['caveat'] = "Some lifestyle factors were not used in the analysis. The insights may be less comprehensive."

        return result
    except Exception as e:
        logger.error(f"Error getting lifestyle insights: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "analyze":
            try:
                # Read patient data from stdin (sent by Express.js)
                patient_data = json.loads(sys.stdin.read())
                result = get_lifestyle_insights(patient_data)
                print(json.dumps(result))
            except Exception as e:
                logger.error(f"Error during analysis: {str(e)}")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        print("Please provide a command: analyze")
        sys.exit(1)
