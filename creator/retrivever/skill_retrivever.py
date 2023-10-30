from typing import List
import json
import os

from langchain.docstore.document import Document

from creator.config.library import config

from .base import BaseVectorStore
from .embedding_creator import create_embedding


class SkillVectorStore(BaseVectorStore):

    def __init__(self):
        self.vectordb_path = config.vectordb_path
        self.embedding = create_embedding(config)
        self.collection_name = "skill_library"
        self.db = None

    def _update_index(self):
        # glob skill_library_path to find `embedding_text.txt`
        texts = []
        metadatas = []
        for root, dirs, files in os.walk(config.local_skill_library_path):
            for file in files:
                if file == "embedding_text.txt":
                    embedding_text_path = os.path.join(root, file)
                    with open(embedding_text_path, mode="r", encoding="utf-8") as f:
                        embedding_text = f.read()
                    skill_path = os.path.join(root, "skill.json")
                    with open(skill_path, encoding="utf-8") as f:
                        skill_json = json.load(f)
                    texts.append(embedding_text)
                    metadatas.append(skill_json)
        self.index(documents=texts, metadatas=metadatas)

    def _postprocess(self, documents: List[Document]):
        return [doc.metadata for doc in documents]
