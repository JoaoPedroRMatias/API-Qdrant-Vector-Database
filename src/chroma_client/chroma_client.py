import chromadb
from sentence_transformers import SentenceTransformer
import json
import os


class ChromaClient:
    def __init__(self, host="localhost", port=8000):
        self.client = chromadb.HttpClient(host=host, port=port)
        self.collection = self.client.get_or_create_collection(name="psychology_books")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_db(self, data):
        result = self.collection.query(
            query_texts=[data],
            n_results=3
        )
        return result