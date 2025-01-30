import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, RobustScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.neural_network import MLPClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.decomposition import PCA
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import joblib
import shap
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
from io import BytesIO
import base64
import requests
from config import Config

# Ensure directories exist
for directory in [Config.MODEL_DIR, Config.DATA_DIR, Config.LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=10485760, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

class MedicalDiagnosisSystem:
    def __init__(self):
        self.models = {}
        self.feature_importances = {}
        self.diseases = [
            'chronic_kidney_disease', 'diabetes', 'heart_disease', 'liver_disease',
            'alzheimers_disease', 'parkinsons_disease', 'breast_cancer', 'lung_cancer',
            'stroke', 'thyroid_disease', 'skin_cancer', 'colorectal_cancer'
        ]
        self.data_paths = {disease: os.path.join(Config.DATA_DIR, f"{disease}.csv") for disease in self.diseases}
        self.load_models()

    def load_models(self):
        for disease in self.diseases:
            model_path = os.path.join(Config.MODEL_DIR, f"{disease}_model_{Config.MODEL_VERSION}.joblib")
            if os.path.exists(model_path):
                self.models[disease] = joblib.load(model_path)
                logger.info(f"Loaded model for {disease}")
            else:
                logger.warning(f"Model for {disease} not found. It will be trained when needed.")

    def save_model(self, disease, model):
        model_path = os.path.join(Config.MODEL_DIR, f"{disease}_model_{Config.MODEL_VERSION}.joblib")
        joblib.dump(model, model_path)
        logger.info(f"Saved model for {disease}")

    def load_data(self, disease):
        try:
            df = pd.read_csv(self.data_paths[disease])
            logger.info(f"Data for {disease} loaded successfully")
            return df
        except Exception as e:
            logger.error(f"Error loading data for {disease}: {str(e)}")
            raise

    def preprocess_data(self, df, target_col, num_features, cat_features):
        X = df.drop(columns=[target_col])
        y = df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        num_transformer = Pipeline([
            ('imputer', KNNImputer(n_neighbors=5)),
            ('scaler', RobustScaler())
        ])

        cat_transformer = Pipeline([
            ('imputer', KNNImputer(n_neighbors=5)),
            ('encoder', OneHotEncoder(handle_unknown='ignore', sparse=False))
        ])

        preprocessor = ColumnTransformer([
            ('num', num_transformer, num_features),
            ('cat', cat_transformer, cat_features)
        ])

        feature_selector = SelectKBest(f_classif, k='all')
        pca = PCA(n_components=0.95)
        smote = SMOTE(random_state=42)

        return X_train, X_test, y_train, y_test, preprocessor, feature_selector, pca, smote

    def train_and_evaluate(self, X_train, X_test, y_train, y_test, preprocessor, feature_selector, pca, smote):
        base_models = [
            ('lr', LogisticRegression(max_iter=5000)),
            ('rf', RandomForestClassifier()),
            ('gb', GradientBoostingClassifier()),
            ('svm', SVC(probability=True)),
            ('mlp', MLPClassifier(max_iter=1000)),
            ('xgb', XGBClassifier()),
            ('lgbm', LGBMClassifier())
        ]

        ensemble = VotingClassifier(estimators=base_models, voting='soft')

        pipeline = ImbPipeline([
            ('preprocessor', preprocessor),
            ('feature_selector', feature_selector),
            ('pca', pca),
            ('smote', smote),
            ('classifier', ensemble)
        ])

        param_grid = {
            'classifier__lr__C': [0.1, 1, 10],
            'classifier__rf__n_estimators': [100, 200, 300],
            'classifier__gb__n_estimators': [100, 200, 300],
            'classifier__svm__C': [0.1, 1, 10],
            'classifier__mlp__hidden_layer_sizes': [(50,50), (100,100), (50,50,50)],
            'classifier__xgb__n_estimators': [100, 200, 300],
            'classifier__lgbm__n_estimators': [100, 200, 300]
        }

        grid_search = GridSearchCV(pipeline, param_grid, cv=5, n_jobs=-1, verbose=1, scoring='roc_auc')
        grid_search.fit(X_train, y_train)

        best_model = grid_search.best_estimator_
        y_pred = best_model.predict(X_test)
        y_pred_proba = best_model.predict_proba(X_test)

        logger.info(f"Best Model Parameters: {grid_search.best_params_}")
        logger.info(f"Accuracy Score: {accuracy_score(y_test, y_pred)}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        logger.info(f"Confusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
        logger.info(f"ROC AUC Score: {roc_auc_score(y_test, y_pred_proba, multi_class='ovr')}")

        feature_importance = best_model.named_steps['classifier'].estimators_[1].feature_importances_
        feature_names = (best_model.named_steps['preprocessor']
                         .named_transformers_['num'].get_feature_names_out().tolist() +
                         best_model.named_steps['preprocessor']
                         .named_transformers_['cat'].get_feature_names_out().tolist())
        
        feature_importance_df = pd.DataFrame({'feature': feature_names, 'importance': feature_importance})
        feature_importance_df = feature_importance_df.sort_values('importance', ascending=False)

        return best_model, feature_importance_df

    def train_all_models(self):
        for disease in self.diseases:
            logger.info(f"Training model for {disease}")
            df = self.load_data(disease)
            
            if disease == 'chronic_kidney_disease':
                target_col = 'classification'
                num_features = ['age', 'bp', 'sg', 'al', 'su', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
                cat_features = ['rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']
            elif disease == 'diabetes':
                target_col = 'Outcome'
                num_features = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
                cat_features = []
            elif disease == 'heart_disease':
                target_col = 'target'
                num_features = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca']
                cat_features = ['thal']
            elif disease == 'liver_disease':
                target_col = 'Dataset'
                num_features = ['Age', 'Total_Bilirubin', 'Direct_Bilirubin', 'Alkaline_Phosphotase', 'Alamine_Aminotransferase', 'Aspartate_Aminotransferase', 'Total_Protiens', 'Albumin', 'Albumin_and_Globulin_Ratio']
                cat_features = ['Gender']
            elif disease == 'alzheimers_disease':
                target_col = 'Group'
                num_features = ['Age', 'EDUC', 'SES', 'MMSE', 'CDR', 'eTIV', 'nWBV', 'ASF']
                cat_features = ['M/F']
            elif disease == 'parkinsons_disease':
                target_col = 'status'
                num_features = ['MDVP:Fo(Hz)', 'MDVP:Fhi(Hz)', 'MDVP:Flo(Hz)', 'MDVP:Jitter(%)', 'MDVP:Jitter(Abs)', 'MDVP:RAP', 'MDVP:PPQ', 'Jitter:DDP', 'MDVP:Shimmer', 'MDVP:Shimmer(dB)', 'Shimmer:APQ3', 'Shimmer:APQ5', 'MDVP:APQ', 'Shimmer:DDA', 'NHR', 'HNR', 'RPDE', 'DFA', 'spread1', 'spread2', 'D2', 'PPE']
                cat_features = []
            elif disease == 'breast_cancer':
                target_col = 'diagnosis'
                num_features = ['radius_mean', 'texture_mean', 'perimeter_mean', 'area_mean', 'smoothness_mean', 'compactness_mean', 'concavity_mean', 'concave points_mean', 'symmetry_mean', 'fractal_dimension_mean']
                cat_features = []
            elif disease == 'lung_cancer':
                target_col = 'LUNG_CANCER'
                num_features = ['AGE', 'SMOKING', 'YELLOW_FINGERS', 'ANXIETY', 'PEER_PRESSURE', 'CHRONIC DISEASE', 'FATIGUE ', 'ALLERGY ', 'WHEEZING', 'ALCOHOL CONSUMING', 'COUGHING', 'SHORTNESS OF BREATH', 'SWALLOWING DIFFICULTY', 'CHEST PAIN']
                cat_features = ['GENDER']
            elif disease == 'stroke':
                target_col = 'stroke'
                num_features = ['age', 'avg_glucose_level', 'bmi']
                cat_features = ['gender', 'hypertension', 'heart_disease', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
            elif disease == 'thyroid_disease':
                target_col = 'binaryClass'
                num_features = ['age', 'TSH', 'T3', 'TT4', 'T4U', 'FTI']
                cat_features = ['sex', 'on_thyroxine', 'query_on_thyroxine', 'on_antithyroid_medication', 'sick', 'pregnant', 'thyroid_surgery', 'I131_treatment', 'query_hypothyroid', 'query_hyperthyroid', 'lithium', 'goitre', 'tumor', 'hypopituitary', 'psych']
            elif disease == 'skin_cancer':
                target_col = 'class'
                num_features = ['age']
                cat_features = ['sex', 'site', 'ulceration']
            elif disease == 'colorectal_cancer':
                target_col = 'diagnosis'
                num_features = ['age', 'bmi', 'glucose', 'insulin', 'homa', 'leptin', 'adiponectin', 'resistin', 'mcp.1']
                cat_features = []
            else:
                logger.error(f"Unknown disease: {disease}")
                continue

            X_train, X_test, y_train, y_test, preprocessor, feature_selector, pca, smote = self.preprocess_data(
                df, target_col, num_features, cat_features)

            best_model, feature_importance = self.train_and_evaluate(
                X_train, X_test, y_train, y_test, preprocessor, feature_selector, pca, smote)

            self.models[disease] = best_model
            self.feature_importances[disease] = feature_importance

            self.save_model(disease, best_model)
            logger.info(f"Model for {disease} trained and saved successfully")

    def generate_shap_plot(self, disease, X):
        model = self.models[disease]
        explainer = shap.TreeExplainer(model.named_steps['classifier'].estimators_[1])
        shap_values = explainer.shap_values(model.named_steps['preprocessor'].transform(X))
        
        plt.figure(figsize=(10, 6))
        shap.summary_plot(shap_values, model.named_steps['preprocessor'].transform(X), 
                          feature_names=self.feature_importances[disease]['feature'].tolist(),
                          plot_type="bar", show=False)
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        data = base64.b64encode(buf.getbuffer()).decode("ascii")
        return f"data:image/png;base64,{data}"

    def get_deepseek_explanation(self, disease, prediction, probability):
        prompt = f"Generate a detailed medical explanation for a {disease} diagnosis. The model predicts {'positive' if prediction else 'negative'} with {probability:.2f} probability. Include potential causes, risk factors, and the significance of this result."
        
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-ai/deepseek-coder-33b-instruct",
            "prompt": prompt,
            "max_tokens": 500
        }
        response = requests.post("https://api.deepseek.com/v1/completions", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['text'].strip()
        else:
            logger.error(f"Error from DeepSeek API: {response.text}")
            return "Unable to generate explanation at this time."

    def get_deepseek_recommendations(self, disease, prediction):
        prompt = f"Provide detailed medical recommendations for a patient diagnosed with {disease}. The diagnosis is {'positive' if prediction else 'negative'}. Include lifestyle changes, potential treatments, and follow-up steps."
        
        headers = {
            "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-ai/deepseek-coder-33b-instruct",
            "prompt": prompt,
            "max_tokens": 500
        }
        response = requests.post("https://api.deepseek.com/v1/completions", json=data, headers=headers)
        
        if response.status_code == 200:
            return response.json()['choices'][0]['text'].strip().split("\n")
        else:
            logger.error(f"Error from DeepSeek API: {response.text}")
            return ["Unable to generate recommendations at this time."]

    def diagnose(self, disease, data):
        try:
            if disease not in self.models:
                logger.info(f"Model for {disease} not loaded. Training now.")
                self.train_all_models()  # This will train and save all models

            model = self.models[disease]
            X = pd.DataFrame([data])
            
            prediction = model.predict(X)[0]
            probability = model.predict_proba(X)[0][1]
            
            shap_plot = self.generate_shap_plot(disease, X)
            explanation = self.get_deepseek_explanation(disease, prediction, probability)
            recommendations = self.get_deepseek_recommendations(disease, prediction)
            
            result = {
                'disease': disease,
                'prediction': int(prediction),
                'probability': float(probability),
                'explanation': explanation,
                'recommendations': recommendations,
                'shap_plot': shap_plot
            }
            
            logger.info(f"{disease.capitalize()} diagnosis: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {disease} diagnosis: {str(e)}", exc_info=True)
            return {'error': str(e)}

# Flask application
app = Flask(__name__)
CORS(app)

diagnosis_system = MedicalDiagnosisSystem()

@app.route("/api/diagnose/<disease>", methods=['POST'])
def diagnose(disease):
    data = request.json
    result = diagnosis_system.diagnose(disease, data)
    return jsonify(result)

@app.route("/api/train", methods=['POST'])
def train_models():
    diagnosis_system.train_all_models()
    return jsonify({"message": "All models trained successfully"})

if __name__ == "__main__":
    app.run(debug=False, port=8000)
