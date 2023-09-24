import sys
sys.path.append("..")
import creator
from rich.markdown import Markdown
from rich import print
import json


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


def test_create_from_file_content():
    skill = creator.create(file_path="../creator/callbacks/display.py")
    creator.save(skill=skill)


def test_create_from_user_request():
    skill = creator.create(request="filter how many prime numbers are in 201")
    # creator.save(skill=skill)
    print(Markdown(repr(skill)))


if __name__ == "__main__":
    test_create_from_user_request()
    # test_create_from_messages_json_path()
    # test_create_from_file_content()
