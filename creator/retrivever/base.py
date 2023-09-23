import numpy as np
from langchain.embeddings import OpenAIEmbeddings
from typing import List
from creator.schema.library import config
from creator.utils import cosine_similarity
import os
import json


class BaseVectorStore:

    def __init__(self, skill_library_path: str = ""):

        self.vectordb_path: str = config.local_skill_library_vectordb_path
        self.skill_library_path = config.local_skill_library_path
        self.vector_store = {}
        self.embeddings = None
        self.embedding_model = OpenAIEmbeddings()
        self.sorted_keys = []
        self.query_cache = {}

        if skill_library_path and os.path.exists(skill_library_path):
            self.skill_library_path = skill_library_path

        if os.path.isdir(self.skill_library_path):
            self.vectordb_path = self.vectordb_path + "/vector_db.json"

        if os.path.exists(self.vectordb_path):
            # load vectordb
            with open(self.vectordb_path, "r") as f:
                self.vector_store = json.load(f)
        
        self.update_index()

    def update_index(self):
        # glob skill_library_path to find `embedding_text.txt`
        embeddings = []

        for root, dirs, files in os.walk(self.skill_library_path):
            for file in files:
                if root not in self.vector_store and file == "embedding_text.txt":
                    embedding_text_path = os.path.join(root, file)
                    with open(embedding_text_path, "r") as f:
                        embedding_text = f.read()
                    
                    skill_path = os.path.join(root, "skill.json")
                    with open(skill_path) as f:
                        skill_json = json.load(f)
                    skill_json["skill_id"] = root
                    skill_json["embedding_text"] = embedding_text
                    self.vector_store[root] = skill_json
        
        # index embedding_texts
        no_embedding_obj = {key:value for key, value in self.vector_store.items() if "embedding" not in value}
        if len(no_embedding_obj) > 0:
            no_embedding_texts = []
            sorted_keys = sorted(no_embedding_obj)
            for key in sorted_keys:
                no_embedding_texts.append(no_embedding_obj[key]["embedding_text"])

            embeddings = self.embedding_model.embed_documents(no_embedding_texts)
            for i, key in enumerate(sorted_keys):
                self.vector_store[key]["embedding"] = embeddings[i]
        
        self.sorted_keys = sorted(self.vector_store)
        embeddings = []
        for key in self.sorted_keys:
            embeddings.append(self.vector_store[key]["embedding"])
        self.embeddings = np.array(embeddings)
        
    def search(self, query: str, top_k: int = 3, threshold=0.8) -> List[dict]:
        key = (query, top_k, threshold)
        if key in self.query_cache:
            return self.query_cache[key]

        self.update_index()

        query_embedding = self.embedding_model.embed_query(query)
        query_embedding = np.array(query_embedding)
        indexes, scores = cosine_similarity(docs_matrix=self.embeddings, query_vec=query_embedding, k=top_k)
        results = []
        for i, index in enumerate(indexes):
            if scores[i] < threshold:
                break
            result = self.vector_store[self.sorted_keys[index]]
            result["score"] = scores[i]
            results.append(result)
        self.query_cache[key] = results
        return result

