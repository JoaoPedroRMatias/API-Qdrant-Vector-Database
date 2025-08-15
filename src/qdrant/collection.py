from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv
import os


load_dotenv()

class QdrantCollection:
    def __init__(self, collection_name: str = "courses"):
        self.QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.API_KEY = os.getenv("QDRANT_API_KEY")
        self.COLLECTION_NAME = collection_name
        self.EMBEDDING_DIM = 768
        self.client = QdrantClient(
            url=self.QDRANT_URL,
            api_key=self.API_KEY,
            timeout=30
        )


    def create_collection(self) -> None:
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

        try:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                **collection_config
            )
            print(f"Collection '{self.COLLECTION_NAME}' created with multilingual settings!")

        except Exception as e:
            print(f"Error creating collection: {str(e)}")
            raise


    def collection_info(self) -> dict:
        return self.client.get_collection(self.COLLECTION_NAME)
