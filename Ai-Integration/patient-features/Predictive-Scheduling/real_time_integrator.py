from config import Config
import logging
import schedule
import time
import threading

logger = logging.getLogger(__name__)

class RealTimeIntegrator:
    def __init__(self, data_collector, data_preprocessor, model_trainer):
        self.data_collector = data_collector
        self.data_preprocessor = data_preprocessor
        self.model_trainer = model_trainer
        self.setup_periodic_retraining()

    def update_model(self, appointment_data):
        try:
            # Save new appointment data
            self.data_collector.save_appointment_data(appointment_data)
            
            # Preprocess new data
            X_new, y_new = self.data_preprocessor.preprocess_data(appointment_data)
            
            # Update model
            self.model_trainer.update_model(X_new, y_new)
            
            return True
        except Exception as e:
            logger.error(f"Error in update_model: {str(e)}")
            return False

    def retrain_model(self):
        try:
            logger.info("Starting periodic model retraining")
            
            # Collect all historical data
            data = self.data_collector.get_historical_data()
            
            # Preprocess data
            X, y = self.data_preprocessor.preprocess_data(data)
            
            # Retrain model
            self.model_trainer.train_model(X, y)
            
            logger.info("Periodic model retraining completed")
        except Exception as e:
            logger.error(f"Error in retrain_model: {str(e)}")

    def setup_periodic_retraining(self):
        schedule.every().day.at("02:00").do(self.retrain_model)  # Retrain daily at 2 AM
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.start()
