import uuid

from langchain.memory.chat_message_histories import SQLChatMessageHistory

from .converter import MessageConverter


def build_memory(memory_path:str, session_id=None):
    if session_id is None:
        session_id = str(uuid.uuid4())
    return SQLChatMessageHistory(
        session_id=session_id,
        connection_string=f"sqlite:///{memory_path}/.langchain.db",
        custom_message_converter=MessageConverter()
    )
