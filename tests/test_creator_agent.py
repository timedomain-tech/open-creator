import sys
sys.path.append("../")

import creator
from creator.agents.creator_agent import open_creator_agent
import os


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
            "role": "user", "content": "create a skill that request is 'given a 4 digit sequence and output the solution of Game of 24', save it, test it and show it"
        }
    ]
    res = open_creator_agent.run({
        "messages": messages,
        "verbose": True,
    })
    print(res)

# TODO: fix no stdout problem


if __name__ == "__main__":
    test_run_creator_agent2()
