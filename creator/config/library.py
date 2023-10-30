import os
from pydantic import BaseModel

from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache

from creator.code_interpreter import CodeInterpreter
from creator.config.load_config import load_yaml_config


# Load configuration from YAML
yaml_config = load_yaml_config()


# Helper function to prepend '~/' to paths if not present
def resolve_path(path):
    if not path.startswith("~"):
        return os.path.expanduser("~/" + path)
    return os.path.expanduser(path)


project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


# Fetch values from the loaded YAML config or set default values
_local_skill_library_path = resolve_path(yaml_config.LOCAL_SKILL_LIBRARY_PATH)
_remote_skill_library_path = resolve_path(yaml_config.REMOTE_SKILL_LIBRARY_PATH)
_vectordb_path = resolve_path(yaml_config.VECTORD_PATH)
_prompt_cache_history_path = resolve_path(yaml_config.PROMPT_CACHE_HISTORY_PATH)
_logger_cache_path = resolve_path(yaml_config.LOGGER_CACHE_PATH)
_llm_cache_path = resolve_path(yaml_config.LLM_CACHE_PATH)
_embedding_cache_path = resolve_path(yaml_config.EMBEDDING_CACHE_PATH)
yaml_config.MEMGPT_CONFIG.MEMORY_PATH = resolve_path(yaml_config.MEMGPT_CONFIG.MEMORY_PATH)

memgpt_config = yaml_config.MEMGPT_CONFIG

_official_skill_library_path = resolve_path(yaml_config.OFFICIAL_SKILL_LIBRARY_PATH)
_official_skill_library_template_path = resolve_path(yaml_config.OFFICIAL_SKILL_LIBRARY_TEMPLATE_PATH)

_model = yaml_config.MODEL_NAME
_temperature = yaml_config.TEMPERATURE
_run_human_confirm = yaml_config.RUN_HUMAN_CONFIRM
_use_stream_callback = yaml_config.USE_STREAM_CALLBACK

# Ensure directories exist
for path in [_llm_cache_path, _local_skill_library_path, _vectordb_path, _prompt_cache_history_path, _logger_cache_path, memgpt_config.MEMORY_PATH, _embedding_cache_path]:
    if not os.path.exists(path):
        os.makedirs(path)

if not os.path.exists(_logger_cache_path):
    open(os.path.join(_logger_cache_path, "output.log"), 'a').close()

# Ensure the history file exists
if not os.path.exists(_prompt_cache_history_path):
    open(os.path.join(_prompt_cache_history_path, "history.txt"), 'a').close()


class LibraryConfig(BaseModel):
    local_skill_library_path: str = _local_skill_library_path
    remote_skill_library_path: str = _remote_skill_library_path
    vectordb_path: str = _vectordb_path
    prompt_cache_history_path: str = _prompt_cache_history_path
    logger_cache_path: str = _logger_cache_path
    llm_cache_path: str = _llm_cache_path
    embedding_cache_path: str = _embedding_cache_path

    model: str = _model
    temperature: float = _temperature
    run_human_confirm: bool = _run_human_confirm
    use_stream_callback: bool = _use_stream_callback

    official_skill_library_path: str = _official_skill_library_path
    official_skill_library_template_path: str = _official_skill_library_template_path

    code_interpreter: CodeInterpreter = CodeInterpreter()

    # prompt paths
    refactor_agent_prompt_path: str = os.path.join(project_dir, "prompts", "refactor_agent_prompt.md")
    codeskill_function_schema_path: str = os.path.join(project_dir, "prompts", "codeskill_function_schema.json")
    creator_agent_prompt_path: str = os.path.join(project_dir, "prompts", "creator_agent_prompt.md")
    api_doc_path: str = os.path.join(project_dir, "prompts", "api_doc.md")
    extractor_agent_prompt_path: str = os.path.join(project_dir, "prompts", "extractor_agent_prompt.md")
    interpreter_agent_prompt_path: str = os.path.join(project_dir, "prompts", "interpreter_agent_prompt.md")
    tester_agent_prompt_path: str = os.path.join(project_dir, "prompts", "tester_agent_prompt.md")
    testsummary_function_schema_path: str = os.path.join(project_dir, "prompts", "testsummary_function_schema.json")
    tips_for_debugging_prompt_path: str = os.path.join(project_dir, "prompts", "tips_for_debugging_prompt.md")
    tips_for_testing_prompt_path: str = os.path.join(project_dir, "prompts", "tips_for_testing_prompt.md")
    tips_for_veryfy_prompt_path: str = os.path.join(project_dir, "prompts", "tips_for_veryfy_prompt.md")
    prompt_enhancer_agent_prompt_path: str = os.path.join(project_dir, "prompts", "prompt_enhancer_agent_prompt.md")
    prompt_enhancer_schema_path: str = os.path.join(project_dir, "prompts", "prompt_enhancer_schema.json")
    memgpt_system_prompt_path: str = os.path.join(project_dir, "prompts", "memgpt_system_prompt.md")
    memgpt_function_schema_path: str = os.path.join(project_dir, "prompts", "memgpt_function_schema.json")

    memgpt_config: dict = None

    use_rich: bool = True
    use_file_logger: bool = False


config = LibraryConfig()
config.memgpt_config = memgpt_config

set_llm_cache(SQLiteCache(database_path=f"{config.llm_cache_path}/.langchain.db"))
