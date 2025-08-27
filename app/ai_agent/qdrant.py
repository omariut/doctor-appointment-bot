import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_cohere import CohereEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_experimental.text_splitter import SemanticChunker
from langchain.indexes import SQLRecordManager, index
from qdrant_client.http.models import VectorParams, Distance


class QdrantIngestionService:

    record_manager: Optional[SQLRecordManager] = None

    def __init__(self, min_chunk_size=None):
        self.qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        self.cohere_embeddings = CohereEmbeddings(model="embed-multilingual-v3.0")
        self.text_splitter = SemanticChunker(
            self.cohere_embeddings,
            # Reference this study https://github.com/monami44/Langchain-Semantic-Chunking-Arena?tab=readme-ov-file#retrieval-quality-evaluation
            breakpoint_threshold_type="interquartile",
            breakpoint_threshold_amount=1,
            min_chunk_size=min_chunk_size,
        )
        self.create_collection()

    def _get_vector_store_instance(self) -> VectorStore:
        return QdrantVectorStore(
            client=self.qdrant,
            collection_name="doctors-appointments",
            embedding=self.cohere_embeddings,
        )

    def _get_record_manager(self):
        print(self.record_manager)
        if not getattr(self, "record_manager"):
            self.record_manager = SQLRecordManager(
                namespace=f"qdrant/doctors/",
                db_url=os.getenv("PG_CONNECTION_STRING"),
            )
            self.record_manager.create_schema()
        print(self.record_manager)
        return self.record_manager

    def _index(self, docs: List[Document]):
        vector_store = self._get_vector_store_instance()
        record_manager = self._get_record_manager()
        return index(
            docs,
            record_manager,
            vector_store,
            cleanup="incremental",
            source_id_key="source",
        )

    def _get_docs(self, doctors: list):
        docs = []
        for doctor in doctors:
            text = f"{doctor['name']}, {doctor['specialty']}, {doctor['degree']}, {doctor['experience']}"
            metadata = {"source": doctor["id"], **doctor}
            docs.append(Document(page_content=text, metadata=metadata))
        return docs

    def create_collection(self):
        self.qdrant.recreate_collection(
            collection_name="doctors-appointments",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

    def upsert(self, doctors: list):
        docs = self._get_docs(doctors)
        self._index(docs)

    def search(self, query: str):
        vector_store = self._get_vector_store_instance()
        results = vector_store.similarity_search(query, k=2)

        for r in results:
            print(r.metadata["name"], "-", r.metadata["specialty"])
