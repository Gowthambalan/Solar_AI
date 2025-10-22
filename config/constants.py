import os
from dotenv import load_dotenv
load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME")

CANONICAL_PATH = "config/solarcanonical.yaml"
PROMPT_PATH = "config/prompt.yaml"
OUTPUT_DIR = "data/outputs"
LOG_FILE = "logs/data_transform.log"

