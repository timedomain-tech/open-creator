from typing import List, Any, Dict
from langchain.vectorstores.qdrant import Qdrant
from langchain.docstore.document import Document
from creator.utils import generate_uuid_like_string


class BaseVectorStore:

    def __init__(self, vectordb_path, embedding, collection_name):
        self.vectordb_path = vectordb_path
        self.embedding = embedding
        self.collection_name = collection_name
        self.db = None

    def _preprocess(self, doc: Any, **kwargs):
        """Preprocess the input doc into text"""
        return doc

    def _postprocess(self, documents: List[Document]):
        """Postprocess the documents"""
        return documents

    def _update_index(self):
        pass

    def reset(self):
        self.db = None

    def index(self, documents: List[Any], ids: List[str] = None, metadatas: List[Dict] = None):
        """Public method to index a document."""
        if metadatas is None:
            metadatas = documents
        texts = [self._preprocess(doc) for doc in documents]
        if ids is None:
            ids = [generate_uuid_like_string() for _ in range(len(texts))]
        if self.db is None:
            self.db = Qdrant.from_texts(texts=texts, embedding=self.embedding, metadatas=metadatas, ids=ids, path=self.vectordb_path, collection_name=self.collection_name)
        else:
            self.db.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    def search(self, query: str, top_k: int = 3, threshold=0.8) -> List[dict]:
        self._update_index()
        documents = self.db.similarity_search(query=query, k=top_k, score_threshold=threshold)
        return self._postprocess(documents)
