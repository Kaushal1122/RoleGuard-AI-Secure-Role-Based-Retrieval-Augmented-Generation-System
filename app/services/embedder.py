import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb


# Project root (company-chatbot)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Data paths
CHUNKS_PATH = BASE_DIR / "data" / "processed" / "chunks.jsonl"
EMBEDDED_PATH = BASE_DIR / "data" / "processed" / "chunks_with_embeddings.jsonl"

# Vector DB path (at project root)
VECTOR_DB_PATH = BASE_DIR / "chroma_db"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "chroma_db"


def load_chunks(path: Path):
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    return chunks


def load_embedding_cache(path: Path):
    cache = {}
    if not path.exists():
        return cache

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            cache[record["chunk_id"]] = record
    return cache


def save_embedding_cache(records: list, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def main():
    if not CHUNKS_PATH.exists():
        print(f"Missing file: {CHUNKS_PATH}")
        return

    VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)

    print("Loading chunks...")
    chunks = load_chunks(CHUNKS_PATH)

    print("Loading embedding cache...")
    cache = load_embedding_cache(EMBEDDED_PATH)

    print("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Initializing ChromaDB (persistent)...")
    client = chromadb.PersistentClient(path=str(VECTOR_DB_PATH))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    updated_records = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]

        if chunk_id in cache:
            record = cache[chunk_id]
            embedding = record["embedding"]
        else:
            embedding = model.encode(chunk["text"]).tolist()
            record = {**chunk, "embedding": embedding}

        updated_records.append(record)

        department = chunk["department"]

        if department.lower() == "general":
            accessible_roles = [
                "Employees", "Finance", "HR",
                "Marketing", "Engineering", "C-Level"
            ]
        else:
            accessible_roles = [department, "C-Level"]

        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            metadatas=[{
                "source_document": chunk["source_document"],
                "department": department,
                "accessible_roles": ",".join(accessible_roles),
                "token_count": chunk["token_count"]
            }],
            documents=[chunk["text"]]
        )

    save_embedding_cache(updated_records, EMBEDDED_PATH)

    print(f"Embedded {len(updated_records)} chunks")
    print(f"Saved cache to: {EMBEDDED_PATH}")
    print(f"Chroma collection name: {COLLECTION_NAME}")
    print(f"Vector DB stored at: {VECTOR_DB_PATH}")


if __name__ == "__main__":
    main()
