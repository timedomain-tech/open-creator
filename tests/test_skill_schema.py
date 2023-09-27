import sys
sys.path.append("..")
from creator.schema.skill import CodeSkill, TestSummary
import json


if __name__ == "__main__":
    # with open("skill_schema_example.json") as f:
    #     skill = CodeSkill.model_validate_json(json_data=f.read())

    with open("skill_schema_example.json") as f:
        skill_json = json.load(f)
    skill = CodeSkill(**skill_json)
    # print(skill.model_dump_json())
    skill_json_schema = CodeSkill.to_skill_function_schema()
    with open("../creator/agents/codeskill_function_schema.json", mode="w") as f:
        json.dump(skill_json_schema, f, ensure_ascii=False)
    
    test_summary_json_schema = TestSummary.to_test_function_schema()
    with open("../creator/agents/testsummary_function_schema.json", mode="w") as f:
        json.dump(test_summary_json_schema, f, ensure_ascii=False)
