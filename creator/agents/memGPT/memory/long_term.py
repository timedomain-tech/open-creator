import numpy as np

from creator.llm.llm_creator import create_embedding
from creator.retrivever.score_functions import cosine_similarity

from langchain.memory.chat_message_histories import SQLChatMessageHistory

from .base import BaseMemory


class RecallMemory(BaseMemory):
    """Recall memory database (eg run on relational database)

    Recall memory here is basically just a full conversation history with the user.
    Queryable via string matching, or date matching.

    Recall Memory: The AI's capability to search through past interactions,
    effectively allowing it to 'remember' prior engagements with a user.
    """

    def __init__(self, message_database: SQLChatMessageHistory, use_vector_search=False, page_size=5):
        self.message_database = message_database
        self.use_vector_search = use_vector_search
        if use_vector_search:
            self.embeddings = dict()
            self.embedding_model = create_embedding()
        self.page_size = page_size

    def __len__(self):
        return len(self.message_database.messages)

    def __repr__(self) -> str:
        # Using a dictionary to maintain counts for each message role
        role_counts = {
            'system': 0,
            'user': 0,
            'assistant': 0,
            'function': 0,
            'other': 0
        }

        for msg in self.self.message_database.messages:
            role_counts[msg.type] = role_counts.get(msg.type, 0) + 1

        memory_str = "\n".join([f"{count} {role}" for role, count in role_counts.items()])
        return f"\n### RECALL MEMORY ###\nStatistics:\n{len(self.message_database.messages)} total messages\n{memory_str}"

    async def add(self, message, name=None):
        raise NotImplementedError("Recall memory is read-only, will automatically update, and doesn't support editting or adding new memories as it's the record of your past interactions.")

    async def modify(self, old_content, new_content, name=None):
        raise NotImplementedError("Recall memory is read-only, will automatically update, and doesn't support editting or adding new memories as it's the record of your past interactions.")

    def _filter_messages(self):
        """Utility to filter messages based on roles."""
        return [d for d in self.message_database.messages if d.type not in ['system', 'function', 'archival']]

    async def _get_or_compute_embedding(self, message_str):
        """Retrieve or compute the embedding for a given string."""
        if message_str not in self.embeddings:
            self.embeddings[message_str] = self.embedding_model.embed_query(message_str)
        return self.embeddings[message_str]

    async def search(self, query, page, start_date=None, end_date=None):
        """Simple text-based search"""
        matches = self._filter_messages()

        filter_by_date = start_date or end_date
        if filter_by_date:
            matches = self._filter_by_date(matches, start_date, end_date)

        if query:
            if self.use_vector_search:
                message_pool_filtered = [d for d in matches if await self._get_or_compute_embedding(d.content)]
                query_vec = self.embedding_model.embed_query(query)
                docs_matrix = np.array([self.embeddings[d.content] for d in message_pool_filtered])
                indexes, scores = cosine_similarity(docs_matrix=docs_matrix, query_vec=query_vec, k=len(docs_matrix))
                matches = [message_pool_filtered[i] for i in indexes]
            else:
                matches = [d for d in matches if d.content and query.lower() in d.content.lower()]
        return self._paginate_results(matches, page)


class ArchivalMemory(RecallMemory):

    def __repr__(self) -> str:
        if len(self.message_database.messages) == 0:
            memory_str = "<empty>"
        else:
            memory_str = "\n".join([d.content for d in self.message_database.messages])
        return f"\n### ARCHIVAL MEMORY ###\n{memory_str}"

    def _filter_messages(self):
        """Utility to filter messages based on roles."""
        return [d for d in self.message_database.messages if d.type in ['archival']]
