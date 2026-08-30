"""Vector Store Manager and Indexing Service using ChromaDB and Sentence-Transformers."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from backend.app.core.config import PROJECT_ROOT, get_settings
from backend.app.rag.chunker import SchemeChunker
from backend.app.schemas.chunk import KnowledgeChunk

logger = logging.getLogger(__name__)

COLLECTION_NAME = "mutual_fund_facts"


class VectorStoreService:
    """ChromaDB Vector Store Service for atomic knowledge chunk indexing and retrieval."""

    def __init__(self, persist_directory: Optional[Path] = None) -> None:
        self.settings = get_settings()
        self.persist_directory = persist_directory or self.settings.absolute_vector_store_path
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize ChromaDB persistent client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
        )

        # Initialize sentence-transformers embedding function
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.settings.embedding_model_name
        )

        self._collection = None

    @property
    def collection(self) -> chromadb.Collection:
        """Lazily obtain or create the ChromaDB facts collection."""
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def count(self) -> int:
        """Return total number of indexed documents in the collection."""
        try:
            return self.collection.count()
        except Exception:
            return 0

    def reset_collection(self) -> None:
        """Delete and recreate the knowledge collection."""
        try:
            self.client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass
        self._collection = self.client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def load_chunks_from_file_or_chunker(self) -> List[KnowledgeChunk]:
        """Load atomic knowledge chunks from processed/chunks.json or generate dynamically."""
        chunks_path = PROJECT_ROOT / "data" / "processed" / "chunks.json"
        if chunks_path.exists():
            try:
                with open(chunks_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return [KnowledgeChunk(**item) for item in data.get("chunks", [])]
            except Exception as e:
                logger.warning("Could not read chunks.json directly (%s), regenerating via chunker", e)

        chunker = SchemeChunker()
        collection = chunker.chunk_all()
        return collection.chunks

    def initialize_store(self, force_reload: bool = False) -> int:
        """Populate ChromaDB with the 38 factual chunks if empty or if force_reload is True.
        
        Returns:
            Total count of indexed documents in collection.
        """
        current_count = self.count()
        if current_count >= 38 and not force_reload:
            logger.info("Vector store already initialized with %d chunks", current_count)
            return current_count

        if force_reload:
            self.reset_collection()

        chunks = self.load_chunks_from_file_or_chunker()
        if not chunks:
            raise ValueError("No chunks found or generated to populate vector store.")

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict[str, Any]] = []

        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.content)
            metadatas.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "scheme_code": chunk.scheme_code,
                    "scheme_name": chunk.scheme_name,
                    "category": chunk.category,
                    "parameter": chunk.parameter,
                    "title": chunk.title,
                    "official_source_url": chunk.official_source_url,
                    "last_updated": chunk.last_updated,
                    "keywords": ", ".join(chunk.keywords),
                }
            )

        # Upsert documents into collection
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        total = self.count()
        logger.info("Successfully indexed %d chunks into ChromaDB", total)
        return total

    def query(
        self,
        query_text: str,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query vector store with optional metadata filtering.
        
        Args:
            query_text: The search query string.
            n_results: Number of nearest neighbors to return.
            where: ChromaDB metadata filter dictionary (e.g. {"scheme_code": "..."}).
            where_document: Document text substring filter.

        Returns:
            List of result dicts containing id, document, metadata, and similarity_score.
        """
        # Ensure collection is loaded and populated
        if self.count() == 0:
            self.initialize_store()

        query_args: Dict[str, Any] = {
            "query_texts": [query_text],
            "n_results": min(n_results, max(1, self.count())),
        }
        if where:
            query_args["where"] = where
        if where_document:
            query_args["where_document"] = where_document

        results = self.collection.query(**query_args)

        formatted_results: List[Dict[str, Any]] = []
        if not results or not results.get("ids") or not results["ids"][0]:
            return formatted_results

        ids = results["ids"][0]
        docs = results["documents"][0] if results.get("documents") else []
        metas = results["metadatas"][0] if results.get("metadatas") else []
        distances = results["distances"][0] if results.get("distances") else []

        for i in range(len(ids)):
            dist = distances[i] if i < len(distances) else 0.0
            # For cosine distance (range 0 to 2), similarity = 1 - (dist / 2.0)
            similarity = max(0.0, min(1.0, 1.0 - (dist / 2.0)))

            formatted_results.append(
                {
                    "chunk_id": ids[i],
                    "content": docs[i] if i < len(docs) else "",
                    "metadata": metas[i] if i < len(metas) else {},
                    "similarity_score": round(similarity, 4),
                    "distance": round(dist, 4),
                }
            )

        return formatted_results

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific chunk by its chunk_id."""
        res = self.collection.get(ids=[chunk_id])
        if res and res.get("ids") and len(res["ids"]) > 0:
            return {
                "chunk_id": res["ids"][0],
                "content": res["documents"][0] if res.get("documents") else "",
                "metadata": res["metadatas"][0] if res.get("metadatas") else {},
            }
        return None

    def get_chunks_by_scheme(self, scheme_code: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks belonging to a specific scheme_code."""
        res = self.collection.get(where={"scheme_code": scheme_code})
        chunks: List[Dict[str, Any]] = []
        if res and res.get("ids"):
            for i in range(len(res["ids"])):
                chunks.append(
                    {
                        "chunk_id": res["ids"][i],
                        "content": res["documents"][i] if res.get("documents") else "",
                        "metadata": res["metadatas"][i] if res.get("metadatas") else {},
                    }
                )
        return chunks
