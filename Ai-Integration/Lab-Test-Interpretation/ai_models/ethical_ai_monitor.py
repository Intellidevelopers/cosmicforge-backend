
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

# Database setup
DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class FairnessAudit(Base):
    __tablename__ = 'fairness_audits'
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    timestamp = Column(DateTime)
    is_fair = Column(Integer)
    fairness_metrics = Column(JSON)

Base.metadata.create_all(engine)

logging.basicConfig(filename='ethical_ai.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class EthicalAIMonitor:
    def __init__(self):
        self.protected_attributes = ['gender', 'race', 'age_group']
        self.fairness_threshold = 0.8

    def calculate_fairness_metrics(self, predictions: np.ndarray, true_labels: np.ndarray, protected_attributes: Dict[str, np.ndarray]) -> Dict[str, Dict[str, float]]:
        fairness_metrics = {}
        for attr in self.protected_attributes:
            if attr in protected_attributes:
                fairness_metrics[attr] = {
                    'demographic_parity': self.calculate_demographic_parity(predictions, protected_attributes[attr]),
                    'equal_opportunity': self.calculate_equal_opportunity(predictions, true_labels, protected_attributes[attr]),
                    'predictive_parity': self.calculate_predictive_parity(predictions, true_labels, protected_attributes[attr])
                }
        return fairness_metrics

    def calculate_demographic_parity(self, predictions: np.ndarray, protected_attribute: np.ndarray) -> float:
        groups = np.unique(protected_attribute)
        group_predictions = {group: predictions[protected_attribute == group] for group in groups}
        positive_rates = {group: np.mean(preds) for group, preds in group_predictions.items()}
        
        min_rate = min(positive_rates.values())
        max_rate = max(positive_rates.values())
        
        return min_rate / max_rate if max_rate > 0 else 1.0

    def calculate_equal_opportunity(self, predictions: np.ndarray, true_labels: np.ndarray, protected_attribute: np.ndarray) -> float:
        groups = np.unique(protected_attribute)
        true_positive_rates = {}
        for group in groups:
            group_mask = protected_attribute == group
            true_positives = np.logical_and(predictions[group_mask] == 1, true_labels[group_mask] == 1)
            positives = true_labels[group_mask] == 1
            true_positive_rates[group] = np.sum(true_positives) / np.sum(positives) if np.sum(positives) > 0 else 0
        
        min_rate = min(true_positive_rates.values())
        max_rate = max(true_positive_rates.values())
        
        return min_rate / max_rate if max_rate > 0 else 1.0

    def calculate_predictive_parity(self, predictions: np.ndarray, true_labels: np.ndarray, protected_attribute: np.ndarray) -> float:
        groups = np.unique(protected_attribute)
        precision_scores = {}
        for group in groups:
            group_mask = protected_attribute == group
            true_positives = np.logical_and(predictions[group_mask] == 1, true_labels[group_mask] == 1)
            predicted_positives = predictions[group_mask] == 1
            precision_scores[group] = np.sum(true_positives) / np.sum(predicted_positives) if np.sum(predicted_positives) > 0 else 0
        
        min_score = min(precision_scores.values())
        max_score = max(precision_scores.values())
        
        return min_score / max_score if max_score > 0 else 1.0

    def check_fairness(self, fairness_metrics: Dict[str, Dict[str, float]]) -> bool:
        for attr_metrics in fairness_metrics.values():
            if any(metric < self.fairness_threshold for metric in attr_metrics.values()):
                return False
        return True

    def generate_confusion_matrices(self, predictions: np.ndarray, true_labels: np.ndarray, protected_attributes: Dict[str, np.ndarray]) -> Dict[str, Dict[str, np.ndarray]]:
        confusion_matrices = {}
        for attr in self.protected_attributes:
            if attr in protected_attributes:
                groups = np.unique(protected_attributes[attr])
                confusion_matrices[attr] = {
                    group: confusion_matrix(true_labels[protected_attributes[attr] == group],
                                            predictions[protected_attributes[attr] == group])
                    for group in groups
                }
        return confusion_matrices

    def plot_confusion_matrices(self, confusion_matrices: Dict[str, Dict[str, np.ndarray]]):
        for attr, matrices in confusion_matrices.items():
            fig, axes = plt.subplots(1, len(matrices), figsize=(5*len(matrices), 5))
            for i, (group, cm) in enumerate(matrices.items()):
                ax = axes[i] if len(matrices) > 1 else axes
                sns.heatmap(cm, annot=True, fmt='d', ax=ax, cmap='Blues')
                ax.set_title(f'{attr.capitalize()} - {group}')
                ax.set_xlabel('Predicted')
                ax.set_ylabel('True')
            plt.tight_layout()
            plt.savefig(f'static/confusion_matrix_{attr}.png')
            plt.close()

    def generate_classification_report(self, predictions: np.ndarray, true_labels: np.ndarray, protected_attributes: Dict[str, np.ndarray]) -> Dict[str, Dict[str, Dict[str, float]]]:
        reports = {}
        for attr in self.protected_attributes:
            if attr in protected_attributes:
                groups = np.unique(protected_attributes[attr])
                reports[attr] = {
                    group: classification_report(true_labels[protected_attributes[attr] == group],
                                                 predictions[protected_attributes[attr] == group],
                                                 output_dict=True)
                    for group in groups
                }
        return reports

    def log_fairness_issue(self, patient_id: str, fairness_metrics: Dict[str, Dict[str, float]]):
        logging.warning(f"Fairness issue detected for patient {patient_id}")
        session = Session()
        try:
            audit = FairnessAudit(
                patient_id=patient_id,
                timestamp=datetime.now(),
                is_fair=0,
                fairness_metrics=json.dumps(fairness_metrics)
            )
            session.add(audit)
            session.commit()
        except Exception as e:
            logging.error(f"Error logging fairness issue: {str(e)}")
            session.rollback()
        finally:
            session.close()

ethical_ai_monitor = EthicalAIMonitor()

def get_protected_attributes(patient_id: str) -> Dict[str, str]:
    # Fetch protected attributes from the database
    session = Session()
    try:
        patient = session.query(Patient).filter_by(id=patient_id).first()
        if patient:
            return {
                'gender': patient.gender,
                'race': patient.race,
                'age_group': patient.age_group
            }
        else:
            logging.error(f"Patient with ID {patient_id} not found")
            return None
    except Exception as e:
        logging.error(f"Error fetching protected attributes: {str(e)}")
        return None
    finally:
        session.close()

def get_true_label(patient_id: str) -> int:
    # Fetch the true label from the database
    session = Session()
    try:
        lab_result = session.query(LabResult).filter_by(patient_id=patient_id).order_by(LabResult.timestamp.desc()).first()
        if lab_result:
            return lab_result.true_label
        else:
            logging.error(f"No lab result found for patient with ID {patient_id}")
            return None
    except Exception as e:
        logging.error(f"Error fetching true label: {str(e)}")
        return None
    finally:
        session.close()

def ethical_ai_report(predictions: np.ndarray, true_labels: np.ndarray, protected_attributes: Dict[str, np.ndarray]) -> Dict[str, Any]:
    fairness_metrics = ethical_ai_monitor.calculate_fairness_metrics(predictions, true_labels, protected_attributes)
    is_fair = ethical_ai_monitor.check_fairness(fairness_metrics)
    confusion_matrices = ethical_ai_monitor.generate_confusion_matrices(predictions, true_labels, protected_attributes)
    ethical_ai_monitor.plot_confusion_matrices(confusion_matrices)
    classification_report = ethical_ai_monitor.generate_classification_report(predictions, true_labels, protected_attributes)

    report = {
        'fairness_metrics': fairness_metrics,
        'is_fair': is_fair,
        'confusion_matrices': {attr: f'confusion_matrix_{attr}.png' for attr in confusion_matrices.keys()},
        'classification_report': classification_report
    }

    return report

def monitor_interpretation(text: str, patient_id: str, interpretation_result: Dict[str, Any]) -> Dict[str, Any]:
    prediction = interpretation_result['prediction']
    true_label = get_true_label(patient_id)
    protected_attributes = get_protected_attributes(patient_id)

    if true_label is not None and protected_attributes is not None:
        fairness_metrics = ethical_ai_monitor.calculate_fairness_metrics(
            np.array([prediction]), 
            np.array([true_label]), 
            {attr: np.array([value]) for attr, value in protected_attributes.items()}
        )
        is_fair = ethical_ai_monitor.check_fairness(fairness_metrics)

        if not is_fair:
            ethical_ai_monitor.log_fairness_issue(patient_id, fairness_metrics)

        interpretation_result['fairness_metrics'] = fairness_metrics
        interpretation_result['is_fair'] = is_fair

    return interpretation_result

def ethical_ai_wrapper(func):
    def wrapper(text, patient_id, *args, **kwargs):
        interpretation_result = func(text, patient_id, *args, **kwargs)
        return monitor_interpretation(text, patient_id, interpretation_result)
    return wrapper
