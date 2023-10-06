import sys
sys.path.append("..")
import creator
from rich.markdown import Markdown
from creator.utils.printer import print
import os


def test_create_from_user_request():
    skill = creator.create(request="filter how many prime numbers are in 201")
    creator.save(skill=skill)
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
    print(Markdown(repr(skill)))


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

def test_create_from_skill_json_path():
    skill_json_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library/create/skill.json"
    skill = creator.create(skill_json_path=skill_json_path)
    print(Markdown(repr(skill)))

def test_save_to_skill_path():
    skill_json_path = skill_json_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library/ask_run_code_confirm/skill.json"
    skill = creator.create(skill_json_path=skill_json_path)
    print(Markdown(repr(skill)))
    skill_path = "../build-in-skill_library/ask_run_code_confirm"
    print(skill.skill_metadata)
    creator.save(skill=skill, skill_path=skill_path)

def test_save_to_hub():
    skill_json_path = skill_json_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library/ask_run_code_confirm/skill.json"
    skill = creator.create(skill_json_path=skill_json_path)
    print(Markdown(repr(skill)))
    creator.save(skill=skill, huggingface_repo_id="ChuxiJ/skill_library")

def test_local_search():
    skills = creator.search("I want to extract some pages from a pdf")
    for skill in skills:
        print(Markdown(repr(skill)))

def test_run_skill():
    skill = creator.search("pdf extract section")[0]
    input_args = {
        "pdf_path": "creator.pdf",
        "start_page": 3,
        "end_page": 8,
        "output_path": "creator3-8.pdf"
    }
    print(Markdown(repr(skill)))
    resp = skill.run(input_args)
    print(resp)

def test_run_skill_with_request():
    skill = creator.search("pdf extract section")[0]
    input_args = "extract 3-8 page form creator.pdf and save it as creator3-8.pdf"
    print(Markdown(repr(skill)))
    resp = skill.run(input_args)
    print(resp)

def test_create_from_file_content2():
    doc_content = """
# Installation
\`\`\`shell
pip install langchain openai 
\`\`\`
The chat model will respond with a message.
\`\`\`python
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.chat_models import ChatOpenAI

chat = ChatOpenAI()
chat([HumanMessage(content="Translate this sentence from English to French: I love programming.")])
\`\`\`
you will get AIMessage(content="J'adore la programmation.", additional_kwargs={}, example=False)

We can then wrap our chat model in a ConversationChain, which has built-in memory for remembering past user inputs and model outputs.

\`\`\`python
from langchain.chains import ConversationChain  
  
conversation = ConversationChain(llm=chat)  
conversation.run("Translate this sentence from English to French: I love programming.")
\`\`\`
output: 'Je adore la programmation.'

conversation.run("Translate it to German.")

output: 'Ich liebe Programmieren.'
"""
    skill = creator.create(file_content=doc_content)
    print(Markdown(repr(skill)))
    creator.save(skill, skill_path="./")


def test_run_skill_with_request2():
    skill = creator.create(request="filter how many prime numbers are in 201")
    creator.save(skill=skill)
    print(Markdown(repr(skill)))
    result = skill.run("try n is 68")
    print(result)

if __name__ == "__main__":
    test_create_from_file_content2()
    # test_local_search()

