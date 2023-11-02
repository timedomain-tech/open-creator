from typing import Any
import datetime

from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage, FunctionMessage
from langchain.memory.chat_message_histories.sql import BaseMessageConverter

from ..time_utils import get_local_time
from .schema import MemoryMessage


class ArchivalMessage(BaseMessage):
    type: str = "archival"


class MessageConverter(BaseMessageConverter):

    def from_sql_model(self, sql_message: Any) -> BaseMessage:
        created_at = sql_message.created_at.strftime("%Y-%m-%d %I:%M:%S %p %Z%z")
        sql_message.additional_kwargs.update({"created_at": created_at})
        if sql_message.type == 'human':
            return HumanMessage(
                content=sql_message.content,
                additional_kwargs=sql_message.additional_kwargs
            )
        elif "ai" in sql_message.type.lower():
            return AIMessage(
                content=sql_message.content,
                additional_kwargs=sql_message.additional_kwargs
            )
        elif "system" in sql_message.type.lower():
            return SystemMessage(
                content=sql_message.content,
                additional_kwargs=sql_message.additional_kwargs
            )
        elif "function" in sql_message.type.lower():
            return FunctionMessage(
                content=sql_message.content,
                name=sql_message.additional_kwargs.get("name", ""),
                additional_kwargs=sql_message.additional_kwargs
            )
        elif "archival" in sql_message.type.lower():
            return ArchivalMessage(
                content=sql_message.content,
                additional_kwargs=sql_message.additional_kwargs
            )
        else:
            raise ValueError(f'Unknown message type: {sql_message.type}')

    def to_sql_model(self, message: BaseMessage, session_id: str) -> Any:
        now = get_local_time()
        now_datetime = datetime.datetime.strptime(now, "%Y-%m-%d %I:%M:%S %p %Z%z")
        if isinstance(message, FunctionMessage):
            message.additional_kwargs.update({"name": message.name})
        message.additional_kwargs.update({"created_at": now})
        return MemoryMessage(
            session_id=session_id,
            type=message.type,
            content=message.content,
            created_at=now_datetime,
            additional_kwargs=message.additional_kwargs
        )

    def get_sql_model_class(self) -> Any:
        return MemoryMessage
