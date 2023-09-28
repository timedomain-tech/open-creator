import os
from typing import Union, List, Optional
from creator.agents import skill_extractor_agent, code_interpreter_agent
from creator.schema.skill import CodeSkill, BaseSkill, BaseSkillMetadata
from creator.config.library import config
from creator.utils import (
    generate_install_command,
    generate_language_suffix,
    generate_skill_doc
)

from creator.hub.huggingface import hf_pull, hf_repo_update, hf_push
from creator.retrivever.base import BaseVectorStore
from creator.client import cmd_client

from creator.utils.printer import print
from rich.markdown import Markdown

import getpass
import platform
import json
from functools import wraps


def validate_create_params(func):
    """
    Decorator function to validate parameters.
    It checks if the provided paths exist and if the correct number of parameters are provided.
    """
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        kwargs = {**dict(zip(arg_names, args)), **kwargs}

        # List of paths to verify
        path_to_verify = ["skill_path", "skill_json_path", "messages_json_path", "file_path"]
        # Check if the provided paths exist
        for path in path_to_verify:
            if kwargs.get(path) and not os.path.exists(kwargs.get(path)):
                print(f"[red]Warning:[/red] [yellow]The path {kwargs.get(path)} does not exist.[/yellow]")
                return None

        # List of parameters to check for huggingface
        params = ["huggingface_repo_id", "huggingface_skill_path"]
        # Check if both huggingface parameters are provided
        huggingface_provided_params = [param for param in params if kwargs.get(param)]
        if len(huggingface_provided_params) == 1:
            print("[red]Warning[/red]: [yellow]Please provide both parameters: huggingface_repo_id and huggingface_skill_path.[/yellow]")
            return None

        # List of parameters to check
        params = ["messages", "request", "skill_path", "skill_json_path", "messages_json_path", "file_content", "file_path"]
        # Check if only one parameter is provided
        provided_params = [param for param in params if kwargs.get(param)]

        if len(provided_params) != 1 and len(huggingface_provided_params) ==0:
            print(f"[red]Warning[/red]: [yellow]Only one parameter can be provided. You provided: {provided_params}[/yellow]")
            return None
        
        # Return the original function with the validated parameters
        return func(cls, *args, **kwargs)
    return wrapper


def validate_save_params(func):
    """
    Decorator function to validate parameters.
    It checks if the provided paths exist and if the correct number of parameters are provided.
    """
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        skill = kwargs.get("skill", None)
        if skill is None:
            print("[red]Warning[/red]: [yellow]Please provide a skill object.[/yellow]")
            return None

        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        kwargs = {**dict(zip(arg_names, args)), **kwargs}

        params = ["huggingface_repo_id", "skill_path"]
        # Check if only one parameter is provided
        provided_params = [param for param in params if kwargs.get(param)]
        if len(provided_params) == 0:
            skill = kwargs.get("skill")
            kwargs["skill_path"] = os.path.join(config.local_skill_library_path, skill.skill_name)
        return func(cls, *args, **kwargs)

    return wrapper


class Creator:
    """
    A class responsible for creating, saving and searching skills. 
    Provides functionalities for generating skills from various sources.
    """
    vectordb = None

    @classmethod
    def _create_from_messages(cls, messages) -> CodeSkill:
        """Generate skill from messages."""
        skill_json = skill_extractor_agent.run({
            "messages": messages,
            "username": getpass.getuser(),
            "current_working_directory": os.getcwd(),
            "operating_system": platform.system(),
            "verbose": True,
        })
        skill = CodeSkill(**skill_json)
        if skill.skill_metadata is None:
            skill.skill_metadata = BaseSkillMetadata()
        return skill

    @classmethod
    def _create_from_skill_json_path(cls, skill_json_path) -> CodeSkill:
        """Load skill from a given path."""
        with open(skill_json_path, mode="r") as f:
            skill = CodeSkill.model_validate_json(f.read())
            skill.skill_metadata.created_at = skill.skill_metadata.created_at.strftime("%Y-%m-%d %H:%M:%S")
            skill.skill_metadata.updated_at = skill.skill_metadata.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        return skill

    @classmethod
    @validate_create_params
    def create(
        cls,
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
        """Main method to create a new skill."""
        
        if skill_path:
            skill_json_path = os.path.join(skill_path, "skill.json")
            return cls._create_from_skill_json_path(skill_json_path)

        if skill_json_path:
            return cls._create_from_skill_json_path(skill_json_path)
        
        if request:
            messages = code_interpreter_agent.run({
                "messages": [{
                    "role": "user",
                    "content": request
                }],
                "username": getpass.getuser(),
                "current_working_directory": os.getcwd(),
                "operating_system": platform.system(),
                "verbose": True,
            })
        
        if messages_json_path:
            with open(messages_json_path) as f:
                messages = json.load(f)
        
        if file_path:
            with open(file_path) as f:
                file_content = "# file name: " + os.path.basename(file_path) + "\n" + f.read()
            return cls._create_from_messages(messages)

        if file_content:
            messages = [{
                "role": "user",
                "content": file_content
            }]

        if messages:
            return cls._create_from_messages(messages)
        
        if huggingface_repo_id and huggingface_skill_path:
            # huggingface_skill_path pattern username/skill_name_{version}, the version is optional and default to 1.0.0
            save_path = os.path.join(config.remote_skill_library_path, huggingface_repo_id, huggingface_skill_path)
            skill = hf_pull(repo_id=huggingface_repo_id, huggingface_skill_path=huggingface_skill_path, save_path=save_path)
            cls.save(skill=skill, skill_path=save_path)
            return skill

        # Raise an error if none of the above conditions are met
        print(Markdown("> Please provide one of the following parameters: messages, request, skill_path, messages_json_path, file_content, or file_path."))

    @classmethod
    @validate_save_params
    def save(
        cls,
        skill: Union[BaseSkill, CodeSkill],
        skill_path: Optional[str] = None,
        huggingface_repo_id: Optional[str] = None,
    ) -> None:
        """Save the skill in various formats."""
        if skill_path is not None and not os.path.exists(skill_path):
            os.makedirs(skill_path, exist_ok=True)
        remote_skill_path = None
        if huggingface_repo_id:
            local_dir = os.path.join(config.remote_skill_library_path, huggingface_repo_id)
            hf_repo_update(huggingface_repo_id, local_dir)
            remote_skill_path = os.path.join(local_dir, skill.skill_name)
            skill_path = os.path.join(config.local_skill_library_path, skill.skill_name)
        
        if skill_path:
            os.makedirs(os.path.dirname(skill_path), exist_ok=True)
            # save json file
            with open(os.path.join(skill_path, "skill.json"), "w") as f:
                json.dump(skill.model_dump(), f, ensure_ascii=False, indent=4)
            
            # save function call
            with open(os.path.join(skill_path, "function_call.json"), "w") as f:
                json.dump(skill.to_function_call(), f, ensure_ascii=False, indent=4)
            
            # save dependencies
            command_str = ""
            if skill.skill_dependencies:
                command_str = generate_install_command(skill.skill_program_language, skill.skill_dependencies)
                with open(os.path.join(skill_path, "install_dependencies.sh"), "w") as f:
                    f.write(command_str)
            
            # save code
            if skill.skill_program_language:
                language_suffix = generate_language_suffix(skill.skill_program_language)
                with open(os.path.join(skill_path, "skill_code" + language_suffix), "w") as f:
                    f.write(skill.skill_code)

            # save conversation history
            if skill.conversation_history:
                with open(os.path.join(skill_path, "conversation_history.json"), "w") as f:
                    f.write(json.dumps(skill.conversation_history, ensure_ascii=False, indent=4))

            # skill description
            doc = generate_skill_doc(skill)
            with open(os.path.join(skill_path, "skill_doc.md"), "w") as f:
                f.write(doc)

            # embedding_text
            embedding_text = "{skill.skill_name}\n{skill.skill_description}\n{skill.skill_usage_example}\n{skill.skill_tags}".format(skill=skill)
            with open(os.path.join(skill_path, "embedding_text.txt"), "w") as f:
                f.write(embedding_text)
            
            # save test code
            if skill.test_summary:
                with open(os.path.join(skill_path, "test_summary.json"), "w") as f:
                    json.dump(skill.test_summary, f, ensure_ascii=False, indent=4)

            if huggingface_repo_id:
                # cp to local path
                os.system(command=f"cp -r {skill_path} {remote_skill_path}")
                hf_push(remote_skill_path)

        print(Markdown(f"> saved to {skill_path}"))

    @classmethod
    def search(self, query: str, top_k: int = 3, threshold=0.8, remote=False) -> List[Union[BaseSkill, CodeSkill]]:
        if remote:
            raise NotImplementedError
        if self.vectordb is None:
            print(Markdown("> loading vector database..."))
            self.vectordb = BaseVectorStore()
        skills = self.vectordb.search(query, top_k=top_k, threshold=threshold)

        return [CodeSkill(**skill) if skill.get("skill_program_language", None) else BaseSkill(**skill) for skill in skills]

    def cli(self):
        cmd_client(self)
