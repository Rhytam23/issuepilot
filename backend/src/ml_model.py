import os
import joblib
import json
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from src.config import Config

class IssueClassifier:
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_path = Config.MODEL_PATH
        self.vectorizer_path = Config.VECTORIZER_PATH
        
        # Ensure model directory exists
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.vectorizer_path), exist_ok=True)

    def train(self, data: List[dict]):
        """
        Trains the model on a list of dicts with 'text' and 'label' keys.
        """
        texts = [item['text'] for item in data]
        labels = [item['label'] for item in data]
        
        self.vectorizer = TfidfVectorizer(stop_words='english')
        X = self.vectorizer.fit_transform(texts)
        
        self.model = MultinomialNB()
        self.model.fit(X, labels)
        
        self.save_model()
        print("Model trained and saved.")

    def predict(self, texts: List[str]) -> List[str]:
        """
        Predicts labels for a list of text strings.
        """
        if not self.model or not self.vectorizer:
            self.load_model()
            
        if not self.model or not self.vectorizer:
            raise ValueError("Model not trained or not found.")
            
        X = self.vectorizer.transform(texts)
        return self.model.predict(X).tolist()

    def save_model(self):
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)

    def load_model(self):
        if os.path.exists(self.model_path) and os.path.exists(self.vectorizer_path):
            self.model = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.vectorizer_path)
        else:
            print("Model files not found. Please train the model first.")

if __name__ == "__main__":
    # Simple training script if run directly
    classifier = IssueClassifier()
    
    # Load sample data
    data_path = "data/labeled_issues.json"
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
        classifier.train(data)
    else:
        print(f"Data file not found at {data_path}")
