import os

from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LOCAL_API_BASE = os.getenv("LOCAL_API_BASE", "http://localhost:11434/v1")
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "llama3")