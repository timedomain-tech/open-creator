## Skill Details:
- **Name**: search
- **Description**: This skill allows users to search for skills by query.
- **Version**: 1.0.0
- **Usage**:
```python
skills = search('I want to extract some pages from a pdf')
```
- **Parameters**:
   - **query** (string): The query to search for skills.
        - Required: True
   - **top_k** (integer): The maximum number of skills to return.
      - Default: 1
   - **threshold** (float): The minimum similarity score to return a skill.
      - Default: 0.8

- **Returns**:
   - **skills** (array): A list of CodeSkill objects.