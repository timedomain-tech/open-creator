import argparse
from creator.core.core import Creator
from creator.agents import code_interpreter_agent
from creator.config.library import config
from creator.schema.skill import BaseSkill, CodeSkill
from creator.utils import generate_skill_doc

import inquirer
from creator.utils.printer import print
from rich.markdown import Markdown
import time
import getpass
import platform
from rich.console import Console

_LOGO_STR = """
  ___                      ____                _             
 / _ \ _ __   ___ _ __    / ___|_ __ ___  __ _| |_ ___  _ __ 
| | | | '_ \ / _ \ '_ \  | |   | '__/ _ \/ _` | __/ _ \| '__|
| |_| | |_) |  __/ | | | | |___| | |  __/ (_| | || (_) | |   
 \___/| .__/ \___|_| |_|  \____|_|  \___|\__,_|\__\___/|_|   
      |_|                                                   
"""

_HELP_STR = """
# Entering Help Commands

- `%create`: Create a new skill from above conversation history
    - `-s` or `--save`: Save skill after creation

- `%save`: Save the skill
    - `-sp` or `--skill_path`: Path to skill JSON file
    - `-hf` or `--huggingface`: Huggingface repo ID

- `%search`: Search for a skill
    - `-q` or `--query`: Search query
    - `-k` or `--top_k`: Number of results to return, default 3

- `%exit`: Exit the CLI
- `%clear`: clear current skill cache and printed messages
- `%reset`: reset all messages and cached skills
- `%undo`: undo the last request
- `%help`: Print this help message
"""



def load_skill_in_console(skill):
    doc = generate_skill_doc(skill)
    print(Markdown(doc))
    if type(skill) == CodeSkill:
        code_interpreter_agent.tool.run({"language": skill.skill_program_language, "code": skill.skill_code})


def _handle_command(messages, command, cache_skills):
    command_list = command.strip().split()
    command = command_list[0]
    params = command_list[1:]

    if command == "%exit":
        print(Markdown("> Bye!"))
        exit()
    elif command == "%help":
        print(Markdown(_HELP_STR))

    elif command.startswith("%create"):
        save = params[params.index('-s')+1] if '-s' in params else False

        skill = Creator.create(messages=messages)
        if skill is None:
            return False
        cache_skills.append(skill)
        if save:
            Creator.save(skill=skill)

    elif command == "%save":
        if len(cache_skills) == 0:
            print(Markdown("> No skill to save! Please create a skill first."))
            return False
        huggingface_repo_id = params[params.index('-hf')+1] if '-hf' in params else None
        skill_path = params[params.index('-sp')+1] if '-sp' in params else None

        choices = []
        for i, skill in enumerate(cache_skills):
            choice = "{} | {} | {} | {}".format(skill.skill_name, skill.skill_description, skill.skill_metadata.created_at, skill.skill_metadata.author)
            choices.append((choice, skill.skill_name))

        questions = [
            inquirer.Checkbox('skills', message="> Select skills to save", choices=choices),
        ]
        if not skill_path:
            questions.append(inquirer.Text('skill_path', message="> Enter your skill save path or save skill to?", default=config.local_skill_library_path))

        answers = inquirer.prompt(questions)
        skill_path = answers.get("skill_path", config.local_skill_library_path)
        selected_skills = answers.get("skills", [])
        if len(selected_skills) == 0:
            print(Markdown("> No skill to save!"))
            return False
        push_to_remote = inquirer.prompt([inquirer.Confirm("push_to_remote", message="push to remote?", default=False)])

        if push_to_remote["push_to_remote"]:
            questions = []
            if not huggingface_repo_id:
                selected_huggingface_repo_id = inquirer.prompt([inquirer.Text('huggingface_repo_id', message="> Enter your huggingface repo id")])
                huggingface_repo_id = selected_huggingface_repo_id["huggingface_repo_id"]

        for skill_name in selected_skills:
            skill = [skill for skill in cache_skills if skill.skill_name == skill_name][0]
            Creator.save(skill, skill_path, huggingface_repo_id)
            if push_to_remote:
                Creator.save(skill=skill, skill_path=skill_path, huggingface_repo_id=huggingface_repo_id)

    elif command == "%search":
        request = params[params.index('-q')+1] if '-q' in params else None
        if request is None:
            print(Markdown("> no search request Please use -q '<your search query>' "))
            return False
        top_k = params[params.index('-k')+1] if '-k' in params else None
        if top_k is None:
            skills = Creator.search(request)
        else:
            skills = Creator.search(request, top_k)
        cache_skills += skills
    else:
        print(Markdown("> Invalid command. Here is a list of available commands:"))
        print(Markdown(_HELP_STR))
        return False
    return True


def interactive():
    messages = []
    cache_skills = []
    console = Console()
    while 1:
        request = inquirer.prompt([inquirer.Text("request", message="[green] creator [/green]> ")]).get("request", "").strip()
        if request == "":
            time.sleep(0.2)
            continue

        if request.startswith("%"):
            if request.startswith("%reset"):
                console.clear()
                cache_skills = []
                messages = []
                print(Markdown("> All messages and cached skills have been reset."))
                continue

            if request.startswith("%clear"):
                console.clear()
                continue

            if request.startswith("%undo"):
                while len(messages) > 0:
                    message = messages.pop()
                    if message["role"] == "user":
                        break
                continue

            _handle_command(messages, request, cache_skills)
            continue

        messages.append({"role":"user", "content": request})
        
        messages = code_interpreter_agent.run(
            {
                "messages": messages,
                "username": getpass.getuser(),
                "current_working_directory": os.getcwd(),
                "operating_system": platform.system(),
                "verbose": True,
            }
        )
