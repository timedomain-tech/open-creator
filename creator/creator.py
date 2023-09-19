import os
from typing import Union
from creator.agents import messages_skill_extractor_agent
from creator.schema.skill import CodeSkill, BaseSkill
from creator.schema.creator import CreateParams, SaveParams
from creator.dependency import (
    generate_install_command,
    generate_language_suffix,
    generate_skill_doc
)

from rich import print
from rich.markdown import Markdown

import getpass
import platform
import json


default_skill_library_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library"
if not os.path.exists(default_skill_library_path):
    os.makedirs(default_skill_library_path)


class Creator:

    @classmethod
    def _create_from_messages(self, messages):
        skill_json = messages_skill_extractor_agent.run({
            "messages": messages,
            "username": getpass.getuser(),
            "current_working_directory": os.getcwd(),
            "operating_system": platform.system(),
            "verbose": True,
        })
        skill = CodeSkill(**skill_json)
        return skill

    @classmethod
    def _create_from_request(self, request):
        raise NotImplementedError
    
    @classmethod
    def _create_from_skill_path(self, skill_path):
        with open(os.join(skill_path, "skill.json"), "r") as f:
            skill = CodeSkill.model_validate_json(f.read())
        return skill

    @classmethod
    def create(self, **kwargs):
        """Create a new skill."""
        if len(kwargs) == 0:
            kwargs["skill_path"] = default_skill_library_path
        
        params = CreateParams(**kwargs)

        if len(params.messages) > 0:
            return self._create_from_messages(params.messages)

        if params.request:
            return self._create_from_request(params.request)
        
        if params.skill_path:
            return self._create_from_skill_path(params.skill_path)

        if params.messages_json_path:
            import json
            with open(params.messages_json_path) as f:
                messages = json.load(f)
            return self._create_from_messages(messages)
    
    @classmethod
    def save(self, skill: Union[BaseSkill, CodeSkill], **kwargs):
        """Save the skill to a json file. or a code file or a huggingface hub or langchain hub"""
        
        if len(kwargs) == 0:
            skill_path = os.path.join(default_skill_library_path, skill.skill_name)
            if not os.path.exists(skill_path):
                os.makedirs(skill_path)
            kwargs["skill_path"] = skill_path

        params = SaveParams(**kwargs)
        
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
            embedding_text = "{skill.skill_name}\n{skill.skill_description}\n{skill.skill_usage_example}".format(skill=skill)
            with open(os.path.join(params.skill_path, "embedding_text.txt"), "w") as f:
                f.write(embedding_text)
            
            # save test code
            if skill.unit_tests:
                # TODO:
                pass
        print(Markdown(f"> saved to {params.skill_path}"))

    def search(self, **kwargs):
        raise NotImplementedError
