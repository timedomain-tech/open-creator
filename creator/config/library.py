from langchain.cache import SQLiteCache
import langchain
from pydantic import BaseModel
from creator.code_interpreter import CodeInterpreter
from creator.config.load_config import load_yaml_config
import os


# Load configuration from YAML
yaml_config = load_yaml_config()


# Helper function to prepend '~/' to paths if not present
def resolve_path(path):
    if not path.startswith("~"):
        return os.path.expanduser("~/" + path)
    return os.path.expanduser(path)


project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


# Fetch values from the loaded YAML config or set default values
_local_skill_library_path = resolve_path(yaml_config.get("LOCAL_SKILL_LIBRARY_PATH", ".cache/open_creator/skill_library"))
_remote_skill_library_path = resolve_path(yaml_config.get("REMOTE_SKILL_LIBRARY_PATH", ".cache/open_creator/remote"))
_local_skill_library_vectordb_path = resolve_path(yaml_config.get("LOCAL_SKILL_LIBRARY_VECTORD_PATH", ".cache/open_creator/vectordb/"))
_prompt_cache_history_path = resolve_path(yaml_config.get("PROMPT_CACHE_HISTORY_PATH", ".cache/open_creator/prompt_cache/"))
_logger_cache_path = resolve_path(yaml_config.get("LOGGER_CACHE_PATH", ".cache/open_creator/logs/"))
_skill_extract_agent_cache_path = resolve_path(yaml_config.get("SKILL_EXTRACT_AGENT_CACHE_PATH", ".cache/open_creator/llm_cache"))
_official_skill_library_path = resolve_path(yaml_config.get("OFFICIAL_SKILL_LIBRARY_PATH", "timedomain/skill-library"))
_official_skill_library_template_path = resolve_path(yaml_config.get("OFFICIAL_SKILL_LIBRARY_TEMPLATE_PATH", "timedomain/skill-library-template"))
_model = yaml_config.get("MODEL_NAME", "gpt-3.5-turbo-16k-0613")
_temperature = yaml_config.get("TEMPERATURE", 0)
_run_human_confirm = yaml_config.get("RUN_HUMAN_CONFIRM", False)
_use_stream_callback = yaml_config.get("USE_STREAM_CALLBACK", True)
_build_in_skill_library_dir = yaml_config.get("BUILD_IN_SKILL_LIBRARY_DIR", "skill_library/open-creator/")
_build_in_skill_library_dir = os.path.join(project_dir, _build_in_skill_library_dir)

# Ensure directories exist
for path in [_skill_extract_agent_cache_path, _local_skill_library_path, _local_skill_library_vectordb_path, _prompt_cache_history_path, _logger_cache_path]:
    if not os.path.exists(path):
        os.makedirs(path)

if not os.path.exists(_logger_cache_path):
    open(os.path.join(_logger_cache_path, "output.log"), 'a').close()

# Ensure the history file exists
if not os.path.exists(_prompt_cache_history_path):
    open(os.path.join(_prompt_cache_history_path, "history.txt"), 'a').close()

build_in_skill_library_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))

build_in_skill_config = {
    "create": os.path.join(_build_in_skill_library_dir, "create"),
    "save": os.path.join(_build_in_skill_library_dir, "save"),
    "search": os.path.join(_build_in_skill_library_dir, "search"),

}  # Placeholder for any built-in skill configurations


class LibraryConfig(BaseModel):
    local_skill_library_path: str = _local_skill_library_path
    remote_skill_library_path: str = _remote_skill_library_path
    local_skill_library_vectordb_path: str = _local_skill_library_vectordb_path
    prompt_cache_history_path: str = _prompt_cache_history_path
    logger_cache_path: str = _logger_cache_path
    skill_extract_agent_cache_path: str = _skill_extract_agent_cache_path
    model: str = _model
    temperature: float = _temperature
    official_skill_library_path: str = _official_skill_library_path
    official_skill_library_template_path: str = _official_skill_library_template_path
    build_in_skill_config: dict = build_in_skill_config
    run_human_confirm: bool = _run_human_confirm
    use_stream_callback: bool = _use_stream_callback
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

    use_rich: bool = True
    use_file_logger: bool = False


config = LibraryConfig()

langchain.llm_cache = SQLiteCache(database_path=f"{config.skill_extract_agent_cache_path}/.langchain.db")
