import argparse
from creator.utils.printer import print as rich_print
from rich.markdown import Markdown
from rich.rule import Rule
import os
import subprocess
import appdirs
import json
import platform


arguments = [
    {
        "name": "create",
        "nickname": "create",
        "help_text": "Create a new skill from above various ways",
        "command": True,
        "type": str,
        "sub_arguments": [
            {
                "name": "request",
                "nickname": "r",
                "help_text": "Request string",
                "type": str,
            },
            {
                "name": "messages",
                "nickname": "m",
                "help_text": "Openai messages format",
                "type": str,
            },
            {
                "name": "skill_json_path",
                "nickname": "sp",
                "help_text": "Path to skill JSON file",
                "type": str,
            },
            {
                "name": "file_content",
                "nickname": "c",
                "help_text": "File content of API docs or code file",
                "type": str,
            },
            {
                "name": "file_path",
                "nickname": "f",
                "help_text": "Path to API docs or code file",
                "type": str,
            },
            {
                "name": "huggingface_repo_id",
                "nickname": "hf_id",
                "help_text": "Huggingface repo ID",
                "type": str,
            },
            {
                "name": "huggingface_skill_path",
                "nickname": "hf_path",
                "help_text": "Huggingface skill path",
                "type": str,
            },
            {
                "name": "save",
                "nickname": "s",
                "help_text": "Save skill after creation",
                "type": bool,
            },
        ],
    },
    {
        "name": "save",
        "nickname": "save",
        "help_text": "Save the skill",
        "type": str,
        "command": True,
        "sub_arguments": [
            {
                "name": "skill",
                "nickname": "s",
                "help_text": "Skill json object",
                "type": str,
            },
            {
                "name": "skill_json_path",
                "nickname": "sp",
                "help_text": "Path to skill JSON file",
                "type": str,
            },
            {
                "name": "huggingface_repo_id",
                "nickname": "hf_id",
                "help_text": "Huggingface repo ID",
                "type": str,
            },
        ],
    },
    {
        "name": "search",
        "nickname": "search",
        "help_text": "Search for a skill",
        "type": str,
        "command": True,
        "sub_arguments": [
            {
                "name": "query",
                "nickname": "q",
                "help_text": "Search query",
                "type": str,
            },
            {
                "name": "top_k",
                "nickname": "k",
                "help_text": "Number of results to return, default 3",
                "type": int,
                "default": 3
            },
            {
                "name": "threshold",
                "nickname": "t",
                "help_text": "Threshold for search, default 0.8",
                "type": float,
                "default": 0.8
            },
            {
                "name": "remote",
                "nickname": "r",
                "help_text": "Search from remote",
                "type": bool,
            }
        ],
    },
    {
        "name": "interactive",
        "nickname": "i",
        "help_text": "Enter interactive mode",
        "command": False,
        "type": bool,
    },
    {
        "name": "quiet",
        "nickname": "q",
        "help_text": "Quiet mode to enter interactive mode and not rich_print LOGO and help", 
        "command": False,
        "type": bool,
    },
    {
        "name": "config",
        "nickname": "config",
        "command": False,
        "help_text": "open config.yaml file in text editor",
        "type": bool,
    }
]


def cmd_client(creator):
    parser = argparse.ArgumentParser(description='Open Creator CLI')
    subparsers = parser.add_subparsers(dest='command')
    subcommand_help_texts = []
    # Add arguments
    for arg in arguments:
        if arg["command"]:
            subparser = subparsers.add_parser(arg["name"], help=arg["help_text"])
            for sub_arg in arg["sub_arguments"]:
                if sub_arg["type"] == bool:
                    subparser.add_argument(f'-{sub_arg["nickname"]}', f'--{sub_arg["name"]}', dest=sub_arg["name"], help=sub_arg["help_text"], action='store_true')
                else:
                    subparser.add_argument(f'-{sub_arg["nickname"]}', f'--{sub_arg["name"]}', dest=sub_arg["name"], help=sub_arg["help_text"], type=sub_arg["type"], default=sub_arg.get("default", None))
            subcommand_help_texts.append(subparser.format_help())
        else:
            if arg["type"] == bool:
                parser.add_argument(f'-{arg["nickname"]}', f'--{arg["name"]}', dest=arg["name"], help=arg["help_text"], action='store_true')
            else:
                parser.add_argument(f'-{arg["nickname"]}', f'--{arg["name"]}', dest=arg["name"], help=arg["help_text"], type=arg["type"], default=arg.get("default", None))
    
    custom_help_text = "\n".join(subcommand_help_texts)
    parser.usage = custom_help_text
    try:
        args = parser.parse_args()
    except Exception:
        print(custom_help_text)
        return

    if args.config:
        # this source code from https://github.com/KillianLucas/open-interpreter/blob/be38ef8ed6ce9d0b7768e2ec3f542337f3444f54/interpreter/cli/cli.py#L101
        config_path = os.path.join(appdirs.user_config_dir(), 'Open-Creator', 'config.yaml')
        config_path = os.path.join(appdirs.user_config_dir(), 'Open-Creator', 'config.yaml')
        print(f"Opening `{config_path}`...")
        # Use the default system editor to open the file
        if platform.system() == 'Windows':
            os.startfile(config_path)  # This will open the file with the default application, e.g., Notepad
        else:
            try:
                # Try using xdg-open on non-Windows platforms
                subprocess.call(['xdg-open', config_path])
            except FileNotFoundError:
                # Fallback to using 'open' on macOS if 'xdg-open' is not available
                subprocess.call(['open', config_path])

    if args.command == "create":
        skill = creator.create(
            request=args.request,
            messages=args.messages,
            skill_json_path=args.skill_json_path,
            file_content=args.file_content,
            file_path=args.file_path,
            huggingface_repo_id=args.huggingface_repo_id,
            huggingface_skill_path=args.huggingface_skill_path,
        )
        rich_print(Markdown(repr(skill)))
        if args.save:
            creator.save(skill=skill)
    
    if args.command == "save":
        skill = None
        skill = json.loads(args.skill)
        creator.save(
            skill=skill,
            skill_json_path=args.skill_json_path,
            huggingface_repo_id=args.huggingface_repo_id,
        )

    if args.command == "search":
        skills = creator.search(
            query=args.query,
            top_k=args.top_k,
            threshold=args.threshold,
            remote=args.remote,
        )
        rich_print(Rule(style="white"))
        for skill in skills:
            rich_print(Markdown(repr(skill)))
            rich_print(Rule(style="white"))

def code_client(creator, command: str):
    command = command[len('creator'):].strip()
    args_list = command.split()

    parser = argparse.ArgumentParser(description='Open Creator CLI')
    subparsers = parser.add_subparsers(dest='command')
    subcommand_help_texts = []
    # Add arguments
    for arg in arguments:
        if arg["command"]:
            subparser = subparsers.add_parser(arg["name"], help=arg["help_text"])
            for sub_arg in arg["sub_arguments"]:
                if sub_arg["type"] == bool:
                    subparser.add_argument(f'-{sub_arg["nickname"]}', f'--{sub_arg["name"]}', dest=sub_arg["name"], help=sub_arg["help_text"], action='store_true')
                else:
                    subparser.add_argument(f'-{sub_arg["nickname"]}', f'--{sub_arg["name"]}', dest=sub_arg["name"], help=sub_arg["help_text"], type=sub_arg["type"], default=sub_arg.get("default", None))
            subcommand_help_texts.append(subparser.format_help())
        else:
            if arg["type"] == bool:
                parser.add_argument(f'-{arg["nickname"]}', f'--{arg["name"]}', dest=arg["name"], help=arg["help_text"], action='store_true')
            else:
                parser.add_argument(f'-{arg["nickname"]}', f'--{arg["name"]}', dest=arg["name"], help=arg["help_text"], type=arg["type"], default=arg.get("default", None))
    
    custom_help_text = "\n".join(subcommand_help_texts)
    parser.usage = custom_help_text
    try:
        args, unknown = parser.parse_known_args(args_list)
    except Exception:
        print(custom_help_text)
        return custom_help_text

    if args.config:
        # this source code from https://github.com/KillianLucas/open-interpreter/blob/be38ef8ed6ce9d0b7768e2ec3f542337f3444f54/interpreter/cli/cli.py#L101
        config_path = os.path.join(appdirs.user_config_dir(), 'Open-Creator', 'config.yaml')
        config_path = os.path.join(appdirs.user_config_dir(), 'Open-Creator', 'config.yaml')
        print(f"Opening `{config_path}`...")
        # Use the default system editor to open the file
        if platform.system() == 'Windows':
            os.startfile(config_path)  # This will open the file with the default application, e.g., Notepad
        else:
            try:
                # Try using xdg-open on non-Windows platforms
                subprocess.call(['xdg-open', config_path])
            except FileNotFoundError:
                # Fallback to using 'open' on macOS if 'xdg-open' is not available
                subprocess.call(['open', config_path])

    if args.command == "create":
        skill = creator.create(
            request=args.request,
            messages=args.messages,
            skill_json_path=args.skill_json_path,
            file_content=args.file_content,
            file_path=args.file_path,
            huggingface_repo_id=args.huggingface_repo_id,
            huggingface_skill_path=args.huggingface_skill_path,
        )
        if args.save:
            creator.save(skill=skill)
        return repr(skill)
    
    if args.command == "save":
        skill = None
        skill = json.loads(args.skill)
        creator.save(
            skill=skill,
            skill_json_path=args.skill_json_path,
            huggingface_repo_id=args.huggingface_repo_id,
        )
        return "Successfully saved skill."

    if args.command == "search":
        skills = creator.search(
            query=args.query,
            top_k=args.top_k,
            threshold=args.threshold,
            remote=args.remote,
        )
        result = ""
        for skill in skills:
            result+=repr(skill)+"\n"
        return result

if __name__ == "__main__":
    cmd_client()

