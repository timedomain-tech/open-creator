from langchain.chat_models import ChatOpenAI, AzureChatOpenAI
from langchain.schema.messages import BaseMessage
from typing import List, Optional, Any, Dict, Tuple
from .tokentrim import trim


class TrimMixin:
    def _create_message_dicts(
        self, messages: List[BaseMessage], stop: Optional[List[str]]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        message_dicts, params = super()._create_message_dicts(messages, stop)
        message_dicts = trim(messages=message_dicts, model=self.model_name, max_tokens=self.max_tokens)
        return message_dicts, params


class ChatOpenAIWithTrim(TrimMixin, ChatOpenAI):
    pass


class AzureChatOpenAIWithTrim(TrimMixin, AzureChatOpenAI):
    pass
