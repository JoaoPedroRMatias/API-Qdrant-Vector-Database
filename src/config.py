from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
QDRANT_URL = os.getenv("http://localhost:6333")
API_KEY = os.getenv("QDRANT_API_KEY")
