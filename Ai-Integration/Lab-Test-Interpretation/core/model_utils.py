
import logging
import torch
import joblib
import json
import aiofiles
from typing import List, Dict, Any, Optional
from .federated_learning import EnsembleModel

async def load_model(path: str = 'federated_model') -> Optional[EnsembleModel]:
    try:
        model = EnsembleModel()
        model.bert_model.load_state_dict(torch.load(f'{path}_bert.pth'))
        model.rf_model = joblib.load(f'{path}_rf.joblib')
        logging.info(f"Loaded federated model from {path}")
        return model
    except FileNotFoundError:
        logging.info("No existing federated model found")
        return None
    except Exception as e:
        logging.error(f"Error loading federated model: {str(e)}")
        return None

async def save_model(model: EnsembleModel, path: str = 'federated_model'):
    try:
        torch.save(model.bert_model.state_dict(), f'{path}_bert.pth')
        joblib.dump(model.rf_model, f'{path}_rf.joblib')
        logging.info(f"Saved federated model to {path}")
    except Exception as e:
        logging.error(f"Error saving federated model: {str(e)}")

async def load_initial_data() -> List[Dict[str, Any]]:
    try:
        async with aiofiles.open('initial_data.json', mode='r') as f:
            content = await f.read()
            data = json.loads(content)
        logging.info(f"Loaded {len(data)} initial data points")
        return data
    except FileNotFoundError:
        logging.warning("No initial data file found")
        return []
    except json.JSONDecodeError:
        logging.error("Error decoding initial data JSON")
        return []
    except Exception as e:
        logging.error(f"Error loading initial data: {str(e)}")
        return []
