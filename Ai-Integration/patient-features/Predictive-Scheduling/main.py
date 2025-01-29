from flask import Flask, request, jsonify
from data_collector import DataCollector
from data_preprocessor import DataPreprocessor
from model_trainer import ModelTrainer
from optimizer import Optimizer
from real_time_integrator import RealTimeIntegrator
from config import Config
import logging
from utils import setup_logger

app = Flask(__name__)
setup_logger()
logger = logging.getLogger(__name__)

data_collector = DataCollector()
data_preprocessor = DataPreprocessor()
model_trainer = ModelTrainer()
optimizer = Optimizer()
real_time_integrator = RealTimeIntegrator(data_collector, data_preprocessor, model_trainer)

@app.route('/predict_appointments', methods=['POST'])
def predict_appointments():
    try:
        data = request.json
        patient_id = data['patient_id']
        appointment_type = data['appointment_type']
        preferred_dates = data['preferred_dates']
        
        patient_data = data_collector.get_patient_data(patient_id)
        provider_availability = data_collector.get_provider_availability(appointment_type, preferred_dates)
        
        features = data_preprocessor.create_features(patient_data, appointment_type, preferred_dates)
        probabilities = model_trainer.predict_probabilities(features)
        
        suggestions = optimizer.optimize_appointments(probabilities, provider_availability, preferred_dates)
        
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error in predict_appointments: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route('/update_model', methods=['POST'])
def update_model():
    try:
        data = request.json
        appointment_data = data['appointment_data']
        
        success = real_time_integrator.update_model(appointment_data)
        return jsonify({'success': success})
    except Exception as e:
        logger.error(f"Error in update_model: {str(e)}")
        return jsonify({"error": "An error occurred while updating the model"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT)
