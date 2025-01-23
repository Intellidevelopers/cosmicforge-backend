
import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score
import logging
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple
from transformers import BertTokenizer, BertForSequenceClassification
from sklearn.ensemble import RandomForestClassifier
import asyncio

load_dotenv()

# Database setup
DB_URL = os.getenv('DATABASE_URL')
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class FederatedLearningLog(Base):
    __tablename__ = 'federated_learning_logs'
    id = Column(Integer, primary_key=True)
    round_number = Column(Integer)
    accuracy = Column(Float)
    f1_score = Column(Float)
    timestamp = Column(DateTime)
    model_version = Column(String)

Base.metadata.create_all(engine)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnsembleModel(nn.Module):
    def __init__(self):
        super(EnsembleModel, self).__init__()
        self.bert_model = BertForSequenceClassification.from_pretrained('bert-base-uncased')
        self.rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

    def forward(self, input_ids, attention_mask):
        bert_output = self.bert_model(input_ids, attention_mask=attention_mask)
        return bert_output.logits

    async def train_model(self, texts: List[str], labels: List[int], batch_size: int = 32, epochs: int = 3):
        # Prepare data for BERT
        encoded_inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        dataset = TensorDataset(encoded_inputs['input_ids'], encoded_inputs['attention_mask'], torch.tensor(labels))
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

        # Train BERT
        optimizer = torch.optim.AdamW(self.bert_model.parameters(), lr=2e-5)
        for epoch in range(epochs):
            for batch in dataloader:
                input_ids, attention_mask, batch_labels = batch
                outputs = self(input_ids, attention_mask)
                loss = nn.functional.cross_entropy(outputs, batch_labels)
                loss.backward()
                optimizer.step()
                optimizer.zero_grad()
            await asyncio.sleep(0)  
        # Train Random Forest
        bert_features = []
        with torch.no_grad():
            for batch in dataloader:
                input_ids, attention_mask, _ = batch
                outputs = self(input_ids, attention_mask)
                bert_features.extend(outputs.numpy())
            await asyncio.sleep(0) 
        self.rf_model.fit(bert_features, labels)

    async def predict(self, texts: List[str]) -> np.ndarray:
        encoded_inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            bert_output = self(encoded_inputs['input_ids'], encoded_inputs['attention_mask'])
        bert_features = bert_output.numpy()
        rf_predictions = self.rf_model.predict(bert_features)
        return rf_predictions

class FederatedLearning:
    def __init__(self, num_rounds: int = 10):
        self.global_model = EnsembleModel()
        self.num_rounds = num_rounds
        self.model_version = datetime.now().strftime("%Y%m%d%H%M%S")

    async def train_round(self, client_data: List[Dict[str, Any]]):
        client_models = []
        for client_id, data in enumerate(client_data):
            try:
                client_model = EnsembleModel()
                await client_model.train_model(data['texts'], data['labels'])
                client_models.append(client_model)
                logging.info(f"Training completed for client {client_id}")
            except Exception as e:
                logging.error(f"Error training model for client {client_id}: {str(e)}")
            await asyncio.sleep(0)  # Allow other tasks to run

        await self.aggregate_models(client_models)

    async def aggregate_models(self, client_models: List[EnsembleModel]):
        try:
            # Aggregate BERT model parameters
            for name, param in self.global_model.bert_model.named_parameters():
                avg_param = torch.stack([model.bert_model.state_dict()[name] for model in client_models]).mean(dim=0)
                param.data.copy_(avg_param)

            # Aggregate Random Forest model
            all_estimators = [model.rf_model.estimators_ for model in client_models]
            self.global_model.rf_model.estimators_ = [
                sum(estimators) / len(estimators) for estimators in zip(*all_estimators)
            ]

            logging.info("Model aggregation completed successfully")
        except Exception as e:
            logging.error(f"Error during model aggregation: {str(e)}")

    async def train(self, all_client_data: List[Dict[str, Any]]):
        for round in range(self.num_rounds):
            logging.info(f"Starting federated learning round {round + 1}/{self.num_rounds}")
            await self.train_round(all_client_data)
            
            # Evaluate global model after each round
            accuracy, f1 = await self.evaluate_global_model(all_client_data)
            await self.log_federated_learning_round(round + 1, accuracy, f1)
            
            logging.info(f"Round {round + 1} completed. Accuracy: {accuracy:.4f}, F1 Score: {f1:.4f}")

    def get_global_model(self) -> EnsembleModel:
        return self.global_model

    async def evaluate_global_model(self, all_client_data: List[Dict[str, Any]]) -> Tuple[float, float]:
        all_texts = []
        all_labels = []
        for data in all_client_data:
            all_texts.extend(data['texts'])
            all_labels.extend(data['labels'])

        X_test, y_test = train_test_split(all_texts, all_labels, test_size=0.2, random_state=42)
        predictions = await self.global_model.predict(X_test)
        
        accuracy = accuracy_score(y_test, predictions)
        f1 = f1_score(y_test, predictions, average='weighted')
        
        return accuracy, f1

    async def log_federated_learning_round(self, round_number: int, accuracy: float, f1_score: float):
        try:
            session = Session()
            log_entry = FederatedLearningLog(
                round_number=round_number,
                accuracy=accuracy,
                f1_score=f1_score,
                timestamp=datetime.now(),
                model_version=self.model_version
            )
            session.add(log_entry)
            await asyncio.to_thread(session.commit)
        except Exception as e:
            logging.error(f"Error logging federated learning round: {str(e)}")
            await asyncio.to_thread(session.rollback)
        finally:
            await asyncio.to_thread(session.close)

async def prepare_data_for_federated_learning(data: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Any]]]:
    texts = [item['text'] for item in data]
    labels = [item['label'] for item in data]
    
    X_train, X_val, y_train, y_val = train_test_split(texts, labels, test_size=0.2, random_state=42)
    
    return {
        'train': {'texts': X_train, 'labels': y_train},
        'val': {'texts': X_val, 'labels': y_val}
    }

federated_learning = FederatedLearning()

async def train_federated_model(data: List[Dict[str, Any]]):
    prepared_data = await prepare_data_for_federated_learning(data)
    await federated_learning.train([prepared_data['train']])
    return federated_learning.get_global_model()

async def predict_with_federated_model(texts: List[str]) -> np.ndarray:
    global_model = federated_learning.get_global_model()
    return await global_model.predict(texts)
