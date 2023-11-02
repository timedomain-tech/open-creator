import json


def load_system_prompt(prompt_path):
    with open(prompt_path, encoding='utf-8') as f:
        prompt = f.read()
    return prompt


def load_json_schema(json_schema_path):
    with open(json_schema_path, encoding="utf-8") as f:
        json_schema = json.load(f)
    return json_schema
