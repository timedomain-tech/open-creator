## Skill Details:
- **Name**: save
- **Description**: Save a skill to a local path or a huggingface repo.
- **Version**: 1.0.0
- **Usage**:
You need to create a skill first
```python
import creator
import os
skill_json_path = os.path.expanduser("~") + "/.cache/open_creator/skill_library/ask_run_code_confirm/skill.json"
skill = creator.create(skill_json_path=skill_json_path)
```
```python
save(skill=skill, huggingface_repo_id="ChuxiJ/skill_library")
```
or
```python
save(skill=skill, skill_path="/path/to/save")
```
- **Parameters**:
   - **skill** (object): CodeSkill object, the skill to be saved.
        - Required: True
   - **huggingface_repo_id** (string): optional, the ID of the huggingface repo. If provided, the skill will be saved to this repo.
   - **skill_path** (string): optional, the local path. If provided, the skill will be saved to this path.

- **Returns**: