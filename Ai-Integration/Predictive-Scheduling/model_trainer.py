from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from config import Config
import joblib
import logging

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self):
        self.model = None

    def train_model(self, X, y):
        try:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=Config.TEST_SIZE, random_state=Config.RANDOM_STATE)
            
            # Hyperparameter tuning
            param_grid = {
                'n_estimators': [100, 200, 300],
                'max_depth': [10, 20, 30, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            grid_search = GridSearchCV(RandomForestClassifier(random_state=Config.RANDOM_STATE), 
                                       param_grid, cv=5, n_jobs=-1, verbose=1)
            grid_search.fit(X_train, y_train)
            
            self.model = grid_search.best_estimator_
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred)
            recall = recall_score(y_test, y_pred)
            f1 = f1_score(y_test, y_pred)
            
            logger.info(f"Model performance: Accuracy={accuracy:.4f}, Precision={precision:.4f}, Recall={recall:.4f}, F1={f1:.4f}")
            
            # Save model
            joblib.dump(self.model, Config.MODEL_PATH)
            logger.info(f"Model saved to {Config.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Error in train_model: {str(e)}")
            raise

    def predict_probabilities(self, X):
        try:
            if self.model is None:
                self.model = joblib.load(Config.MODEL_PATH)
            return self.model.predict_proba(X)[:, 1]
        except Exception as e:
            logger.error(f"Error in predict_probabilities: {str(e)}")
            raise

    def update_model(self, X_new, y_new):
        try:
            if self.model is None:
                self.model = joblib.load(Config.MODEL_PATH)
            self.model.fit(X_new, y_new)
            joblib.dump(self.model, Config.MODEL_PATH)
            logger.info("Model updated and saved successfully")
        except Exception as e:
            logger.error(f"Error in update_model: {str(e)}")
            raise
