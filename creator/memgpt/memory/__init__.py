from .core_memory import CoreMemory
from .recall_memory import RecallMemory
from .archival_memory import ArchivalMemory
from .builder import build_memory
from ..time_utils import get_local_time


class MemoryManager:

    def __init__(self, memory_config):
        self.chat_message_history = build_memory(memory_path=memory_config.MEMORY_PATH, session_id=memory_config.session_id)
        self.session_id = self.chat_message_history.session_id
        self.core_memory = CoreMemory(
            persona=memory_config.PERSONA,
            human=memory_config.HUMAN,
            persona_char_limit=memory_config.CORE_MEMORY_PERSONA_CHAR_LIMIT,
            human_char_limit=memory_config.CORE_MEMORY_HUMAN_CHAR_LIMIT,
        )
        self.recall_memory = RecallMemory(message_database=self.chat_message_history, use_vector_search=memory_config.USE_VECTOR_SEARCH)
        self.archival_memory = ArchivalMemory(message_database=self.chat_message_history, use_vector_search=memory_config.USE_VECTOR_SEARCH)
        self.page_size = self.recall_memory.page_size = self.archival_memory.page_size = memory_config.PAGE_SIZE

    @property
    def human(self):
        return self.core_memory.human

    @property
    def persona(self):
        return self.core_memory.persona

    @property
    def memory_edit_timestamp(self):
        messages = self.chat_message_history.messages
        now = get_local_time()
        if messages:
            return messages[-1].additional_kwargs.get("created_at", now)
        return now

    @property
    def recall_memory_count(self):
        messages = self.chat_message_history.messages
        return len([m for m in messages if m.type != "archival"])

    @property
    def archival_memory_count(self):
        messages = self.chat_message_history.messages
        return len([m for m in messages if m.type == "archival"])

    @property
    def is_new_session(self):
        return len(self.chat_message_history.messages) == 0

    @property
    def messages(self):
        messages = self.chat_message_history.messages
        # filter archival and subagent
        messages = [m for m in messages if m.type != "archival" and "subagent" not in m.additional_kwargs]
        return messages

    async def add_user_message(self, message):
        self.chat_message_history.add_user_message(message)

    async def add_message(self, message):
        self.chat_message_history.add_message(message)

    def get_memory(self, memory_type):
        memory = getattr(self, f"{memory_type}_memory", None)
        assert memory is not None, f"Memory type {memory_type} not found"
        return memory

    async def add(self, memory_type, message, name=None):
        return await self.get_memory(memory_type=memory_type).add(message, name=name)

    async def modify(self, memory_type, old_content, new_content, name=None):
        return await self.get_memory(memory_type=memory_type).modify(old_content=old_content, new_content=new_content, name=name)

    async def search(self, memory_type, query, page, start_date=None, end_date=None):
        return await self.get_memory(memory_type=memory_type).search(query=query, page=page, start_date=start_date, end_date=end_date)
