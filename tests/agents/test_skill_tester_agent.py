import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from creator.core.skill import CodeSkill, BaseSkillMetadata
import creator


def create_skill():
    skill_json = {
        "skill_name": "filter_prime_numbers",
        "skill_description": "This skill filters the number of prime numbers in a given range.",
        "skill_tags": [
            "prime numbers",
            "filter",
            "range"
        ],
        "skill_usage_example": "filter_prime_numbers(2, 201)",
        "skill_program_language": "python",
        "skill_code": "def filter_prime_numbers(start, end):\n    def isPrime(num):\n        if num < 2:\n            return False\n        for i in range(2, int(num ** 0.5) + 1):\n            if num % i == 0:\n                return False\n        return True\n\n    count = 0\n    for num in range(start, end + 1):\n        if isPrime(num):\n            count += 1\n\n    return count",
        "skill_parameters": [
            {
                "param_name": "start",
                "param_type": "integer",
                "param_description": "The starting number of the range.",
                "param_required": True,
                "param_default": None
            },
            {
                "param_name": "end",
                "param_type": "integer",
                "param_description": "The ending number of the range.",
                "param_required": True,
                "param_default": None
            }
        ],
        "skill_return": {
            "param_name": "count",
            "param_type": "integer",
            "param_description": "The number of prime numbers in the given range.",
            "param_required": True,
            "param_default": None
        },
        "skill_dependencies": None,
        "test_summary": None
    }
    skill = CodeSkill(**skill_json)
    skill.skill_metadata = BaseSkillMetadata()
    return skill


def test_tester_agent():
    skill = create_skill()
    test_summary = skill.test()
    print(repr(test_summary))
    test_summary.show()
    creator.save(skill)


if __name__ == "__main__":
    test_tester_agent()

