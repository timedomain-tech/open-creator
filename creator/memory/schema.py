from typing import Any
import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime, JSON

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain.memory.chat_message_histories.sql import BaseMessageConverter
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from creator.utils.time_utils import get_local_time

Base = declarative_base()


class ArchivalMessage(BaseMessage):
    type: str = "archival"


class MemoryMessage(Base):
    __tablename__ = 'memory_messages'

    id = Column(Integer, primary_key=True)
    session_id = Column(Text)
    type = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime)
    additional_kwargs = Column(JSON)


class MessageConverter(BaseMessageConverter):

    def from_sql_model(self, sql_message: Any) -> BaseMessage:
        created_at = sql_message.additional_kwargs.get("created_at", datetime.now())
        sql_message.additional_kwargs.update({"created_at": created_at})
        if sql_message.type == 'human':
            return HumanMessage(
                content=sql_message.content,
                additional_kwargs={"created_at": sql_message.created_at}
            )
        elif sql_message.type == 'ai':
            return AIMessage(
                content=sql_message.content,
                additional_kwargs=sql_message.additional_kwargs
            )
        elif sql_message.type == 'system':
            return SystemMessage(
                content=sql_message.content,
            )
        elif sql_message.type == 'function':
            return FunctionMessage(
                content=sql_message.content,
                name=sql_message.additional_kwargs.get("name", ""),
            )
        elif sql_message.type == "archival":
            return ArchivalMessage(
                content=sql_message.content,
            )
        else:
            raise ValueError(f'Unknown message type: {sql_message.type}')

    def to_sql_model(self, message: BaseMessage, session_id: str) -> Any:
        now = get_local_time()
        if isinstance(message, FunctionMessage):
            message.additional_kwargs.update({"name": message.name})
        message.additional_kwargs.update({"created_at": now})
        return MemoryMessage(
            session_id=session_id,
            type=message.type,
            content=message.content,
            created_at=message.additional_kwargs.get("created_at", now),
            additional_kwargs=message.additional_kwargs
        )

    def get_sql_model_class(self) -> Any:
        return MemoryMessage


class ChatMessageHistory(SQLChatMessageHistory):

    @property
    def memory_edit_timestamp(self):
        messages = self.messages()
        now = get_local_time()
        if messages:
            return messages[-1].additional_kwargs.get("created_at", now)
        return now

    @property
    def recall_memory_count(self):
        messages = self.messages()
        return len([m for m in messages if m.type != "archival"])

    @property
    def archival_memory_count(self):
        messages = self.messages()
        return len([m for m in messages if m.type == "archival"])
