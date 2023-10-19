## Open-Creator API Documentation

### Function: `create`
Generates a `CodeSkill` instance using different input sources.

#### Parameters:
- `request`: String detailing the skill functionality.
- `messages` or `messages_json_path`: Messages as a list of dictionaries or a path to a JSON file containing messages.
- `file_content` or `file_path`: String of file content or path to a code/API doc file.
- `skill_path` or `skill_json_path`: Directory path with skill name as stem or file path with `skill.json` as stem.
- `huggingface_repo_id`: Identifier for a Huggingface repository.
- `huggingface_skill_path`: Path to the skill within the Huggingface repository.

#### Returns:
- `CodeSkill`: The created skill.

#### Installation
```shell
pip install -U open-creator
```
open-creator: "^0.1.2"

#### Usage:
```python
from creator import create
```

#### Notes:
- Ensure to provide accurate and accessible file paths.
- At least one parameter must be specified to generate a skill.
- Parameters’ functionality does not overlap; specify the most relevant one for clarity.
- Use absolute paths where possible to avoid relative path issues.
- Ensure the repository ID and skill path are accurate and that you have the necessary access permissions to retrieve the skill from the repository.
