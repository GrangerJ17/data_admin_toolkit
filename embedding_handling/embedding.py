from sentence_transformers import SentenceTransformer
import asyncio
import sqlite3
from datetime import datetime
from webscrape.database_logic import PropertyDatabase
from embedding_handling.db_operations import *
import chromadb
from chromadb.config import Settings

def get_collection(client, name):
    try:
        return client.get_collection(name)
    except Exception:
        return client.create_collection(name,  
                                        metadata={ "hnsw:space": "cosine",
                                                "hnsw:num_threads": 4,
                                                "hnsw:construction_ef": 200})



settings = Settings(is_persistent=True, persist_directory="../database/")
client = chromadb.Client(settings=settings)
collection = get_collection(client, "embeddings_storage")
model = SentenceTransformer("all-mpnet-base-v2")
db = PropertyDatabase()

def embed_text(document: list):
    return model.encode(document)

def search_embeddings():
    pass

def main():
    

    
    query="SELECT * FROM scrape_history WHERE vectorised = ?"
    property_metadata = []
    properties_to_vectorise = []


    with sqlite3.connect(db.db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query, (False,))
        results = [dict(row) for row in cur.fetchall()]

        for res in results:
            if res["vectorised"] == 0:
                property_metadata.append(res)

        for entry in property_metadata:
            cur.execute("SELECT * FROM properties WHERE property_id = ?", (entry["property_id"], ))
            properties_to_vectorise.append(dict(cur.fetchone()))

    descriptions = [property["description"] for property in properties_to_vectorise] 
    embedded_docs = [embed_text(desc) for desc in descriptions]
    metadatas = [{"embedded_at": str(datetime.now())} for property in properties_to_vectorise]
    ids = [property["property_id"] for property in properties_to_vectorise]

    store_embeddings(collection=collection, embeddings=embedded_docs, documents=descriptions, metadatas=metadatas, ids=ids)


result = query_embeddings(collection=collection, query_texts=["Looking for a rental property in a bustling part of sydney. Preferably with an artsy culture"], n_results=2)

print(result)

with sqlite3.connect(db.db_path) as conn:
    cur = conn.cursor()
    cur.execute()