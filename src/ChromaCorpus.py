from pathlib import Path
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

class ChromaCorpus:
    def __init__(
        self,
        chroma_dir: str,
        collection_name: str = "academic_corpus",
        openai_api_key: Optional[str] = None,
        k: int = 6,
        mode: str = "load",  # 'load' | 'create' | 'reset'
    ):
        self.chroma_dir = Path(chroma_dir)
        self.collection_name = collection_name
        self.k = k
        self.mode = mode.lower()

        # ── Configure Chroma client ──────────────────────
        self.client = chromadb.Client(Settings(
            persist_directory=str(self.chroma_dir),
            is_persistent=True,
            allow_reset=(self.mode == "reset")
        ))

        if self.mode == "reset":
            print("Resetting Chroma DB at", self.chroma_dir)
            self.client.reset()

        # ── Ensure collection exists ─────────────────────
        self.collection = self.client.get_or_create_collection(self.collection_name)

        # ── Embedding + Retriever setup ──────────────────
        self.embedding_function = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=openai_api_key
        )
        self.vectstore = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embedding_function
        )
        self.retriever = self.vectstore.as_retriever(search_kwargs={"k": self.k})

    def count_documents(self) -> int:
        return self.collection.count()

    def get_relevant_chunks(self, query: str) -> List[Dict[str, Any]]:
        return self.retriever.get_relevant_documents(query)

    def add_texts(self, texts: list[str], metadatas: list[dict], ids: Optional[list[str]] = None):
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

    def get_retriever(self):
        return self.retriever

    def get_collection(self):
        return self.collection

