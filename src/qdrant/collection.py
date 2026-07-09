from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from config.settings import QDRANT_URL, API_KEY


class QdrantCollection:
    def __init__(self):
        self.QDRANT_URL = QDRANT_URL
        self.API_KEY = API_KEY
        self.EMBEDDING_DIM = 768
        self.client = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.API_KEY,
            timeout=30
        )

    def create_collection(self, name_collection) -> None:
        collection_config = {
            "vectors_config": VectorParams(
                size=self.EMBEDDING_DIM,
                distance=Distance.COSINE,
                on_disk=True
            ),
            "optimizers_config": {
                "default_segment_number": 3,
                "indexing_threshold": 1000,
                "memmap_threshold": 20000,
            },
            "hnsw_config": {
                "m": 24,
                "ef_construct": 200,
                "full_scan_threshold": 15000
            },
            "quantization_config": {
                "scalar": {
                    "type": "int8",
                    "always_ram": True
                }
            }
        }

        self.client.create_collection(
            collection_name=name_collection,
            **collection_config
        )

        return f"Collection '{name_collection}' created with multilingual settings!"

    def collection_info(self, name_collection):
        try:
            return {"error": False, "collection": self.client.get_collection(name_collection)}

        except Exception:
            return {"error": True, "message": f"Collection '{name_collection}' not found!"}
