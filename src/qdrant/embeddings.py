from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, SearchParams, RecommendStrategy
from sentence_transformers import SentenceTransformer
import uuid
import os
from typing import List, Dict, Optional
from functools import lru_cache
from dotenv import load_dotenv
from pprint import pprint


load_dotenv()

class QdrantEmbedding:
    def __init__(self, collection_name: str = "courses"):
        self.QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.API_KEY = os.getenv("QDRANT_API_KEY")
        self.COLLECTION_NAME = collection_name
        self.client = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.API_KEY,
            prefer_grpc=True
        )

        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
            device="cpu"
        )


    @lru_cache(maxsize=10000)
    def _generate_embedding(self, text: str) -> List[float]:
        cleaned_text = ' '.join(text.strip().split())
        return self.model.encode(
            cleaned_text,
            convert_to_numpy=True,
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False
        ).tolist()


    def add_course(self, title: str, description: str, metadata: Optional[Dict] = None) -> dict:
        full_text = f"{title} - {description}"
        vector = self._generate_embedding(full_text)

        payload = {
            "title": title,
            "description": description,
            "full_text": full_text,
        }

        if metadata:
            payload.update({"metadata": metadata})

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload=payload
        )

        return self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point],
            wait=True
        )


    def search(self, query: str, limit: int = 2, score_threshold: float = None, filter_conditions: Optional[Dict] = None) -> List[Dict]:
        query_vector = self._generate_embedding(query)
        qdrant_filter = None

        if filter_conditions:
            qdrant_filter = Filter(**filter_conditions)

        search_result = self.client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=qdrant_filter,
            limit=limit,
            score_threshold=score_threshold,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False
            )
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "vector": hit.vector
            }
            for hit in search_result
        ]
