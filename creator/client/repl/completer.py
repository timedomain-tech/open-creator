from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.history import FileHistory
from creator.config.library import config
import os


prompt_cache_history_path = os.path.join(config.prompt_cache_history_path + "/history.txt")
file_history = FileHistory(prompt_cache_history_path)

completer = NestedCompleter.from_nested_dict({
    'create': {
        '--save': None,
        '-s': None,
    },
    'save': {
        '--skill_path': None,
        '--huggingface': None,
        '-sp': None,
        '-hf': None,
    },
    'search': {
        '--query': None,
        '-q': None,
        '--top_k': None,
        '-k': None,
    },
    '.test()': None,
    ".run": None,
    ".auto_optimize()": None,
    '%exit': None,
    '%clear': None,
    '%reset': None,
    '%undo': None,
    '%help': None,
})
