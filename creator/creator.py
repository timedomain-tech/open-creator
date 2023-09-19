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

import getpass
import platform
import json


default_skill_library_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library"
if not os.path.exists(default_skill_library_path):
    os.makedirs(default_skill_library_path)


class Creator:

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

    def _create_from_request(self, request):
        raise NotImplementedError
    
    def _create_from_skill_json_path(self, skill_json_path):
        with open(skill_json_path) as f:
            skill = CodeSkill.model_validate_json(f.read())
        return skill

    def create(self, **kwargs):
        """Create a new skill."""
        if len(kwargs) == 0:
            kwargs["skill_json_path"] = default_skill_library_path

        params = CreateParams(**kwargs)

        if len(params.messages) > 0:
            return self._create_from_messages(params.messages)

        if params.request:
            return self._create_from_request(params.request)
        
        if params.skill_json_path:
            return self._create_from_skill_json_path(params.skill_json_path)

        params.messages_json_path
        if params.messages_json_path:
            import json
            with open(params.messages_json_path, "r") as f:
                messages = json.load(f)
            return self._create_from_messages(messages)
        
    def save(self, skill: Union[BaseSkill, CodeSkill], **kwargs):
        """Save the skill to a json file. or a code file or a huggingface hub or langchain hub"""
        
        if len(kwargs) == 0:
            kwargs["save_path"] = os.path.join(default_skill_library_path, skill.skill_name)

        params = SaveParams(**kwargs)
        
        if params.save_path:
            os.makedirs(os.path.dirname(params.save_path), exist_ok=True)
            # save json file
            with open(os.path.join(params.save_path, "skill.json"), "w") as f:
                f.write(skill.model_dump_json())
            
            # save function call
            with open(os.path.join(params.save_path, "function_call.json"), "w") as f:
                f.write(skill.to_function_call())
            
            # save dependencies
            command_str = ""
            if skill.skill_dependencies:
                command_str = generate_install_command(skill.skill_program_language, skill.skill_dependencies)
                with open(os.path.join(params.save_path, "install_dependencies.sh"), "w") as f:
                    f.write(command_str)
            
            # save code
            if skill.skill_program_language:
                language_suffix = generate_language_suffix(skill.skill_program_language)
                with open(os.path.join(params.save_path, "skill_code" + language_suffix), "w") as f:
                    f.write(skill.skill_code)

            # save conversation history
            if skill.conversation_history:
                with open(os.path.join(params.save_path, "conversation_history.json"), "w") as f:
                    f.write(json.dumps(skill.conversation_history, ensure_ascii=False))

            # skill description
            doc = generate_skill_doc(skill)
            with open(os.path.join(params.save_path, "skill_doc.md"), "w") as f:
                f.write(doc)

            # embedding_text
            desc_text = skill.skill_description + 
            
            # save test code
            if skill.unit_tests:
                # TODO:
                pass
            
            

    def search(self, **kwargs):
        raise NotImplementedError
