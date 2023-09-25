from typing import Any, Dict

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from creator.callbacks.display import MessageBox
import traceback


class FunctionCallStreamingStdOut(StreamingStdOutCallbackHandler):
    message_box = None

    def on_chain_start(
        self, serialized: Dict[str, Any] = {}, inputs: Dict[str, Any] = {}, **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        self.message_box = MessageBox()
        
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if chunk is None:
            return
        try:
            self.message_box.update_from_chunk(chunk)
        except Exception:
            print(traceback.format_exc())

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        self.message_box.output = output

    def on_chain_end(self, outputs: Dict[str, Any] = {}, **kwargs: Any) -> None:
        self.message_box.end()

