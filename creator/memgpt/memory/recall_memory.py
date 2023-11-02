from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.adapters.openai import convert_message_to_dict

from creator.retrivever.memory_retrivever import MemoryVectorStore

from .base import BaseMemory


class RecallMemory(BaseMemory):
    """Recall memory database (eg run on relational database)

    Recall memory here is basically just a full conversation history with the user.
    Queryable via string matching, or date matching.

    Recall Memory: The AI's capability to search through past interactions,
    effectively allowing it to 'remember' prior engagements with a user.
    """

    def __init__(self, message_database: SQLChatMessageHistory, use_vector_search: bool = True):
        self.message_database = message_database
        self.use_vector_search = use_vector_search
        if self.use_vector_search:
            self.retrivever = MemoryVectorStore()

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
        self.message_database.add_message(message)

    async def modify(self, old_content, new_content, name=None):
        raise NotImplementedError("Archival/Recall memory doesn't support modify!")

    def _filter_messages(self):
        """Utility to filter messages based on roles."""
        return [d for d in self.message_database.messages if d.type not in ['system', 'function', 'archival']]

    async def search(self, query, page, start_date=None, end_date=None):
        """Simple text-based search"""
        matches = self._filter_messages()

        filter_by_date = start_date or end_date
        if filter_by_date:
            matches = self._filter_by_date(matches, start_date, end_date)

        if query:
            if self.use_vector_search:
                texts = [d.content for d in matches]
                metadatas = [convert_message_to_dict(match) for match in matches]
                self.retrivever.index(documents=texts, metadatas=metadatas)
                matches = self.retrivever.search(query=query, top_k=len(matches))
                self.retrivever.reset()
            else:
                matches = [d for d in matches if d.content and query.lower() in d.content.lower()]
        return self._paginate_results(matches, page)
