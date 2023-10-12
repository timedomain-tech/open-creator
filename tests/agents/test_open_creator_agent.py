import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

import creator
from creator.agents.creator_agent import open_creator_agent


def test_config_path():
    print(creator.config.build_in_skill_config)
    print(os.path.isdir(creator.config.build_in_skill_config["create"]))
    print(creator.config.model)


def test_run_create_skill():
    create_codeskill_obj = creator.create(skill_path=creator.config.build_in_skill_config["create"])
    messages = create_codeskill_obj.run("create a skill that request is 'open the chrome and go to www.google.com in my mac'")
    print(messages)


def test_run_creator_agent():
    messages = [
        {
            "role": "user", "content": "create a skill that request is 'open the chrome and go to www.google.com in my mac' and show the skill"
        }
    ]
    res = open_creator_agent.run({
        "messages": messages,
        "verbose": True,
    })
    print(res)


def test_run_creator_agent2():
    messages = [
        {
            "role": "user", "content": "create a skill that request is 'given a 4 digit sequence and output the solution of Game of 24 for example input is 1 1 2 12', show it and save it"
        }
    ]
    res = open_creator_agent.run({
        "messages": messages,
        "verbose": True,
    })
    print(res)


def test_run_creator_agent3():
    skill = creator.create(request="given a 4 digit sequence and output the solution of Game of 24. for example input is 1 1 2 12, use python as code language")
    skill.show()
    creator.save(skill)
    resp = skill.run("try 1 1 1 12")
    print(resp[-1])


def test_run_creator_agent4():
    messages = [
        {
            "role": "user", "content": "create a skill that request is 'given a 4 digit sequence and output the solution of Game of 24 for example input is 1 1 2 12', show it"
        }
    ]
    res = open_creator_agent.run({
        "messages": messages,
        "verbose": True,
    })
    print(res)
    res.append(
        {
            "role": "user",
            "content": "refine the skill and only retrun top 5 solutions (sorted and if has) if test ok (by showing the test summary), save it, otherwise do nothing"
        }
    )
    res = open_creator_agent.run({
        "messages": res,
        "verbose": True,
    })


def test_run_creator_agent5():
    messages = {"messages": [{"role": "user", "content": "Could you Please help me create one skill can open Google Chrome and search for 'openai' and 'chatgpt'"}], "verbose": True}
    res = open_creator_agent.run(messages)
    print(res)


if __name__ == "__main__":
    test_run_creator_agent5()
