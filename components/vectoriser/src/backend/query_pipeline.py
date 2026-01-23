from sentence_transformers import SentenceTransformer
from datetime import datetime
from pathlib import Path
import chromadb
from chromadb.config import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from vectoriser.src.backend.vectorise import *                                                                                                 
from vectoriser.src.backend.database_logic import PropertyDatabase
from vectoriser.src.backend.vector_db_operations import store_embeddings, query_embeddings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHROMA_DIR = PROJECT_ROOT / "src" / "backend" / "vector_database" / "chroma"
                                              
app = FastAPI()

model = get_model()

client = get_client()


origins = [
    "http://localhost:1704"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



collection = get_collection(get_client(), "embeddings_storage")    

@app.get("/retrieve/")
def retrieve(term: str):
    search_terms = [term] 
    relevant_properties = query_embeddings(collection, search_terms, model, 10)       
   
    response = {}

    
    for field in property:
        i = 0
        for value in property[field]:
            response[f"property_{i}"] = {
                    str(field): str(value)   
                 }
            i+=1                          


    return response
                                                                                       
    











































