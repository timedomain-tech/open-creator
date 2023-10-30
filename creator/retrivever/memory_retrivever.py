from typing import List

from langchain.docstore.document import Document
from langchain.adapters.openai import convert_openai_messages

from creator.config.library import config

from .base import BaseVectorStore
from .embedding_creator import create_embedding


class MemoryVectorStore(BaseVectorStore):

    def __init__(self, collection_name="recall_memory"):
        self.vectordb_path = config.vectordb_path
        self.embedding = create_embedding(config)
        self.collection_name = collection_name
        self.db = None

    def _postprocess(self, documents: List[Document]):
        return [convert_openai_messages(doc.metadata) for doc in documents]
