# from .creator import Creator
# import sys
import langchain
from langchain.cache import SQLiteCache
import os

# support llm cache
cache_path = os.path.expanduser('~') + "/.cache/open_creator/llm_cache"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)

langchain.llm_cache = SQLiteCache(database_path=f"{cache_path}/.langchain.db")


# to save a step, we can directly `import creator` and use its interface
# sys.modules["creator"] = Creator()

#   ___                      ____                _             
#  / _ \ _ __   ___ _ __    / ___|_ __ ___  __ _| |_ ___  _ __ 
# | | | | '_ \ / _ \ '_ \  | |   | '__/ _ \/ _` | __/ _ \| '__|
# | |_| | |_) |  __/ | | | | |___| | |  __/ (_| | || (_) | |   
#  \___/| .__/ \___|_| |_|  \____|_|  \___|\__,_|\__\___/|_|   
#       |_|                                                   