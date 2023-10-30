import os
from typing import Union, List, Optional
from creator.config.library import config
from creator.utils import print
from creator.hub.huggingface import hf_pull
from creator.retrivever.skill_retrivever import SkillVectorStore

from .skill import CodeSkill, BaseSkill, BaseSkillMetadata
from .runnable import create_skill_from_messages, create_skill_from_request, create_skill_from_file_content

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

        if len(provided_params) != 1 and len(huggingface_provided_params) == 0:
            can_construct_skill = "request" in provided_params and ("file_content" in provided_params or "file_path" in provided_params)
            if not can_construct_skill:
                print(f"[red]Warning[/red]: [yellow]Only one parameter can be provided. You provided: {provided_params}[/yellow]")
                return None
        # Return the original function with the validated parameters
        return func(cls, **kwargs)
    return wrapper


def validate_save_params(func):
    """
    Decorator function to validate parameters.
    It checks if the provided paths exist and if the correct number of parameters are provided.
    """
    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        arg_names = func.__code__.co_varnames[:func.__code__.co_argcount]
        kwargs = {**dict(zip(arg_names, args)), **kwargs}
        skill_key = ""
        for k, v in kwargs.items():
            if type(v) is CodeSkill:
                skill_key = k
        kwargs["skill"] = kwargs.pop(skill_key, None)
        skill = kwargs.get("skill", None)
        if skill is None:
            print("[red]Warning[/red]: [yellow]Please provide a skill object.[/yellow]")
            return None
        skill_path = kwargs.get("skill_path", None)
        if skill_path is not None and os.path.dirname(skill_path) != skill.skill_name:
            skill_path = os.path.join(skill_path, skill.skill_name)
            kwargs["skill_path"] = skill_path
        params = ["huggingface_repo_id", "skill_path"]
        # Check if only one parameter is provided
        provided_params = [param for param in params if kwargs.get(param)]
        if len(provided_params) == 0:
            kwargs["skill_path"] = os.path.join(config.local_skill_library_path, skill.skill_name)
        return func(cls, **kwargs)

    return wrapper


class Creator:
    """
    A class responsible for creating, saving and searching skills.
    Provides functionalities for generating skills from various sources.
    """
    vectordb = None
    config = config

    @classmethod
    def _create_from_skill_json_path(cls, skill_json_path) -> CodeSkill:
        """Load skill from a given path."""
        with open(skill_json_path, mode="r", encoding="utf-8") as f:
            skill = CodeSkill.model_validate_json(f.read())
            if not isinstance(skill.skill_metadata.created_at, str):
                skill.skill_metadata.created_at = skill.skill_metadata.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if not isinstance(skill.skill_metadata.updated_at, str):
                skill.skill_metadata.updated_at = skill.skill_metadata.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        return skill

    @classmethod
    def _create_from_skill_json(cls, skill_json, save) -> CodeSkill:
        """Load skill from a given json."""
        if skill_json is not None:
            skill = CodeSkill(**skill_json)
            if skill.skill_metadata is None:
                skill.skill_metadata = BaseSkillMetadata()
            if save:
                skill.save()
            return skill
        print("> No skill was generated.", print_type="markdown")
        return None

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
        save: bool = False,
    ) -> CodeSkill:
        """Main method to create a new skill."""

        skill_json = None
        if skill_path:
            skill_json_path = os.path.join(skill_path, "skill.json")
            return cls._create_from_skill_json_path(skill_json_path)

        if skill_json_path:
            return cls._create_from_skill_json_path(skill_json_path)

        if request:
            skill_json = create_skill_from_request(request)

        if messages_json_path:
            with open(messages_json_path, encoding="utf-8") as f:
                messages = json.load(f)

        if file_path:
            with open(file_path, encoding="utf-8") as f:
                file_content = "### file name: " + os.path.basename(file_path) + "\n---" + f.read()

        if messages is not None and len(messages) > 0:
            skill_json = create_skill_from_messages(messages)

        elif file_content is not None:
            skill_json = create_skill_from_file_content(file_content)

        elif huggingface_repo_id and huggingface_skill_path:
            # huggingface_skill_path pattern username/skill_name_{version}, the version is optional and default to 1.0.0
            save_path = os.path.join(config.remote_skill_library_path, huggingface_repo_id, huggingface_skill_path)
            skill_json = hf_pull(repo_id=huggingface_repo_id, huggingface_skill_path=huggingface_skill_path, save_path=save_path)
            save = True

        return cls._create_from_skill_json(skill_json, save=save)

    @classmethod
    @validate_save_params
    def save(
        cls,
        skill: Union[BaseSkill, CodeSkill],
        skill_path: Optional[str] = None,
        huggingface_repo_id: Optional[str] = None,
    ) -> None:
        """Save the skill in various formats."""
        skill.save(skill_path=skill_path, huggingface_repo_id=huggingface_repo_id)

    @classmethod
    def search(self, query: str, top_k: int = 3, threshold=0.8, remote=False) -> List[Union[BaseSkill, CodeSkill]]:
        if remote:
            raise NotImplementedError
        if self.vectordb is None:
            print("> loading vector database...", print_type="markdown")
            self.vectordb = SkillVectorStore()
        skills = self.vectordb.search(query, top_k=top_k, threshold=threshold)

        return [CodeSkill(**skill) if skill.get("skill_program_language", None) else BaseSkill(**skill) for skill in skills]
