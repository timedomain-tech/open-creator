## Skill Details:
- **Name**: create
- **Description**: Create a skill from various sources.
- **Version**: 1.0.0
- **Usage**:
```python
skill = create(request="filter how many prime numbers are in 201")
skill = create(messages=[{"role": "user","content": "write a program to list all the python functions and their docstrings in a directory"},{"role": "assistant","content": "Sure, I can help with that. Here's the plan:\n\n1. First, we need to get a list of all Python files in the specified directory. We can do this by using the `os` and `glob` modules in Python.\n2. Then, for each Python file, we will parse the file to find all function definitions. We can do this by using the `ast` module in Python, which can parse Python source code into an abstract syntax tree (AST).\n3. For each function definition, we will extract the function's name and its docstring. The `ast` module can also help us with this.\n4. Finally, we will print out the function names and their docstrings.\n\nLet's start with step 1: getting a list of all Python files in the specified directory.","function_call": {"name": "run_code","arguments": "{\n  \"language\": \"python\",\n  \"code\": \"import os\\nimport glob\\n\\n# Get the current working directory\\ncwd = os.getcwd()\\n\\n# Get a list of all Python files in the directory\\npython_files = glob.glob(os.path.join(cwd, '*.py'))\\n\\npython_files\"\n}"}}])
skill = create(messages_json_path="./messages_example.json")
skill = create(file_path="../creator/utils/ask_human.py")
skill = create(huggingface_repo_id="Sayoyo/skill-library", huggingface_skill_path="extract_pdf_section")
skill = create(skill_json_path=os.path.expanduser("~") + "/.cache/open_creator/skill_library/create/skill.json")
```
- **Parameters**:
   - **request** (string): Request string.
   - **messages** (array): Messages in list of dict format.
   - **messages_json_path** (string): Path to messages JSON file.
   - **skill_path** (string): Path to skill directory.
   - **skill_json_path** (string): Path to skill JSON file.
   - **file_content** (string): File content.
   - **file_path** (string): Path to file.
   - **huggingface_repo_id** (string): Huggingface repo ID.
   - **huggingface_skill_path** (string): Huggingface skill path.

- **Returns**:
   - **CodeSkill** (object): Created skill