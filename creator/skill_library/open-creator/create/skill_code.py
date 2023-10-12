from creator.core import creator
from creator.core.skill import CodeSkill
from typing import Optional, List


def create(
    request: Optional[str] = None,
    messages: Optional[List[dict]] = None,
    messages_json_path: Optional[str] = None,
    skill_path: Optional[str] = None,
    skill_json_path: Optional[str] = None,
    file_content: Optional[str] = None,
    file_path: Optional[str] = None,
    huggingface_repo_id: Optional[str] = None,
    huggingface_skill_path: Optional[str] = None,
) -> CodeSkill:
    """Create a skill from various sources.

    Args:
        request (Optional[str], optional): Request string. Defaults to None.
        messages (Optional[List[dict]], optional): Messages in list of dict format. Defaults to None.
        messages_json_path (Optional[str], optional): Path to messages JSON file. Defaults to None.
        skill_path (Optional[str], optional): Path to skill directory. Defaults to None.
        skill_json_path (Optional[str], optional): Path to skill JSON file. Defaults to None.
        file_content (Optional[str], optional): File content. Defaults to None.
        file_path (Optional[str], optional): Path to file. Defaults to None.
        huggingface_repo_id (Optional[str], optional): Huggingface repo ID. Defaults to None.
        huggingface_skill_path (Optional[str], optional): Huggingface skill path. Defaults to None.

    Returns:
        CodeSkill: Created skill
    Example:
        >>> skill = create(request="filter how many prime numbers are in 201")
        >>> skill = create(messages=[{"role": "user","content": "write a program to list all the python functions and their docstrings in a directory"},{"role": "assistant","content": "Sure, I can help with that. Here's the plan:\n\n1. First, we need to get a list of all Python files in the specified directory. We can do this by using the `os` and `glob` modules in Python.\n2. Then, for each Python file, we will parse the file to find all function definitions. We can do this by using the `ast` module in Python, which can parse Python source code into an abstract syntax tree (AST).\n3. For each function definition, we will extract the function's name and its docstring. The `ast` module can also help us with this.\n4. Finally, we will print out the function names and their docstrings.\n\nLet's start with step 1: getting a list of all Python files in the specified directory.","function_call": {"name": "run_code","arguments": "{\n  \"language\": \"python\",\n  \"code\": \"import os\\nimport glob\\n\\n# Get the current working directory\\ncwd = os.getcwd()\\n\\n# Get a list of all Python files in the directory\\npython_files = glob.glob(os.path.join(cwd, '*.py'))\\n\\npython_files\"\n}"}}])
        >>> skill = create(messages_json_path="./messages_example.json")
        >>> skill = create(file_path="../creator/utils/ask_human.py")
        >>> skill = create(huggingface_repo_id="Sayoyo/skill-library", huggingface_skill_path="extract_pdf_section")
        >>> skill = create(skill_json_path=os.path.expanduser("~") + "/.cache/open_creator/skill_library/create/skill.json")
    """
    if request is not None:
        skill = creator.create(request=request)
    elif messages is not None:
        skill = creator.create(messages=messages)
    elif messages_json_path is not None:
        skill = creator.create(messages_json_path=messages_json_path)
    elif skill_path is not None:
        skill = creator.create(skill_path=skill_path)
    elif skill_json_path is not None:
        skill = creator.create(skill_json_path=skill_json_path)
    elif file_content is not None:
        skill = creator.create(file_content=file_content)
    elif file_path is not None:
        skill = creator.create(file_path=file_path)
    elif huggingface_repo_id is not None and huggingface_skill_path is not None:
        skill = creator.create(
            huggingface_repo_id=huggingface_repo_id, huggingface_skill_path=huggingface_skill_path
        )
    else:
        raise ValueError("At least one argument must be provided.")

    return skill
