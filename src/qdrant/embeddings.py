from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, SearchParams, RecommendStrategy
from fastembed import TextEmbedding
import numpy as np
import os
import uuid
from typing import List, Dict, Optional
from functools import lru_cache
from config.settings import QDRANT_URL, API_KEY

# Modelo carregado uma vez por processo, nao por instancia/request.
# cache_dir fixo evita rebaixar o modelo (~1GB) a cada restart do container.
_MODEL = TextEmbedding(
    model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
    cache_dir=os.getenv("FASTEMBED_CACHE_DIR", ".fastembed_cache")
)


@lru_cache(maxsize=10000)
def _generate_embedding(text: str) -> List[float]:
    cleaned_text = ' '.join(text.strip().split())
    vector = next(_MODEL.embed([cleaned_text]))
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector.tolist()


class Qdrant:
    def __init__(self, collection_name: str = "documents"):
        self.QDRANT_URL = QDRANT_URL
        self.API_KEY = API_KEY
        self.COLLECTION_NAME = collection_name
        self.client = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.API_KEY,
            prefer_grpc=True
        )


    def add_document(self, title, description, metadata: Optional[Dict] = None) -> dict:
        full_text = f"{title} - {description}"
        vector = _generate_embedding(full_text)
        
        payload = {
            "title": title,
            "description": description
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


    def search(self, query: str, limit: int = 1, score_threshold: float = None, filter_conditions: Optional[Dict] = None) -> List[Dict]:
        query_vector = _generate_embedding(query)
        qdrant_filter = None

        if filter_conditions:
            qdrant_filter = Filter(**filter_conditions)

        search_result = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            query_filter=qdrant_filter,
            limit=limit,
            score_threshold=score_threshold,
            search_params=SearchParams(
                hnsw_ef=128,
                exact=False
            )
        ).points

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
                "vector": hit.vector
            }
            for hit in search_result
        ]
