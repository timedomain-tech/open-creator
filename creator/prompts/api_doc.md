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

#### Notes:
- use `skill.save()` or `save(skill)` as the default path is already set.


### Function: `search`
Retrieve skills related to a specified query from the available pool of skills.

#### Parameters:
- `query` (str): Search query string.
- `top_k` (Optional[int]): Maximum number of skills to return. Default is 1.
- `threshold` (Optional[float]): Minimum similarity score to return a skill. Default is 0.8.

#### Returns:
- List[CodeSkill]: A list of retrieved `CodeSkill` objects that match the query.

#### Notes:
- The `query` should be descriptive to enhance the accuracy of retrieved results.
- Adjust `top_k` and `threshold` to balance between specificity and breadth of results.
- Ensure to check the length of the returned list to validate the presence of results before usage.


### Skill Object Methods and Operator Overloading

Explore the functionalities and modifications of a skill object through methods and overloaded operators.

#### Method: `show` and `show_code`
Show a skill name, description, parameters, returns, usage examples and etc
Show the skill code
- **Example Usage**:
```python
skill.show()
skill.show_code()
```

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
- `CodeSkill` is a pydantic model, to see its propetries, use `.__annotations__`
