import numpy as np
from scipy.optimize import linear_sum_assignment
from config import Config
import logging

logger = logging.getLogger(__name__)

class Optimizer:
    def optimize_appointments(self, probabilities, provider_availability, preferred_dates):
        try:
            # Combine probabilities with provider availability
            combined_scores = probabilities * provider_availability
            
            # Reshape the scores to a 2D array (dates x hours)
            scores_2d = combined_scores.reshape(len(preferred_dates), -1)
            
            # Use the Hungarian algorithm to find the optimal assignment
            row_ind, col_ind = linear_sum_assignment(scores_2d, maximize=True)
            
            suggestions = []
            for i, j in zip(row_ind, col_ind):
                date = preferred_dates[i]
                hour = Config.WORKING_HOURS_START + j
                probability = probabilities[i * Config.HOURS_PER_DAY + j]
                
                suggestions.append({
                    'date': date,
                    'time': f"{hour:02d}:00",
                    'probability': float(probability)
                })
            
            # Sort suggestions by probability and return top N
            suggestions.sort(key=lambda x: x['probability'], reverse=True)
            return suggestions[:Config.MAX_SUGGESTIONS]
        except Exception as e:
            logger.error(f"Error in optimize_appointments: {str(e)}")
            raise
