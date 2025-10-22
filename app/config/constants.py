import os
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "qwen2.5vl:7b")
CANONICAL_PATH = os.getenv("CANONICAL_PATH", "app/config/solarcanonical.yaml")
PROMPT_PATH = os.getenv("PROMPT_PATH", "app/config/prompt.yaml")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "data/outputs")
CLEANED_DIR = os.getenv("CLEANED_FILES", "data/outputs/cleaned_outputs")
LOG_FILE = os.getenv("LOG_FILE", "logs/data_transform.log")

# MongoDB constants
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "default_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "default_collection")

# Ensure output/log directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CLEANED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
