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

#### Usage:
1. Creating Skill using a Request String:
```python
skill = create(request="filter how many prime numbers are in 201")
```
2. Creating Skill using Messages:
- Directly:
```python
skill = create(messages=[{"role": "user", "content": "write a program..."}])
```
- Via JSON Path:
```python
skill = create(messages_json_path="./messages_example.json")
```

3. Creating Skill using File Content or File Path:
- Direct Content:
```python
skill = create(file_content="def example_function(): pass")
```
- File Path:
```python
skill = create(file_path="../creator/utils/example.py")
```

4. Creating Skill using Skill Path or Skill JSON Path:
- JSON Path:
```python
skill = create(skill_json_path="~/.cache/open_creator/skill_library/create/skill.json")
```
- Skill Path:
```python
skill = create(skill_path="~/.cache/open_creator/skill_library/create")
```

5. Creating Skill using Huggingface Repository ID and Skill Path:
If a skill is hosted in a Huggingface repository, you can create it by specifying the repository ID and the skill path within the repository.
```python
skill = create(huggingface_repo_id="YourRepo/skill-library", huggingface_skill_path="specific_skill")
```

#### Notes:
- Ensure to provide accurate and accessible file paths.
- At least one parameter must be specified to generate a skill.
- Parameters’ functionality does not overlap; specify the most relevant one for clarity.
- Use absolute paths where possible to avoid relative path issues.
- Ensure the repository ID and skill path are accurate and that you have the necessary access permissions to retrieve the skill from the repository.


### Function: `save`
Stores a `CodeSkill` instance either to a local path or a Huggingface repository. In default just use `save(skill)` and it will store the skill into the default path. Only save the skill when the user asks to do so.

#### Parameters:
- `skill` (CodeSkill): The skill instance to be saved.
- `huggingface_repo_id` (Optional[str]): Identifier for a Huggingface repository.
- `skill_path` (Optional[str]): Local path where the skill should be saved.

#### Returns:
- None

#### Usage:
The `save` function allows for the persistent storage of a `CodeSkill` instance by saving it either locally or to a specified Huggingface repository. 

1. **Save to Huggingface Repository:**
```python
save(skill=skill, huggingface_repo_id="YourRepo/skill_library")
```

2. **Save Locally:**
```python
save(skill=skill, skill_path="/path/to/save")
```

#### Notes:
- At least one of `huggingface_repo_id` or `skill_path` must be provided to execute the function, otherwise a `ValueError` will be raised.
- Ensure provided paths and repository identifiers are accurate and accessible.


### Function: `search`
Retrieve skills related to a specified query from the available pool of skills.

#### Parameters:
- `query` (str): Search query string.
- `top_k` (Optional[int]): Maximum number of skills to return. Default is 1.
- `threshold` (Optional[float]): Minimum similarity score to return a skill. Default is 0.8.

#### Returns:
- List[CodeSkill]: A list of retrieved `CodeSkill` objects that match the query.

#### Usage:
The `search` function allows users to locate skills related to a particular query string. This is particularly useful for identifying pre-existing skills within a skill library that may fulfill a requirement or for exploring available functionalities.

1. **Basic Search:**
```python
skills = search("extract pages from a pdf")
```

2. **Refined Search:**
```python
skills = search("extract pages from a pdf", top_k=3, threshold=0.85)
```

#### Notes:
- The `query` should be descriptive to enhance the accuracy of retrieved results.
- Adjust `top_k` and `threshold` to balance between specificity and breadth of results.
- Ensure to check the length of the returned list to validate the presence of results before usage.

Certainly, let's refine the "Skill object method" section for enhanced clarity and structure:

--- 

### Skill Object Methods and Operator Overloading

Explore the functionalities and modifications of a skill object through methods and overloaded operators.

#### Method: `run`
Execute a skill with provided arguments or request.

- **Example Usage**:
  ```python
skills = search("pdf extract section")
if skills:
    skill = skills[0]
    input_args = {
        "pdf_path": "creator.pdf",
        "start_page": 3,
        "end_page": 8,
        "output_path": "creator3-8.pdf"
    }
    print(skill.run(input_args))
  ```
  
#### Method: `test`
Validate a skill using a tester agent.

- **Example Usage**:
  ```python
skill = create(request="filter prime numbers in a range, e.g., filter_prime_numbers(2, 201)")
test_summary = skill.test()
print(test_summary)
print(skill.conversation_history)
  ```
  
#### Overloaded Operators: 
Modify and refine skills using operator overloading.

1. **Combining Skills**: Utilize the `+` operator to chain or execute skills in parallel, detailing the coordination with the `>` operator.
   ```python
   new_skill = skillA + skillB > "Explanation of how skills A and B operate together"
   ```
   
2. **Refactoring Skills**: Employ the `>` operator to enhance or modify existing skills.
   ```python
   refactored_skill = skill > "Descriptive alterations or enhancements"
   ```
   
3. **Decomposing Skills**: Use the `<` operator to break down a skill into simpler components.
   ```python
   simpler_skills = skill < "Description of how the skill should be decomposed"
   ```

#### Notes:
- Ensure accurate descriptions when using overloaded operators to ensure skill modifications are clear and understandable.
- Validate skills with `test` method to ensure functionality post-modification.
