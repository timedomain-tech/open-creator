from typing import Any, Callable

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema.messages import AIMessageChunk

from .buffer_manager import buffer_output_manager
from .rich_manager import rich_output_manager
from .file_manager import file_output_manager


class BaseStreamingHandler(StreamingStdOutCallbackHandler):
    def __init__(self, output_manager: Callable):
        self.output_manager = output_manager

    def on_chain_start(self, **kwargs: Any) -> None:
        agent_name = kwargs.get("agent_name")
        self.output_manager.add(agent_name)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        chunk = kwargs.get("chunk", None)
        if chunk is None:
            chunk = AIMessageChunk(content=token, additional_kwargs=kwargs)
        self.output_manager.update(chunk)

    def on_tool_end(self, **kwargs: Any) -> Any:
        chunk = kwargs.get("chunk", None)
        if chunk is not None:
            self.output_manager.update_tool_result(chunk)

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        self.output_manager.finish(err=error)

    def on_chain_end(self, **kwargs: Any) -> None:
        message = kwargs.get("message", None)
        self.output_manager.finish(message=message)


class OutputBufferStreamingHandler(BaseStreamingHandler):
    def __init__(self):
        super().__init__(buffer_output_manager)


class RichTerminalStreamingHandler(BaseStreamingHandler):
    def __init__(self):
        super().__init__(rich_output_manager)


class FileLoggerStreamingHandler(BaseStreamingHandler):
    def __init__(self):
        super().__init__(file_output_manager)
