from typing import Any, Dict

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .buffer_menager import output_buffer_manager
from loguru import logger


class FunctionCallStreamingStdOut(StreamingStdOutCallbackHandler):

    def on_chain_start(
        self, serialized: Dict[str, Any] = {}, inputs: Dict[str, Any] = {}, **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
        agent_name = kwargs.get("agent_name")
        output_buffer_manager.add(agent_name)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            output_buffer_manager.update(chunk)

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        if output is not None:
            output_buffer_manager.tool_result = output

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        output_buffer_manager.finish()
        logger.debug("Finish on_chain_error")

    def on_chain_end(self, outputs: Dict[str, Any] = {}, **kwargs: Any) -> None:
        """Run when chain finishes running."""
        output_buffer_manager.finish()
        logger.debug("Finish on_chain_end")

    def end(self):
        """Run when chain finishes running."""
        output_buffer_manager.finish()
        logger.debug("Finish end")
