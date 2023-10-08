from typing import Any, Dict

from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from creator.callbacks.display import RichMessageBox
import traceback
from creator.callbacks import custom_message_box as cmb_module

rich_messagebox = RichMessageBox()
message_boxes = [rich_messagebox]

class FunctionCallStreamingStdOut(StreamingStdOutCallbackHandler):

    def on_chain_start(
        self, serialized: Dict[str, Any] = {}, inputs: Dict[str, Any] = {}, **kwargs: Any
    ) -> None:
        """Run when chain starts running."""
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

            if cmb_module.custom_message_box is not None:
                cmb_module.custom_message_box.update_from_chunk(chunk)
        except Exception:
            print(traceback.format_exc())

    def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        if message_boxes is not None:
                for message_box in message_boxes:
                    if message_box is not None:
                        message_box.output = output

        if cmb_module.custom_message_box is not None:
            cmb_module.custom_message_box.output = output

    def on_chain_end(self, outputs: Dict[str, Any] = {}, **kwargs: Any) -> None:
        if message_boxes is not None:
            for message_box in message_boxes:
                if message_box is not None:
                    message_box.end()
       
        if cmb_module.custom_message_box is not None:
            cmb_module.custom_message_box.end()

    def end(self):
        if message_boxes is not None:
            for message_box in message_boxes:
                if message_box is not None:
                    message_box.end()
       
        if cmb_module.custom_message_box is not None:
            cmb_module.custom_message_box.end()