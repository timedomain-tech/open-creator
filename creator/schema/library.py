from pydantic import BaseModel, field_validator, model_validator
from typing import List, Optional
from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())


_local_skill_library_path = os.environ.get("LOCAL_SKILL_LIBRARY_PATH", os.path.expanduser("~") + "/.cache/open_creator/skill_library")
_remote_skill_library_path = os.environ.get("REMOTE_SKILL_LIBRARY_PATH", os.path.expanduser("~") + "/.cache/open_creator/")
_skill_extract_agent_cache_path = os.environ.get("SKILL_EXTRACT_AGENT_CACHE_PATH", os.path.expanduser("~") + "/.cache/open_creator/llm_cache")
_official_skill_library_path = os.environ.get("OFFICIAL_SKILL_LIBRARY_PATH", "timedomain/skill-library")
_skill_extract_agent_model = os.environ.get("SKILL_EXTRACT_AGENT_MODEL", "gpt-3.5-turbo-16k-0613")

if not os.path.exists(_skill_extract_agent_cache_path):
    os.makedirs(_skill_extract_agent_cache_path)

if not os.path.exists(_local_skill_library_path):
    os.makedirs(_local_skill_library_path)


build_in_skill_config = {

}


class LibraryConfig(BaseModel):
    local_skill_library_path: str = _local_skill_library_path
    remote_skill_library_path: str = _remote_skill_library_path
    skill_extract_agent_cache_path: str = _skill_extract_agent_cache_path
    skill_extract_agent_model: str = _skill_extract_agent_model
    official_skill_library_path: str = _official_skill_library_path
    build_in_skill_config: dict = build_in_skill_config


config = LibraryConfig()
