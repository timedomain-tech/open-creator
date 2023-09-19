from typing import Any, Dict, List, Union
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import LLMResult
from creator.callbacks.display import MessageBox


class FunctionCallStreamingStdOut(StreamingStdOutCallbackHandler):
    message_box = MessageBox()

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        self.message_box = MessageBox()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if token == "" and chunk is not None:
            token = chunk.additional_kwargs.get('function_call', {}).get("arguments", "")
        self.message_box.update_from_chunk(chunk)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        self.message_box.end()

    def on_llm_error(
        self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Run when LLM errors."""
        self.message_box.end()

