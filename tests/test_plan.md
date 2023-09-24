

## Test Plan

### Creator

#### creator.create
Return: a skill object
- Normal Functionality
  - `creator.create(request="xxx")`
  - `creator.create(messages=[xxx,])` only support openai messages
  - `creator.create(skill_json_path="~/.cache/open_creator/skill_library/{skill_name}/skill.json")`
  - `creator.create(messages_json_path="xxx.json")`
  - `creator.create(file_content="content")` can be API docs or code file
  - `creator.create(file_path="xxxx.md")` can be API docs or code file path
  - `creator.create(huggingface_repo_id="timedomain/skill_library", huggingface_skill_path="code_interpreter")` can be API docs or code file url
- Error Handling
  - `creator.create()` this will print error and return None
  - `creator.create(request="xxx", messages=[xxx,])` two or more params as input will print error and return None
  -  `huggingface_repo_id` and `huggingface_skill_path` should both input or not input, otherwise will print error and return None

#### creator.save
Return: None
- Normal Functionality
  - `creator.save(skill, skill_path="~/.cache/open_creator/skill_library/{skill_name}")`
  - `creator.save(skill, huggingface_repo_id="timedomain/skill_library")`
- Error Handling
  - no skill input will print error and return None


#### creator.search
Return: List[skill]
- Normal Functionality
  - `creator.search(query="xxx", top_k=3, threshold=0.8)` top_k and threshold are optional
- Error Handling
  - `creator.search(query="xxx", remote=True) raise NotImplementedError

