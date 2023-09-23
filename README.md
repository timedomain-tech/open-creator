<h1 align="center">◓ Open Creator</h1>

<p align="center">
    <a href="https://discord.gg/mMszyg2j">
        <img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=flat&logoColor=white"/>
    </a>
    <a href="README_JA.md"><img src="https://img.shields.io/badge/ドキュメント-日本語-white.svg" alt="JA doc"/></a>
    <a href="README_ZH.md"><img src="https://img.shields.io/badge/文档-中文版-white.svg" alt="ZH doc"/></a>
    <img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
    <br><br>
    <b>Build your costomized skill library</b><br>
    An open-source LLM tool helps create your tools<br>
</p>

<br>

`open-creator` is an innovative package designed to extract skills from existing conversations or a requirement, save them, and retrieve them when required. It offers a seamless way to consolidate and archive refined versions of codes, turning them into readily usable skill sets, thereby enhancing the power of the [open-interpreter](https://github.com/KillianLucas/open-interpreter).

# Features
- [x] **Skill Library**: Efficiently save and retrieve structured function calls.
- [x] **Reflection Agent**: Automatically structures and categorizes your function calls.
- [x] **cache Chat LLM runs by using SQLite which is stored in `~/.cache/open_creator/llm_cache/.langchain.db`**: Save time and money by reusing previous runs.
- [x] **Sreaming**: Stream your function calls
- [ ] **Community Hub**: Share and utilize skills from the wider community. Support `huggingface_hub` & `langchain_hub`

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

1.2 Create a skill from a conversation history
```python
# you can use open-interpreter to save messages to a path
import json
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
        "parsed_arguments": {
          "language": "python",
          "code": "import os\nimport glob\n\n# Get the current working directory\ncwd = os.getcwd()\n\n# Get a list of all Python files in the directory\npython_files = glob.glob(os.path.join(cwd, '*.py'))\n\npython_files"
        }
      }
    }
  ]
skill = creator.create(messages=messages)
```

1.3 Create a skill from a skill json file
```python
skill = creator.create(skill_json_path="my_skill.json")
```

1.4 Create a skill from a messages_json_path
```python
skill = creator.create(messages_json_path="example_messages/example1.json")
```

1.5* Create a skill from code file
```python
skill = creator.create(code_file_path="example_code/example1.py")
```

## 2. Save a Skill
```python
# creator.save(skill, save_path="my_skill.json") or you can use the default path
creator.save(skill) # default path is ~/Library/
```

## 3. Search skills
```python
user_request = "Extract pages 3-8 from `example.pdf` and save to `example_page3-8.pdf`"
skills = creator.search(q=user_request, top_k=3)
```

## 4. Use a skill
```python
input_args = {
    "pdf_file_path": "example.pdf",
    "begin_page": 3,
    "end_page": 8,
    "output_file_path": "example_page3-8.pdf"
}
skill(**input_args)
```

## 5. Push to hub
stay tuned
```python
creator.push(skill, hub="my_hub")
```

## 6. Pull a skill from hub
stay tuned
```python
skill = creator.pull(hub="my_hub")
```
---

# Configurations
Customize open_creator based on your needs:

- Local Repository Path `open_creator.config.skill_library_path = 'path/to/your/local/repo'`
- Hub Repository Token: `open_creator.config.user_access_token = 'xxxx'`

# Contributing
We welcome contributions from the community! Whether it's a bug fix, new feature, or a skill to add to the library, your contributions are valued. Please check our [Contributing Guidelines](./CONTRIBUTING.md) for guidelines.

## License

Open Creator is licensed under the [MIT](./LICENSE) License. You are permitted to use, copy, modify, distribute, sublicense and sell copies of the software.
<br>


# Reference
> [1] Lucas, K. (2023). open-interpreter [Software]. Available at: https://github.com/KillianLucas/open-interpreter

> [2] Qian, C., Han, C., Fung, Y. R., Qin, Y., Liu, Z., & Ji, H. (2023). CREATOR: Disentangling Abstract and Concrete Reasonings of Large Language Models through Tool Creation. arXiv preprint arXiv:2305.14318.

> [3] Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., & Anandkumar, A. (2023). Voyager: An Open-Ended Embodied Agent with Large Language Models. arXiv preprint arXiv:2305.16291.

