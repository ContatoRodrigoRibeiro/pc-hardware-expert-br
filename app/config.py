import os
from dotenv import load_dotenv

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LLM_MODEL = os.getenv("LLM_MODEL", "grok-3")