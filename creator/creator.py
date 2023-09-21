import os
from typing import Union, List
from creator.agents import skill_extractor_agent
from creator.schema.skill import CodeSkill, BaseSkill
from creator.schema.creator import CreateParams, SaveParams
from creator.schema.library import config
from creator.dependency import (
    generate_install_command,
    generate_language_suffix,
    generate_skill_doc
)
from creator.hub.huggingface import hf_pull, hf_repo_update, hf_push

from rich import print
from rich.markdown import Markdown

import getpass
import platform
import json


class Creator:
    """
    A class responsible for creating and saving skills. 
    Provides functionalities for generating skills from various sources.
    """

    @classmethod
    def _create_from_messages(self, messages) -> CodeSkill:
        """Generate skill from messages."""
        skill_json = skill_extractor_agent.run({
            "messages": messages,
            "username": getpass.getuser(),
            "current_working_directory": os.getcwd(),
            "operating_system": platform.system(),
            "verbose": True,
        })
        skill = CodeSkill(**skill_json)
        return skill

    @classmethod
    def _create_from_file_content(self, file_content) -> CodeSkill:
        """Generate skill from messages."""
        skill_json = skill_extractor_agent.run({
            "messages": {
                "role": "user",
                "content": file_content
            },
            "username": getpass.getuser(),
            "current_working_directory": os.getcwd(),
            "operating_system": platform.system(),
            "verbose": True,
        })
        skill = CodeSkill(**skill_json)
        return skill
    
    @classmethod
    def _create_from_request(self, request):
        """Placeholder for generating skill from a request."""
        raise NotImplementedError
    
    @classmethod
    def _create_from_skill_json_path(self, skill_json_path) -> CodeSkill:
        """Load skill from a given path."""
        with open(skill_json_path, mode="r") as f:
            skill = CodeSkill.model_validate_json(f.read())
        return skill

    @classmethod
    def create(self, **kwargs) -> CodeSkill:
        """Main method to create a new skill."""

        params = CreateParams(**kwargs)
        if params.messages:
            return self._create_from_messages(params.messages)
        
        if params.request:
            return self._create_from_request(params.request)
        
        if params.skill_path:
            params.skill_json_path = os.path.join(params.skill_path, "skill.json")
        
        if params.skill_json_path:
            return self._create_from_skill_json_path(params.skill_json_path)
        
        if params.messages_json_path:
            with open(params.messages_json_path) as f:
                messages = json.load(f)
            return self._create_from_messages(messages)
        
        if params.file_content:
            return self._create_from_file_content(params.file_content)
        
        if params.file_path:
            with open(params.file_path) as f:
                file_content = "# file name: " + os.path.basename(params.file_path) + "\n" + f.read()
            return self._create_from_file_content(file_content)
        
        if params.huggingface_repo_id and params.huggingface_skill_path:
            # huggingface_skill_path pattern username/skill_name_{version}, the version is optional and default to 1.0.0
            save_path = os.path.join(config.remote_skill_library_path, params.huggingface_repo_id, params.huggingface_skill_path)
            skill = hf_pull(repo_id=params.huggingface_repo_id, huggingface_skill_path=params.huggingface_skill_path, save_path=save_path)
            self.save(skill=skill, skill_path=save_path)
            return skill
        
        raise ValueError("Please provide one of the following parameters: messages, request, skill_path, messages_json_path, file_content, or file_path.")
        
    @classmethod
    def save(self, skill: Union[BaseSkill, CodeSkill], **kwargs) -> None:
        """Save the skill in various formats."""
        
        if len(kwargs) == 0:
            skill_path = os.path.join(config.local_skill_library_path, skill.skill_name)
            if not os.path.exists(skill_path):
                os.makedirs(skill_path)
            kwargs["skill_path"] = skill_path

        params = SaveParams(**kwargs)

        if params.huggingface_repo_id:
            local_dir = os.path.join(config.remote_skill_library_path, params.huggingface_repo_id)
            hf_repo_update(params.huggingface_repo_id, local_dir)
            skill_path = os.path.join(local_dir, skill.skill_name)
            params.skill_path = skill_path
        
        if params.skill_path:
            os.makedirs(os.path.dirname(params.skill_path), exist_ok=True)
            # save json file
            with open(os.path.join(params.skill_path, "skill.json"), "w") as f:
                json.dump(skill.model_dump(), f, ensure_ascii=False, indent=4)
            
            # save function call
            with open(os.path.join(params.skill_path, "function_call.json"), "w") as f:
                json.dump(skill.to_function_call(), f, ensure_ascii=False, indent=4)
            
            # save dependencies
            command_str = ""
            if skill.skill_dependencies:
                command_str = generate_install_command(skill.skill_program_language, skill.skill_dependencies)
                with open(os.path.join(params.skill_path, "install_dependencies.sh"), "w") as f:
                    f.write(command_str)
            
            # save code
            if skill.skill_program_language:
                language_suffix = generate_language_suffix(skill.skill_program_language)
                with open(os.path.join(params.skill_path, "skill_code" + language_suffix), "w") as f:
                    f.write(skill.skill_code)

            # save conversation history
            if skill.conversation_history:
                with open(os.path.join(params.skill_path, "conversation_history.json"), "w") as f:
                    f.write(json.dumps(skill.conversation_history, ensure_ascii=False, indent=4))

            # skill description
            doc = generate_skill_doc(skill)
            with open(os.path.join(params.skill_path, "skill_doc.md"), "w") as f:
                f.write(doc)

            # embedding_text
            embedding_text = "{skill.skill_name}\n{skill.skill_description}\n{skill.skill_usage_example}\n{skill.skill_tags}".format(skill=skill)
            with open(os.path.join(params.skill_path, "embedding_text.txt"), "w") as f:
                f.write(embedding_text)
            
            # save test code
            if skill.unit_tests:
                # TODO:
                pass

            if params.huggingface_repo_id:
                hf_push(params.skill_path)

        print(Markdown(f"> saved to {params.skill_path}"))

    def search(self, **kwargs) -> List[CodeSkill]:
        """Placeholder for search functionality."""
        raise NotImplementedError
