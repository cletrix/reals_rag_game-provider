import os
from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore

def get_query_engine():
    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://qdrant:6333"))
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=os.getenv("QDRANT_COLLECTION", "landf_docs"),
    )
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_ctx,
    )
    return index.as_query_engine(
        similarity_top_k=int(os.getenv("SIMILARITY_TOP_K", "4")),
        response_mode="compact",
    )
