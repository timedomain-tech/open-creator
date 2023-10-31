import json

from langchain.schema.runnable import RunnableConfig

from creator.utils import runnable, print, print_run_url
from creator.utils import generate_install_command
from creator.config.library import config as creator_config
from creator.agents import (
    create_skill_extractor_agent,
    create_code_interpreter_agent,
    create_code_tester_agent,
    create_prompt_enhancer_agent,
    create_code_refactor_agent
)


@runnable(run_name="ConstructCreateSkillMessages")
def construct_create_skill_messages(request):
    if isinstance(request, str):
        content = request
    elif isinstance(request, dict) and "request" in request:
        content = request["request"]
    return {
        "messages": [
            {"role": "user", "content": content}
        ]
    }


@print_run_url
def create_skill_from_messages(messages):
    skill_extractor_agent = create_skill_extractor_agent(creator_config)
    return skill_extractor_agent.with_config({"run_name": "CreateSkillFromMessages"}).invoke(input={"messages": messages})["extracted_skill"]


@print_run_url
def create_skill_from_request(request):
    creator_config.use_rich = False
    prompt_enhancer_agent = create_prompt_enhancer_agent(creator_config)
    creator_config.use_rich = True
    code_interpreter_agent = create_code_interpreter_agent(creator_config)
    skill_extractor_agent = create_skill_extractor_agent(creator_config)
    chain = construct_create_skill_messages | prompt_enhancer_agent | construct_create_skill_messages | code_interpreter_agent | skill_extractor_agent
    skill_json = chain.with_config({"run_name": "CreateSkillFromRequest"}).invoke(input=request)["extracted_skill"]
    return skill_json


@print_run_url
def create_skill_from_file_content(file_content):
    skill_extractor_agent = create_skill_extractor_agent(creator_config)
    chain = construct_create_skill_messages | skill_extractor_agent
    skill_json = chain.with_config({"run_name": "CreateSkillFromFileContent"}).invoke(input=file_content)["extracted_skill"]
    return skill_json


@runnable(run_name="ConstructCreatorMessages")
def _generate_install_command(inputs):
    install_script = generate_install_command(**inputs)
    return install_script


@runnable(run_name="InstallSkill")
def install_skill(inputs, config: RunnableConfig):
    skill_dependencies, skill_program_language = inputs["skill_dependencies"], inputs["skill_program_language"]
    if skill_dependencies is None:
        return inputs
    try:
        install_script = _generate_install_command.invoke({"language": skill_program_language, "dependencies": skill_dependencies}, config)
        print("> Installing dependencies", print_type="markdown")
        print(f"```bash\n{install_script}\n```\n", print_type="markdown")
        result = creator_config.code_interpreter.run({"language": "shell", "code": install_script}, run_name="InstallDependencies", callbacks=config.get("callbacks", None))
        print(f"> Install dependencies result: {result}", print_type="markdown")
    except Exception as e:
        print(f"> Error when installing dependencies: {e}", print_type="markdown")
    return inputs


@runnable(run_name="ConstructRunSkillMessages")
def construct_run_skill_messages(inputs):
    skill_name, skill_program_language, skill_code, tool_result, params = inputs["skill_name"], inputs["skill_program_language"], inputs["skill_code"], inputs["tool_result"], inputs["params"]
    messages = [
        {"role": "assistant", "content": "ok I will run your code", "function_call": {
            "name": skill_name,
            "arguments": json.dumps({"language": skill_program_language, "code": skill_code})
        }}
    ]
    params = json.dumps(params) if isinstance(params, dict) else params
    messages.append({"role": "function", "name": "run_code", "content": json.dumps(tool_result)})
    messages.append({"role": "user", "content": params})
    return {"messages": messages}


@runnable(run_name="SetupSkill")
def setup_skill(inputs, config: RunnableConfig):
    language, code = inputs["language"], inputs["code"]
    tool_result = creator_config.code_interpreter.invoke({"language": language, "code": code}, config)
    inputs["tool_result"] = tool_result
    return inputs


@runnable(run_name="RunSkill")
def run_skill(inputs, config: RunnableConfig):
    code_interpreter_agent = create_code_interpreter_agent(creator_config)
    code_interpreter_agent.tools[0] = creator_config.code_interpreter
    tool_inputs = {"language": inputs["skill_program_language"], "code": inputs["skill_code"]}
    inputs.update(tool_inputs)
    chain = (install_skill | setup_skill | construct_run_skill_messages | code_interpreter_agent).with_config({"run_name": "Steps"})
    messages = chain.invoke(inputs, config)["messages"]
    return messages


@runnable(run_name="ConstructTestSkillMessages")
def construct_test_skill_messages(inputs):
    skill_repr, tool_input, tool_result = inputs["skill_repr"], inputs["tool_input"], inputs["tool_result"]
    messages = [
        {"role": "user", "content": skill_repr},
        {"role": "assistant", "content": "", "function_call": {"name": "run_code", "arguments": json.dumps(tool_input)}},
        {"role": "function", "name": "run_code", "content": json.dumps(tool_result)},
        {"role": "user", "content": "I have already run the function for you so you can directy use the function by passing the parameters without import the function"},
    ]
    return {"messages": messages}


@runnable(run_name="TestSkill")
def test_skill(inputs, config: RunnableConfig):
    code_tester_agent = create_code_tester_agent(creator_config)
    code_tester_agent.tools[0] = creator_config.code_interpreter
    code = f"""\n\n
import io
import unittest
stream = io.StringIO()
runner = unittest.TextTestRunner(stream=stream)


{inputs["skill_code"]}
"""
    tool_inputs = {"language": inputs["skill_program_language"], "code": code}
    inputs.update(tool_inputs)
    inputs["tool_input"] = tool_inputs
    chain = (install_skill | setup_skill | construct_test_skill_messages | code_tester_agent).with_config({"run_name": "Steps"})
    test_result = chain.invoke(inputs, config)["output"]
    return test_result


@runnable(run_name="ConstructRefactorSkillMessages")
def construct_refactor_skill_messages(inputs):
    conversation_history, refactor_type, skill_repr, skill_program_language, skill_code, user_request = inputs["conversation_history"], inputs["refactor_type"], inputs["skill_repr"], inputs["skill_program_language"], inputs["skill_code"], inputs["user_request"]
    messages = [
        {"role": "system", "content": f"Your action type is: {refactor_type}"},
        {"role": "function", "name": "show_skill", "content": skill_repr},
        {"role": "function", "name": "show_code", "content": f"current skill code:\n```{skill_program_language}\n{skill_code}\n```"},
        {"role": "user", "content": f"{user_request}\nplease output only one skill object" if refactor_type in ("Combine", "Refine") else "\nplease help me decompose the skill object into different independent skill objects"}
    ]
    messages = conversation_history + [{"role": "system", "content": "Above context is conversation history from other agents. Now let's refactor our skill."}] + messages
    return {"messages": messages}


@runnable(run_name="RefactorSkill")
def refactor_skill(inputs, config: RunnableConfig):
    code_refactor_agent = create_code_refactor_agent(creator_config)
    chain = construct_refactor_skill_messages | code_refactor_agent
    refactored_skill_jsons = chain.invoke(inputs, config)["refacted_skills"]
    return refactored_skill_jsons


@runnable(run_name="AutoOptimizeSkill")
def auto_optimize_skill(inputs, config: RunnableConfig):
    old_skill, retry_times = inputs["old_skill"], inputs["retry_times"]
    skill = old_skill.model_copy(deep=True)
    refined = False
    conversation_history = [] if skill.conversation_history is None else skill.conversation_history
    for i in range(retry_times):
        if skill.test_summary is None:
            test_result = test_skill.invoke({
                "skill_program_language": skill.skill_program_language,
                "skill_dependencies": skill.skill_dependencies,
                "skill_code": skill.skill_code,
                "skill_repr": repr(skill)
            }, config)
            conversation_history = conversation_history + test_result["messages"]
            if "test_summary" in test_result:
                test_summary = test_result["test_summary"]
                if isinstance(test_summary, dict) and "test_cases" in test_summary:
                    pass
                else:
                    test_summary = {"test_cases": test_summary}
                all_passed = all(test_case["is_passed"] for test_case in test_summary["test_cases"])
                if all_passed and refined:
                    skill.conversation_history = conversation_history
                    return {
                        "skill": skill,
                        "test_summary": test_summary,
                    }
            print(f"> Auto Refine Skill {i+1}/{retry_times}", print_type="markdown")
            skill = skill > "I have tested the skill, but it failed, please refine it."
            skill.conversation_history = conversation_history
            if all_passed:
                return {
                    "skill": skill,
                    "test_summary": test_summary,
                }
            refined = True
    return {
        "skill": skill,
        "test_summary": test_summary,
    }
