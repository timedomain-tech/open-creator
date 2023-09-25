from langchain.cache import SQLiteCache
import langchain
from pydantic import BaseModel
from dotenv import load_dotenv, find_dotenv
from creator.code_interpreter import CodeInterpreter
import os


load_dotenv(find_dotenv())


_local_skill_library_path = os.environ.get("LOCAL_SKILL_LIBRARY_PATH", os.path.expanduser("~") + "/.cache/open_creator/skill_library")
_remote_skill_library_path = os.environ.get("REMOTE_SKILL_LIBRARY_PATH", os.path.expanduser("~") + "/.cache/open_creator/remote")
_local_skill_library_vectordb_path = os.environ.get("LOCAL_SKILL_LIBRARY_VECTORDB_PATH", os.path.expanduser("~") + "/.cache/open_creator/vectordb/")
_prompt_cache_history_path = os.environ.get("PROMPT_CACHE_HISTORY_PATH", os.path.expanduser("~") + "/.cache/open_creator/prompt_cache/history.txt")
_skill_extract_agent_cache_path = os.environ.get("SKILL_EXTRACT_AGENT_CACHE_PATH", os.path.expanduser("~") + "/.cache/open_creator/llm_cache")
_official_skill_library_path = os.environ.get("OFFICIAL_SKILL_LIBRARY_PATH", "timedomain/skill-library")
_official_skill_library_template_path = os.environ.get("OFFICIAL_SKILL_LIBRARY_PATH", "timedomain/skill-library-template")
_agent_model = os.environ.get("AGENT_MODEL", "gpt-3.5-turbo-16k-0613")

if not os.path.exists(_skill_extract_agent_cache_path):
    os.makedirs(_skill_extract_agent_cache_path)

if not os.path.exists(_local_skill_library_path):
    os.makedirs(_local_skill_library_path)

if not os.path.exists(_local_skill_library_vectordb_path):
    os.makedirs(_local_skill_library_vectordb_path)

if not os.path.exists(_prompt_cache_history_path):
    os.makedirs(os.path.dirname(_prompt_cache_history_path))
    open(_prompt_cache_history_path, 'a').close()


build_in_skill_config = {

}


class LibraryConfig(BaseModel):
    local_skill_library_path: str = _local_skill_library_path
    remote_skill_library_path: str = _remote_skill_library_path
    local_skill_library_vectordb_path: str = _local_skill_library_vectordb_path
    prompt_cache_history_path: str = _prompt_cache_history_path
    skill_extract_agent_cache_path: str = _skill_extract_agent_cache_path
    agent_model: str = _agent_model
    official_skill_library_path: str = _official_skill_library_path
    official_skill_library_template_path: str = _official_skill_library_template_path
    build_in_skill_config: dict = build_in_skill_config
    code_interpreter: CodeInterpreter = CodeInterpreter()


config = LibraryConfig()
langchain.llm_cache = SQLiteCache(database_path=f"{config.skill_extract_agent_cache_path}/.langchain.db")
