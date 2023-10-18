from typing import Any

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from .buffer_manager import buffer_output_manager
from .rich_manager import rich_output_manager
from .file_manager import file_output_manager


class OutputBufferStreamingHandler(StreamingStdOutCallbackHandler):

    def on_chain_start(self, **kwargs: Any) -> None:
        """Run when chain starts running."""
        agent_name = kwargs.get("agent_name")
        buffer_output_manager.add(agent_name)

    def on_llm_new_token(self, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            buffer_output_manager.update(chunk)

    def on_tool_end(self, **kwargs: Any) -> Any:
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            buffer_output_manager.update_tool_result(chunk)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        buffer_output_manager.finish(err=error)

    def on_chain_end(self, **kwargs: Any) -> None:
        """Run when chain finishes running."""
        message = kwargs.get("message", None)
        buffer_output_manager.finish(message=message)


class RichTerminalStreamingHandler(StreamingStdOutCallbackHandler):

    def on_chain_start(self, **kwargs: Any) -> None:
        """Run when chain starts running."""
        agent_name = kwargs.get("agent_name")
        rich_output_manager.add(agent_name)

    def on_llm_new_token(self, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            rich_output_manager.update(chunk)

    def on_tool_end(self, **kwargs: Any) -> Any:
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            rich_output_manager.update_tool_result(chunk)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        rich_output_manager.finish(err=error)

    def on_chain_end(self, **kwargs: Any) -> None:
        """Run when chain finishes running."""
        message = kwargs.get("message", None)
        rich_output_manager.finish(message=message)


class FileLoggerStreamingHandler(StreamingStdOutCallbackHandler):

    def on_chain_start(self, **kwargs: Any) -> None:
        """Run when chain starts running."""
        agent_name = kwargs.get("agent_name")
        file_output_manager.add(agent_name)

    def on_llm_new_token(self, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            file_output_manager.update(chunk)

    def on_tool_end(self, **kwargs: Any) -> Any:
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            file_output_manager.update_tool_result(chunk)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        file_output_manager.finish(err=error)

    def on_chain_end(self, **kwargs: Any) -> None:
        """Run when chain finishes running."""
        message = kwargs.get("message", None)
        file_output_manager.finish(message=message)
