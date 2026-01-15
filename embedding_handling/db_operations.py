


def store_embeddings(collection, embeddings: list,documents: list, metadatas: list, ids: list, target_db: str = None):
    collection.add(embeddings=embeddings, 
                   documents=documents,
                metadatas=metadatas,
                ids=ids)

def query_embeddings(collection, query_texts: list, n_results: int = 2, target_db: str = None):
    if target_db is not None:
        collection = target_db

    result = collection.query(
        query_texts=query_texts,
        n_results=n_results
    )

    return result
    

def get_from_sql_db(property_id: str, n_results:int = 2, target_db: str = None):
    pass

