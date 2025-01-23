import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import accuracy_score, classification_report
import joblib
import logging
from typing import Dict, Any, List, Union
import json
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PredictiveAnalytics:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.feature_selector = None
        self.preprocessor = None

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the input data by handling missing values and encoding categorical variables.
        """
        logger.info("Starting data preprocessing")
        try:
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

            self.preprocessor = Pipeline(steps=[
                ('num', numeric_transformer),
                ('cat', categorical_transformer)
            ])

            preprocessed_data = pd.DataFrame(
                self.preprocessor.fit_transform(data),
                columns=numeric_features.tolist() + self.preprocessor.named_steps['cat'].get_feature_names(categorical_features).tolist()
            )

            logger.info("Data preprocessing completed successfully")
            return preprocessed_data
        except Exception as e:
            logger.error(f"Error during data preprocessing: {str(e)}")
            raise

    def select_features(self, X: pd.DataFrame, y: pd.Series, k: int = 10) -> pd.DataFrame:
        """
        Select the top k most important features.
        """
        logger.info(f"Selecting top {k} features")
        try:
            self.feature_selector = SelectKBest(f_classif, k=k)
            X_selected = self.feature_selector.fit_transform(X, y)
            selected_feature_indices = self.feature_selector.get_support(indices=True)
            selected_features = X.columns[selected_feature_indices]
            logger.info(f"Selected features: {', '.join(selected_features)}")
            return pd.DataFrame(X_selected, columns=selected_features)
        except Exception as e:
            logger.error(f"Error during feature selection: {str(e)}")
            raise

    def train_model(self, data: pd.DataFrame, target_column: str) -> None:
        """
        Train the predictive model using the provided data.
        """
        logger.info("Starting model training")
        try:
            if target_column not in data.columns:
                raise ValueError(f"Target column '{target_column}' not found in the data")

            X = data.drop(target_column, axis=1)
            y = data[target_column]

            X_selected = self.select_features(X, y)
            self.feature_columns = X_selected.columns

            X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42)

            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_train, y_train)

            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Model trained successfully. Accuracy: {accuracy:.2f}")
            logger.info("\nClassification Report:\n" + classification_report(y_test, y_pred))

            model_path = 'predictive_model.joblib'
            joblib.dump(self.model, model_path)
            logger.info(f"Model saved successfully to {model_path}")

            # Save feature columns and preprocessor
            feature_path = 'feature_columns.joblib'
            joblib.dump(self.feature_columns, feature_path)
            logger.info(f"Feature columns saved to {feature_path}")

            preprocessor_path = 'preprocessor.joblib'
            joblib.dump(self.preprocessor, preprocessor_path)
            logger.info(f"Preprocessor saved to {preprocessor_path}")

            feature_selector_path = 'feature_selector.joblib'
            joblib.dump(self.feature_selector, feature_selector_path)
            logger.info(f"Feature selector saved to {feature_selector_path}")

        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise

    def load_model(self) -> None:
        """
        Load the trained model and associated components.
        """
        try:
            model_path = 'predictive_model.joblib'
            feature_path = 'feature_columns.joblib'
            preprocessor_path = 'preprocessor.joblib'
            feature_selector_path = 'feature_selector.joblib'

            if not all(os.path.exists(path) for path in [model_path, feature_path, preprocessor_path, feature_selector_path]):
                raise FileNotFoundError("One or more model files are missing. Please train the model first.")

            self.model = joblib.load(model_path)
            self.feature_columns = joblib.load(feature_path)
            self.preprocessor = joblib.load(preprocessor_path)
            self.feature_selector = joblib.load(feature_selector_path)
            logger.info("Model and associated components loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def predict_health_issues(self, patient_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Predict potential health issues for a given patient.
        """
        try:
            if self.model is None:
                self.load_model()

            # Preprocess the patient data
            preprocessed_data = self.preprocessor.transform(patient_data)
            preprocessed_df = pd.DataFrame(preprocessed_data, columns=self.feature_columns)

            # Select features
            selected_features = self.feature_selector.transform(preprocessed_df)

            # Make predictions
            probabilities = self.model.predict_proba(selected_features)
            predicted_class = self.model.predict(selected_features)

            # Get feature importance
            feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
            top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]

            # Prepare the result
            result = {
                'predicted_class': int(predicted_class[0]),
                'probability': float(probabilities[0].max()),
                'top_factors': [{'factor': factor, 'importance': float(importance)} for factor, importance in top_factors],
                'used_features': self.feature_columns.tolist(),
                'missing_features': list(set(patient_data.columns) - set(self.feature_columns))
            }

            # Add a caveat if critical features are missing
            if result['missing_features']:
                result['caveat'] = "Some features were missing from the input data. The prediction may be less accurate."

            return result
        except Exception as e:
            logger.error(f"Error during health issue prediction: {str(e)}")
            raise

def get_health_predictions(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get health predictions for a specific patient.
    """
    try:
        patient_df = pd.DataFrame([patient_data])
        analytics = PredictiveAnalytics()
        predictions = analytics.predict_health_issues(patient_df)

        return {
            'patient_id': patient_data.get('patient_id'),
            'predictions': predictions
        }
    except Exception as e:
        logger.error(f"Error getting health predictions: {str(e)}")
        raise

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "train":
            try:
                # Load training data from a file (provided by the Express.js backend)
                training_data = pd.read_csv('training_data.csv')
                analytics = PredictiveAnalytics()
                preprocessed_data = analytics.preprocess_data(training_data)
                analytics.train_model(preprocessed_data, 'health_issue')
            except Exception as e:
                logger.error(f"Error during training: {str(e)}")
                sys.exit(1)
        elif command == "predict":
            try:
                # Read patient data from stdin (sent by Express.js)
                patient_data = json.loads(sys.stdin.read())
                result = get_health_predictions(patient_data)
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
