from queue import Queue, Empty
from langchain.schema.messages import ChatMessageChunk
from .base import OutputManager


class BufferOutputManager(OutputManager):
    def __init__(self):
        self.stack_buffer:Queue = Queue()
        self.last_delta: ChatMessageChunk = None
        self.last_output: ChatMessageChunk = None
        self.agent_names:Queue = Queue()

    def add(self, agent_name: str):
        self.agent_names.put(agent_name)
        self.stack_buffer.put((None, None))

    def update(self, chunk):
        new_output = self.merge_delta(chunk)
        self.stack_buffer.put((chunk, new_output))
        self.last_delta, self.last_output = chunk, new_output

    def update_tool_result(self, chunk):
        self.last_delta, self.last_output = chunk, chunk

    def finish(self, message=None, err=None):
        if message is not None:
            self.stack_buffer.put((message, message))
        if self.last_output is not None:
            self.stack_buffer.put((self.last_delta, self.last_output))
        self.last_delta = None
        self.last_output = None
        if err is not None:
            self.stack_buffer.put((err, err))
        self.stack_buffer.put(None)

    def __iter__(self):
        while not self.agent_names.empty():
            agent_name = self.agent_names.get()
            while 1:
                try:
                    item = self.stack_buffer.get()
                except Empty:
                    item = None
                if item is None:
                    break
                yield agent_name, item

    def merge_delta(self, chunk: ChatMessageChunk):
        new_output = chunk
        if self.last_output is not None:
            new_output = self.last_output + chunk
        return new_output


buffer_output_manager = BufferOutputManager()
