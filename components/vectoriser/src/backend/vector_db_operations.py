# embedding_handling/db_operations.py
from datetime import datetime

def store_embeddings(collection, embeddings: list, documents: list, metadatas: list, ids: list):
    """
    Store embeddings in Chroma collection
    """
    if not embeddings or not documents or not ids:
        print("No embeddings to store.")
        return

    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Stored {len(embeddings)} embeddings in collection '{collection.name}'.")


def query_embeddings(collection, query_texts: list, model, n_results: int = 2):
    """
    Retrieve nearest embeddings for given query texts
    """
    if not query_texts:
        return None

    query_embeddings = [model.encode(text).tolist() for text in query_texts]

    result = collection.query(
        query_embeddings=query_embeddings,
        n_results=n_results
    )

    return result


