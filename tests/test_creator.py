import sys
sys.path.append("..")
import creator
from rich.markdown import Markdown
from rich import print
import json


def test_create_from_user_request():
    skill = creator.create(request="filter how many prime numbers are in 201")
    # creator.save(skill=skill)
    print(Markdown(repr(skill)))


def test_create_from_messages():
    messages = [
        {
            "role": "user",
            "content": "write a program to list all the python functions and their docstrings in a directory"
        },
        {
            "role": "assistant",
            "content": "Sure, I can help with that. Here's the plan:\n\n1. First, we need to get a list of all Python files in the specified directory. We can do this by using the `os` and `glob` modules in Python.\n2. Then, for each Python file, we will parse the file to find all function definitions. We can do this by using the `ast` module in Python, which can parse Python source code into an abstract syntax tree (AST).\n3. For each function definition, we will extract the function's name and its docstring. The `ast` module can also help us with this.\n4. Finally, we will print out the function names and their docstrings.\n\nLet's start with step 1: getting a list of all Python files in the specified directory.",
            "function_call": {
                "name": "run_code",
                "arguments": "{\n  \"language\": \"python\",\n  \"code\": \"import os\\nimport glob\\n\\n# Get the current working directory\\ncwd = os.getcwd()\\n\\n# Get a list of all Python files in the directory\\npython_files = glob.glob(os.path.join(cwd, '*.py'))\\n\\npython_files\"\n}",
            }
        }
    ]
    skill = creator.create(messages=messages)
    creator.save(skill=skill)


def test_create_from_messages_json_path():
    skill = creator.create(messages_json_path="./messages_example.json")
    creator.save(skill=skill)


def test_create_from_code_file_content():
    code_file_content = """
from rich import print as rich_print
from rich.markdown import Markdown
from rich.rule import Rule

def display_markdown_message(message):
    '''Display markdown message. Works with multiline strings with lots of indentation.
    Will automatically make single line > tags beautiful.
    '''

    for line in message.split("\n"):
        line = line.strip()
        if line == "":
            print("")
        elif line == "---":
            rich_print(Rule(style="white"))
        else:
            rich_print(Markdown(line))

    if "\n" not in message and message.startswith(">"):
        # Aesthetic choice. For these tags, they need a space below them
        print("")
"""
    skill = creator.create(file_content=code_file_content)
    creator.save(skill=skill)

def test_create_from_doc_file_content():
    api_doc_file_content = """
# Installation
```bash
pip install -U open-creator
```

# Usage
```python
import creator
```
## 1. Create a Skill
- [x] 1.1 from a request
- [x] 1.2 from a conversation history (openai messages format)
- [x] 1.3 from a skill json file
- [x] 1.4 from a messages_json_path
- [x] 1.5 from code file

1.1 Create a skill from a request
```python
request = "help me write a script that can extracts a specified section from a PDF file and saves it as a new PDF"
skill = creator.create(request=request)
```
"""
    skill = creator.create(file_content=api_doc_file_content)
    creator.save(skill=skill)

def test_create_from_file_path():
    skill = creator.create(file_path="../creator/utils/ask_human.py")
    creator.save(skill=skill)

def test_create_from_huggingface():
    skill = creator.create(
        huggingface_repo_id="Sayoyo/skill-library", huggingface_skill_path="extract_pdf_section"
    )
    if skill is not None:
        creator.save(skill=skill)


if __name__ == "__main__":
    test_create_from_huggingface()
    # test_create_from_messages_json_path()
    # test_create_from_file_content()
