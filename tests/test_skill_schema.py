import sys
sys.path.append("..")
from creator.schema.skill import CodeSkill
import json


if __name__ == "__main__":
    with open("skill_schema_example.json") as f:
        skill = CodeSkill.model_validate_json(json_data=f.read())

    with open("skill_schema_example.json") as f:
        skill_json = json.load(f)
    skill = CodeSkill(**skill_json)
    # print(skill.model_dump_json())
    skill_json_schema = CodeSkill.to_skill_function_schema()
    print(json.dumps(skill_json_schema, ensure_ascii=False))
          