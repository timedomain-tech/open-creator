import sys 
sys.path.append("../")

from creator.agents.extractors import messages2skill_agent, file2skill_agent
import getpass
import os
import platform
import time
import json


def test_messages2skill_agent():
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
    begin = time.time()

    extracted_skill = messages2skill_agent.run({
        "messages": messages,
        "username": getpass.getuser(),
        "current_working_directory": os.getcwd(),
        "operating_system": platform.system(),
        "verbose": True,
    })

    print("first run it costs {} seconds".format(time.time() - begin))

    print(extracted_skill)


def test_file2skill_agent():

    with open("../creator/callbacks/display.py") as f:
        file_content = f.read()

    begin = time.time()

    extracted_skill = file2skill_agent.run({
        "file_content": file_content,
        "username": getpass.getuser(),
        "current_working_directory": os.getcwd(),
        "operating_system": platform.system(),
        "verbose": True,
    })

    print("first run it costs {} seconds".format(time.time() - begin))

    print(json.dumps(extracted_skill, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_file2skill_agent()

