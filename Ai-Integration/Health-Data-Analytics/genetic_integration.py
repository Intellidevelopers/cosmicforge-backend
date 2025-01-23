import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif
import joblib
import logging
from typing import Dict, Any, List, Union
import json
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GeneticIntegration:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.imputer = None
        self.feature_selector = None
        self.feature_columns = None

    def preprocess_genetic_data(self, genetic_data: pd.DataFrame) -> np.ndarray:
        logger.info("Starting genetic data preprocessing")
        try:
            if self.imputer is None:
                self.imputer = SimpleImputer(strategy='median')
                imputed_data = self.imputer.fit_transform(genetic_data)
                joblib.dump(self.imputer, 'genetic_imputer.joblib')
            else:
                imputed_data = self.imputer.transform(genetic_data)

            if self.scaler is None:
                self.scaler = StandardScaler()
                processed_data = self.scaler.fit_transform(imputed_data)
                joblib.dump(self.scaler, 'genetic_scaler.joblib')
            else:
                processed_data = self.scaler.transform(imputed_data)

            logger.info("Genetic data preprocessing completed successfully")
            return processed_data
        except Exception as e:
            logger.error(f"Error during genetic data preprocessing: {str(e)}")
            raise

    def select_features(self, X: np.ndarray, y: np.ndarray, k: int = 50) -> np.ndarray:
        logger.info(f"Selecting top {k} genetic features")
        try:
            if self.feature_selector is None:
                self.feature_selector = SelectKBest(f_classif, k=k)
                X_selected = self.feature_selector.fit_transform(X, y)
                joblib.dump(self.feature_selector, 'genetic_feature_selector.joblib')
            else:
                X_selected = self.feature_selector.transform(X)

            self.feature_columns = self.feature_selector.get_support(indices=True)
            logger.info(f"Selected {len(self.feature_columns)} genetic features")
            return X_selected
        except Exception as e:
            logger.error(f"Error during genetic feature selection: {str(e)}")
            raise

    def train_genetic_model(self, genetic_data: pd.DataFrame, health_outcomes: np.ndarray) -> None:
        logger.info("Starting genetic model training")
        try:
            processed_data = self.preprocess_genetic_data(genetic_data)
            selected_data = self.select_features(processed_data, health_outcomes)

            X_train, X_test, y_train, y_test = train_test_split(selected_data, health_outcomes, test_size=0.2, random_state=42)

            self.model = Sequential([
                Dense(64, activation='relu', input_shape=(selected_data.shape[1],)),
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

            self.model.save('genetic_model.h5')
            logger.info("Genetic model saved successfully")

            # Save feature columns
            joblib.dump(self.feature_columns, 'genetic_feature_columns.joblib')
            logger.info("Genetic feature columns saved successfully")

        except Exception as e:
            logger.error(f"Error during genetic model training: {str(e)}")
            raise

    def load_model(self) -> None:
        try:
            model_path = 'genetic_model.h5'
            scaler_path = 'genetic_scaler.joblib'
            imputer_path = 'genetic_imputer.joblib'
            feature_selector_path = 'genetic_feature_selector.joblib'
            feature_columns_path = 'genetic_feature_columns.joblib'

            if not all(os.path.exists(path) for path in [model_path, scaler_path, imputer_path, feature_selector_path, feature_columns_path]):
                raise FileNotFoundError("One or more model files are missing. Please train the model first.")

            self.model = load_model(model_path)
            self.scaler = joblib.load(scaler_path)
            self.imputer = joblib.load(imputer_path)
            self.feature_selector = joblib.load(feature_selector_path)
            self.feature_columns = joblib.load(feature_columns_path)
            logger.info("Genetic model and associated components loaded successfully")
        except Exception as e:
            logger.error(f"Error loading genetic model: {str(e)}")
            raise

    def get_genetic_recommendations(self, genetic_data: pd.DataFrame) -> List[Dict[str, Any]]:
        try:
            if self.model is None:
                self.load_model()

            processed_data = self.preprocess_genetic_data(genetic_data)
            selected_data = self.feature_selector.transform(processed_data)

            predictions = self.model.predict(selected_data)

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
                    'genetic_marker': f'Marker_{self.feature_columns[i]}',
                    'risk_level': risk_level,
                    'probability': float(prob[0]),
                    'recommended_action': action
                })

            result = {
                'recommendations': recommendations,
                'used_features': self.feature_columns.tolist(),
                'missing_features': list(set(range(genetic_data.shape[1])) - set(self.feature_columns))
            }

            if result['missing_features']:
                result['caveat'] = "Some genetic markers were not used in the analysis. The recommendations may be less comprehensive."

            return result
        except Exception as e:
            logger.error(f"Error getting genetic recommendations: {str(e)}")
            raise

def get_personalized_recommendations(genetic_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        genetic_df = pd.DataFrame(genetic_data['genetic_markers'])
        integration = GeneticIntegration()
        recommendations = integration.get_genetic_recommendations(genetic_df)

        return {
            'patient_id': genetic_data.get('patient_id'),
            'genetic_recommendations': recommendations
        }
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "train":
            try:
                # Load training data from a file (assuming it's provided by the Express.js backend)
                genetic_data = pd.read_csv('genetic_training_data.csv')
                health_outcomes = pd.read_csv('health_outcomes.csv')['outcome'].values
                integration = GeneticIntegration()
                integration.train_genetic_model(genetic_data, health_outcomes)
            except Exception as e:
                logger.error(f"Error during training: {str(e)}")
                sys.exit(1)
        elif command == "predict":
            try:
                # Read genetic data from stdin (sent by Express.js)
                genetic_data = json.loads(sys.stdin.read())
                result = get_personalized_recommendations(genetic_data)
                print(json.dumps(result))
            except Exception as e:
                logger.error(f"Error during prediction: {str(e)}")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    else:
        print("Please provide a command: train or predict")
        sys.exit(1)
