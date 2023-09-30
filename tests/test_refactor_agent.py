import sys
sys.path.append("..")

from creator.schema.skill import CodeSkill, BaseSkillMetadata
from rich import print
from rich.markdown import Markdown
import json


def create_finetune_testcase():
    skillA_schema = {
        "skill_name": "data_cleaning",
        "skill_description": "Cleans input data by converting string representations of 'null' and 'NaN' to actual null values, and then removing null values and duplicates.",
        "skill_tags": ["data_processing", "cleaning", "null_removal", "duplicate_removal"],
        "skill_usage_example": "data_cleaning(input_data, remove_duplicates=True)",
        "skill_program_language": "python",
        "skill_code": """
    def data_cleaning(data, remove_duplicates=True):
        # Convert string representations of null to actual null values
        data = data.replace({'null': None, 'NaN': None})
        
        # Remove null values
        data = data.dropna()
        
        # Remove duplicates if specified
        if remove_duplicates:
            data = data.drop_duplicates()
        
        return data
        """,
        "skill_parameters": [
            {
                "param_name": "data",
                "param_type": "array",
                "param_description": "The input dataset that needs cleaning.",
                "param_required": True
            },
            {
                "param_name": "remove_duplicates",
                "param_type": "boolean",
                "param_description": "Flag to determine if duplicates should be removed. Defaults to True.",
                "param_required": False,
                "param_default": True
            }
        ],
        "skill_return": {
            "param_name": "cleaned_data",
            "param_type": "array",
            "param_description": "The cleaned dataset with string 'null'/'NaN' values converted to actual nulls, and nulls and duplicates removed based on specified parameters."
        },
        "skill_dependencies": [
            {
                "dependency_name": "pandas",
                "dependency_version": "1.2.0",
                "dependency_type": "package"
            }
        ]
    }
    skill = CodeSkill(**skillA_schema)
    skill.skill_metadata = BaseSkillMetadata()
    return skill

def test_refactor_add_input_param():
    skillA = create_finetune_testcase()
    print(Markdown(repr(skillA)))
    finetuned_skillA = skillA > "add a parameter that allows the choice of whether to remove duplicate values"
    print(Markdown(repr(finetuned_skillA)))

def test_refactor_add_output_param():
    skillA = create_finetune_testcase()
    print(Markdown(repr(skillA)))
    finetuned_skillA = skillA > "Not only get cleaned data, but also want to get statistics on deleted null and duplicate values"
    print(Markdown(repr(finetuned_skillA)))

def test_refactor_change_logic():
    skillA = create_finetune_testcase()
    print(Markdown(repr(skillA)))
    finetuned_skillA = skillA > 'Convert all "null" or "NaN" of string type to true null before removing nulls'
    print(Markdown(repr(finetuned_skillA)))

def create_combine_testcase():
    skillA_json = {
        "skill_name": "data_cleaning",
        "skill_description": "This skill is responsible for cleaning the input data by removing empty values. It provides a simple way to preprocess data and make it ready for further analysis or visualization.",
        "skill_tags": ["cleaning", "preprocessing", "data"],
        "skill_usage_example": "data_cleaning(input_data)",
        "skill_program_language": "python",
        "skill_code": """
def data_cleaning(data):
    \"\"\"Clean the data by removing empty values.\"\"\"
    return [item for item in data if item is not None]
""",
        "skill_parameters": [
            {
                "param_name": "data",
                "param_type": "array",
                "param_description": "The input data that needs cleaning. It should be a list of values.",
                "param_required": True
            }
        ],
        "skill_return": {
            "param_name": "cleaned_data",
            "param_type": "array",
            "param_description": "The cleaned data after removing empty values."
        },
        "skill_dependencies": None
    }
    skillA = CodeSkill(**skillA_json)
    skillA.skill_metadata = BaseSkillMetadata()

    skillB_json = {
        "skill_name": "data_visualization",
        "skill_description": "This skill is responsible for visualizing the input data by generating a bar chart. It helps in understanding the data distribution and patterns.",
        "skill_tags": ["visualization", "chart", "data"],
        "skill_usage_example": "data_visualization(input_data)",
        "skill_program_language": "python",
        "skill_code": """
        import matplotlib.pyplot as plt

        def data_visualization(data):
            \"\"\"Visualize the data using a bar chart.\"\"\"
            plt.bar(range(len(data)), data)
            plt.show()
        """,
        "skill_parameters": [
            {
                "param_name": "data",
                "param_type": "array",
                "param_description": "The input data that needs to be visualized. It should be a list of values.",
                "param_required": True
            }
        ],
        "skill_return": None,
        "skill_dependencies": [
            {
                "dependency_name": "matplotlib",
                "dependency_version": "3.4.3",
                "dependency_type": "package"
            }
        ]
    }
    skillB = CodeSkill(**skillB_json)
    skillB.skill_metadata = BaseSkillMetadata()

    skillC_json = {
        "skill_name": "data_statistics",
        "skill_description": "This skill calculates the average value of the input data. It provides a basic statistical overview of the dataset.",
        "skill_tags": ["statistics", "average", "data"],
        "skill_usage_example": "data_statistics(input_data)",
        "skill_program_language": "python",
        "skill_code": """
        def data_statistics(data):
            \"\"\"Calculate the average of the data.\"\"\"
            return sum(data) / len(data)
        """,
    "skill_parameters": [
        {
            "param_name": "data",
            "param_type": "array",
            "param_description": "The input data for which the average needs to be calculated. It should be a list of numerical values.",
            "param_required": True
        }
    ],
    "skill_return": {
        "param_name": "average",
        "param_type": "float",
        "param_description": "The average value of the input data."
    },
        "skill_dependencies": None
    }
    skillC = CodeSkill(**skillC_json)
    skillC.skill_metadata = BaseSkillMetadata()
    return skillA, skillB, skillC

def test_refactor_chain_combine():
    skillA, skillB, skillC = create_combine_testcase()
    print(Markdown(repr(skillA)))
    print(Markdown(repr(skillB)))
    chained_skill = skillA + skillB > "I have a dataset with empty values. First, I want to clean the data by removing the empty values, then visualize it using a bar chart."
    print(Markdown(repr(chained_skill)))

def test_refactor_internal_logic_combination():
    skillA, skillB, skillC = create_combine_testcase()
    print(Markdown(repr(skillA)))
    print(Markdown(repr(skillB)))
    chained_skill = skillA + skillB + skillC > "I have a dataset. I want to calculate its average. If the average is above a certain threshold, I'd like to visualize the data using a bar chart. Otherwise, I just want the average value."
    print(Markdown(repr(chained_skill)))

def test_refactor_parallel_combination():
    skillA, skillB, skillC = create_combine_testcase()
    chained_skill = skillA + skillB + skillC > "I have a dataset. I want to both visualize the data using a bar chart and calculate its average simultaneously"
    print(Markdown(repr(chained_skill)))
    skill = chained_skill[0]
    print(skill.model_dump())

def create_complex_skill():
    skill_json = {
        'skill_name': 'data_visualization_and_statistics',
        'skill_description': 'This skill is responsible for visualizing the input data using a bar chart and calculating its average simultaneously. It provides a comprehensive overview of the dataset.',
        'skill_metadata': {'created_at': '2023-09-30 00:26:46', 'author': 'gongjunmin', 'updated_at': '2023-09-30 00:26:46', 'usage_count': 0, 'version': '1.0.0', 'additional_kwargs': {}},
        'skill_tags': ['data visualization', 'statistics', 'bar chart'],
        'skill_usage_example': 'data_visualization_and_statistics(input_data)',
        'skill_program_language': 'python',
        'skill_code': 'def data_visualization_and_statistics(input_data):\n    visualize_data(input_data)\n    calculate_average(input_data)',
        'skill_parameters': [
            {'param_name': 'input_data', 'param_type': 'any', 'param_description': 'The input dataset to be visualized and analyzed.', 'param_required': True, 'param_default': None}
        ],
        'skill_return': None,
        'skill_dependencies': [
            {'dependency_name': 'visualize_data', 'dependency_version': '', 'dependency_type': 'built-in'},
            {'dependency_name': 'calculate_average', 'dependency_version': '', 'dependency_type': 'built-in'}
        ]
    }
    skill = CodeSkill(**skill_json)
    skill.skill_metadata = BaseSkillMetadata()
    return skill

def test_refactor_decompose():
    skill = create_complex_skill()
    # print(Markdown(repr(skill)))
    decomposed_skill = skill < "I want to decompose this skill into two skills: one for visualizing the data using a bar chart, and one for calculating the average."
    print(Markdown(repr(decomposed_skill)))

if __name__ == "__main__":
    test_refactor_decompose()
