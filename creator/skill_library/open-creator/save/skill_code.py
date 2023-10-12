from creator.core import creator
from creator.core.skill import CodeSkill


def save(skill: CodeSkill, huggingface_repo_id: str = None, skill_path: str = None):
    """
    Save a skill to a local path or a huggingface repo.
    
    Parameters:
    skill: CodeSkill object, the skill to be saved.
    huggingface_repo_id: str, optional, the ID of the huggingface repo. If provided, the skill will be saved to this repo.
    skill_path: str, optional, the local path. If provided, the skill will be saved to this path.
    
    Returns:
    None
    
    Example:
    >>> import creator
    >>> import os
    >>> skill_json_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library/ask_run_code_confirm/skill.json"
    >>> skill = creator.create(skill_json_path=skill_json_path)
    >>> save(skill=skill, huggingface_repo_id="ChuxiJ/skill_library") # save to remote
    >>> save(skill=skill, skill_path="/path/to/save") # save to local
    """
    if huggingface_repo_id is not None:
        creator.save(skill=skill, huggingface_repo_id=huggingface_repo_id)
    elif skill_path is not None:
        creator.save(skill=skill, skill_path=skill_path)
    else:
        creator.save(skill=skill)