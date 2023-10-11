from typing import Any, Dict

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from creator.callbacks.rich_message_box import RichMessageBox
import traceback
from creator.callbacks import custom_message_box as cmb_module
from typing import Any, Dict, List
from langchain.schema.messages import BaseMessage
from loguru import logger
from langchain.schema import AgentAction, AgentFinish, LLMResult

rich_messagebox = RichMessageBox()
custom_messagebox = cmb_module.get_custom_message_box()
message_boxes = [rich_messagebox, custom_messagebox]

class FunctionCallStreamingStdOut(StreamingStdOutCallbackHandler):

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        logger.debug(f"on_llm_start: {serialized}\n{prompts}\nkwargs: {kwargs}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        logger.debug(f"on_llm_end: kwargs: {kwargs}")
        

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """Run when LLM errors."""
        logger.debug(f"on_llm_error: error: {error}\nkwargs: {kwargs}")


    def on_chain_start(
        self, serialized: Dict[str, Any] = {}, inputs: Dict[str, Any] = {}, **kwargs: Any
    ) -> None:
        logger.debug(f"on_chain_start: {serialized}\ninputs: {inputs}\nkwargs: {kwargs}")
        """Run when chain starts running."""
        

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any
    ) -> None:
        """Run when LLM starts running."""
        logger.debug(f"on_chat_model_start: {serialized}\n")#kwargs: {kwargs}
        if message_boxes is not None:
            for message_box in message_boxes:
                if message_box is not None:
                    message_box.start()

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        chunk = kwargs.get("chunk", None)
        if chunk is None:
            return
        try:
            if message_boxes is not None:
                for message_box in message_boxes:
                    if message_box is not None:
                        message_box.update_from_chunk(chunk)

        except Exception:
            print(traceback.format_exc())

    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> Any:
        """Run on agent action."""
        super().on_agent_action(action, **kwargs)
        logger.debug(f"on_agent_action: kwargs: {kwargs}")

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Run on agent end."""
        logger.debug(f"on_agent_finish: kwargs: {kwargs}")


    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Run when tool starts running."""
        logger.debug(f"on_tool_start: input_str: {input_str}\nkwargs: {kwargs}")

        
    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        logger.debug(f"on_tool_end: {output}\nkwargs: {kwargs}")

        if message_boxes is not None:
            for message_box in message_boxes:
                if message_box is not None:
                    message_box.output = output
    
    

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """Run when tool errors."""
        logger.debug(f"on_tool_error: error: {error}\nkwargs: {kwargs}")


    def on_chain_end(self, outputs: Dict[str, Any] = {}, **kwargs: Any) -> None:
        logger.debug(f"on_chain_end: {outputs}\nkwargs: {kwargs}")
        if message_boxes is not None:
            for message_box in message_boxes:
                if message_box is not None:
                    message_box.end()

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        """Run when chain errors."""
        logger.debug(f"on_chain_error: error: {error}\nkwargs: {kwargs}")


    def end(self):
        logger.debug(f"end: ")
        if message_boxes is not None:
            for message_box in message_boxes:
                if message_box is not None:
                    message_box.end()