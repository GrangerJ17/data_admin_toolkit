# embedding_handling/vectorise.py
from sentence_transformers import SentenceTransformer
from datetime import datetime
from pathlib import Path
import chromadb
from chromadb.config import Settings

from scraper.src.database_logic import PropertyDatabase
from vectoriser.src.vector_db_operations import store_embeddings, query_embeddings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = PROJECT_ROOT / "src" / "vector_database" / "chroma"

print(PROJECT_ROOT)
print(CHROMA_DIR)

model = SentenceTransformer("all-mpnet-base-v2")

client = chromadb.Client(
    Settings(is_persistent=True, persist_directory=str(CHROMA_DIR))
)

def get_collection(client, name: str):
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name)

collection = get_collection(client, "embeddings_storage")

# Postgres DB wrapper
db = PropertyDatabase() 

def embed_text(text: str):
    return model.encode(text).tolist()

def main():
    properties_to_vectorise = []

    # Use the existing Postgres connection
    conn = db.connection
    cur = conn.cursor()

    # Fetch unvectorised properties
    cur.execute("SELECT * FROM scrape_history WHERE vectorised = 0")
    results = cur.fetchall()
    cur.execute("UPDATE scrape_history SET vectorised = 1 WHERE vectorised = 0")
    if not results:
        print("No unvectorised properties found.")
        return

    for entry in results:
        property_id = entry[0]  # adjust index based on your table structure
        cur.execute("SELECT * FROM properties WHERE property_id = %s", (property_id,))
        row = cur.fetchone()
        if row:
            # convert row to dict if needed
            colnames = [desc[0] for desc in cur.description]
            properties_to_vectorise.append(dict(zip(colnames, row)))

    if not properties_to_vectorise:
        print("No properties found to vectorise.")
        return

    # Embed descriptions
    descriptions = [p["description"] for p in properties_to_vectorise]
    embedded_docs = [embed_text(desc) for desc in descriptions]
    metadatas = [{"embedded_at": str(datetime.now())} for _ in properties_to_vectorise]
    ids = [p["property_id"] for p in properties_to_vectorise]

    # Store in Chroma
    store_embeddings(collection, embedded_docs, descriptions, metadatas, ids)

    # Mark properties as vectorised in Postgres
    for pid in ids:
        cur.execute("UPDATE scrape_history SET vectorised = 1 WHERE property_id = %s", (pid,))
    conn.commit()

    print(f"Vectorised and stored {len(ids)} properties.")

def search_embeddings(query_texts: list, n_results: int = 2):
    return query_embeddings(collection, query_texts, model, n_results=n_results)


if __name__ == "__main__":
    main()

    # Example retrieval
    query = "Looking for a rental property in a bustling part of Sydney"
    results = search_embeddings([query], n_results=5)

    print("Retrieved documents:", results['documents'])
    print("IDs:", results['ids'])
    print("Distances:", results['distances'])

