import os
from .constants import (
    DEFAULT_PERSONA,
    DEFAULT_HUMAN,
    CORE_MEMORY_HUMAN_CHAR_LIMIT,
    CORE_MEMORY_PERSONA_CHAR_LIMIT
)


class AttrDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(key)


memory_config = AttrDict({
    "memory_path": os.path.expanduser("~/.cache/open_creator/memory"),
    "system_prompt_path": os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.md"),
    "function_schema_path": os.path.join(os.path.dirname(__file__), "prompts", "function_schema.json"),
    # replace with your own session_id
    "session_id": None,
    "persona": DEFAULT_PERSONA,
    "human": DEFAULT_HUMAN,
    "persona_char_limit": CORE_MEMORY_PERSONA_CHAR_LIMIT,
    "human_char_limit": CORE_MEMORY_HUMAN_CHAR_LIMIT,
    "page_size": 5,
    "use_vector_search": True,
})
