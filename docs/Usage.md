# Usage
```python
import creator
```
## 1. Create a Skill
- [x] 1.1 from a request
- [x] 1.2 from a conversation history (openai messages format)
- [x] 1.3 from a skill json file
- [x] 1.4 from a messages_json_path
- [x] 1.5 from code file content
- [x] 1.6 from doc file content
- [x] 1.7 from file path
- [x] 1.8 from huggingface

1.1 Create a skill from a request
```python
request = "help me write a script that can extracts a specified section from a PDF file and saves it as a new PDF"
skill = creator.create(request=request)
```

1.5 Create a skill from code file content
```python
code_content = """
def hello():
    print("Hello, world!")
"""
skill = creator.create(file_content=code_content)
```

1.6 Create a skill from doc file content
```python
doc_content = """
# Installation
pip install mypackage
"""
skill = creator.create(file_content=doc_content)
```

1.7 Create a skill from file path
```python
skill = creator.create(file_path="path/to/your/file.py")
```

1.8 Create a skill from huggingface
```python
skill = creator.create(huggingface_repo_id="YourRepoID", huggingface_skill_path="your_skill_path")
```

## 2. Save a Skill
- [x] 2.1 Save to default path
- [x] 2.2 Save to specific skill path
- [x] 2.3 Save to huggingface

2.1 Save to default path
```python
creator.save(skill)
```

2.2 Save to specific skill path
```python
creator.save(skill, skill_path="path/to/your/skill/directory")
```

2.3 Save to huggingface
```python
creator.save(skill, huggingface_repo_id="YourRepoID")
```

## 3. Search skills
- [x] 3.1 Local Search

3.1 Local Search
```python
skills = creator.search("your_search_query")
for skill in skills:
    print(skill)
```
