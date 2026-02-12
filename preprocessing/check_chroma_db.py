import chromadb
from pathlib import Path


# Project root (company-chatbot)
BASE_DIR = Path(__file__).resolve().parent.parent

VECTOR_DB_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))

collection = client.get_collection("chroma_db")

print("Count:", collection.count())
