import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("REPO_NAME")  # format: "owner/repo"
    MODEL_PATH = os.getenv("MODEL_PATH", "model_artifacts/model.pkl")
    VECTORIZER_PATH = os.getenv("VECTORIZER_PATH", "model_artifacts/vectorizer.pkl")
    STORAGE_FILE = os.getenv("STORAGE_FILE", "storage.json")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    API_KEY = os.getenv("API_KEY", "dev-secret-key") # Default for dev convenience
