import os
from qdrant_client import QdrantClient
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore


def _build_index() -> VectorStoreIndex:
    client = QdrantClient(url=os.getenv("QDRANT_URL", "http://qdrant:6333"))
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=os.getenv("QDRANT_COLLECTION", "landf_docs"),
    )
    storage_ctx = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_ctx,
    )


def get_query_engine(similarity_top_k: int | None = None):
    index = _build_index()
    top_k = similarity_top_k or int(os.getenv("SIMILARITY_TOP_K", "4"))
    return index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="compact",
    )


def get_streaming_query_engine(similarity_top_k: int | None = None):
    index = _build_index()
    top_k = similarity_top_k or int(os.getenv("SIMILARITY_TOP_K", "2"))
    return index.as_query_engine(
        similarity_top_k=top_k,
        response_mode="compact",
        streaming=True,
    )
