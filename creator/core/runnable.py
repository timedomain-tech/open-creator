import json

from creator.utils import runnable, print
from creator.utils import generate_install_command
from creator.config.library import config
from creator.llm import create_llm
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


@runnable(run_name="CreateSkillFromMessages")
def create_skill_from_messages(messages):
    skill_extractor_agent = create_skill_extractor_agent(create_llm(config))
    skill_json = skill_extractor_agent.invoke(input={"messages": messages})["extracted_skill"]
    return skill_json


@runnable(run_name="CreateSkillFromRequest")
def create_skill_from_request(request):
    config.use_rich = False
    prompt_enhancer_agent = create_prompt_enhancer_agent(create_llm(config))
    config.use_rich = True
    code_interpreter_agent = create_code_interpreter_agent(create_llm(config))
    skill_extractor_agent = create_skill_extractor_agent(create_llm(config))
    chain = construct_create_skill_messages | prompt_enhancer_agent | construct_create_skill_messages | code_interpreter_agent | skill_extractor_agent
    skill_json = chain.invoke(input={"request": request})["extracted_skill"]
    return skill_json


@runnable(run_name="CreateSkillFromFileContent")
def create_skill_from_file_content(file_content):
    skill_extractor_agent = create_skill_extractor_agent(create_llm(config))
    chain = construct_create_skill_messages | skill_extractor_agent
    skill_json = chain.invoke(input={"request": file_content})["extracted_skill"]
    return skill_json


@runnable(run_name="ConstructCreatorMessages")
def _generate_install_command(language: str, dependencies):
    install_script = generate_install_command(language, dependencies)
    return {"install_script": install_script}


@runnable(run_name="InstallSkill")
def install_skill(skill_dependencies, skill_program_language):
    if skill_dependencies is None:
        return
    try:
        install_script = _generate_install_command.invoke({"language": skill_program_language, "dependencies": skill_dependencies})
        print("> Installing dependencies", print_type="markdown")
        print(f"```bash\n{install_script}\n```\n", print_type="markdown")
        result = config.code_interpreter.run({"language": "shell", "code": install_script}, run_name="InstallDependencies")
        print(f"> Install dependencies result: {result}", print_type="markdown")
    except Exception as e:
        print(f"> Error when installing dependencies: {e}", print_type="markdown")
    return


@runnable(run_name="ConstructRunSkillMessages")
def construct_run_skill_messages(skill_name, skill_program_language, skill_code, tool_result, params):
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
def setup_skill(skill_program_language, skill_code):
    tool_result = config.code_interpreter.run({
        "language": skill_program_language,
        "code": skill_code
    })
    return {"tool_result": tool_result}


@runnable(run_name="RunSkill")
def run_skill(params, skill_name, skill_program_language, skill_code, skill_dependencies):
    install_skill.invoke({"skill_dependencies": skill_dependencies, "skill_program_language": skill_program_language})
    tool_result = setup_skill.invoke({"skill_program_language": skill_program_language, "skill_code": skill_code})["tool_result"]
    code_interpreter_agent = create_code_interpreter_agent(create_llm(config))
    code_interpreter_agent.tools[0] = config.code_interpreter
    messages_inputs = construct_run_skill_messages.invoke({"skill_name": skill_name, "skill_program_language": skill_program_language, "skill_code": skill_code, "tool_result": tool_result, "params": params})
    messages = code_interpreter_agent.invoke(messages_inputs)["messages"]
    return messages


@runnable(run_name="ConstructTestSkillMessages")
def construct_test_skill_messages(skill_repr, tool_input, tool_result):
    messages = [
        {"role": "user", "content": skill_repr},
        {"role": "assistant", "content": "", "function_call": {"name": "run_code", "arguments": json.dumps(tool_input)}},
        {"role": "function", "name": "run_code", "content": json.dumps(tool_result)},
        {"role": "user", "content": "I have already run the function for you so you can directy use the function by passing the parameters without import the function"},
    ]
    return {"messages": messages}


@runnable(run_name="TestSkill")
def test_skill(skill_program_language, skill_dependencies, skill_code, skill_repr):
    install_skill.invoke({"skill_dependencies": skill_dependencies, "skill_program_language": skill_program_language})
    code = f"""\n\n
import io
import unittest
stream = io.StringIO()
runner = unittest.TextTestRunner(stream=stream)


{skill_code}
"""
    tool_inputs = {"skill_program_language": skill_program_language, "skill_code": code}
    tool_result = setup_skill.invoke(tool_inputs)["tool_result"]
    messages_inputs = construct_test_skill_messages.invoke({"skill_repr": skill_repr, "tool_input": tool_inputs, "tool_result": tool_result})
    code_tester_agent = create_code_tester_agent(create_llm(config))
    code_tester_agent.tools[0] = config.code_interpreter
    test_result = code_tester_agent.invoke(messages_inputs)["messages"]
    return test_result


@runnable(run_name="ConstructRefactorSkillMessages")
def construct_refactor_skill_messages(conversation_history, refactor_type, skill_repr, skill_program_language, skill_code, user_request):
    messages = [
        {"role": "system", "content": f"Your action type is: {refactor_type}"},
        {"role": "function", "name": "show_skill", "content": skill_repr},
        {"role": "function", "name": "show_code", "content": f"current skill code:\n```{skill_program_language}\n{skill_code}\n```"},
        {"role": "user", "content": "{user_request}\nplease output only one skill object" if refactor_type in ("Combine", "Refine") else "\nplease help me decompose the skill object into different independent skill objects"}
    ]
    messages = conversation_history + [{"role": "system", "content": "Above context is conversation history from other agents. Now let's refactor our skill."}] + messages
    return {"messages": messages}


@runnable(run_name="RefactorSkill")
def refactor_skill(conversation_history, refactor_type, skill_program_language, skill_code, skill_repr, user_request):
    code_refactor_agent = create_code_refactor_agent(create_llm(config))
    chain = construct_refactor_skill_messages | code_refactor_agent
    refactored_skill_jsons = chain.invoke({
        "conversation_history": conversation_history,
        "refactor_type": refactor_type,
        "skill_repr": skill_repr,
        "skill_program_language": skill_program_language,
        "skill_code": skill_code,
        "user_request": user_request
    })["refacted_skills"]
    return refactored_skill_jsons


@runnable(run_name="AutoOptimizeSkill")
def auto_optimize_skill(old_skill, retry_times):
    skill = old_skill.model_copy(deep=True)
    refined = False
    conversation_history = [] if skill.conversation_history is None else skill.conversation_history
    for i in range(retry_times):
        if skill.test_summary is None:
            test_result = test_skill.invoke({
                "skill_program_language": skill.skill_program_language,
                "skill_dependencies": skill.skill_dependencies,
                "skill_code": skill.skill_code,
                "skill_repr": skill.skill_repr
            })
            conversation_history = conversation_history + test_result["messages"]
            if "test_summary" in test_result:
                test_summary = test_result["test_summary"]
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
