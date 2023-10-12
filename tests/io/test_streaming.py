import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from creator.agents import code_interpreter_agent
from creator.agents.creator_agent import open_creator_agent
from creator.utils import print


def test_interpreter_agent():
    messages = {"messages": [{"role": "user", "content": "Please help me open Google Chrome and search for openai chatgpt"}], "verbose": True}
    for stop, item in code_interpreter_agent.iter(messages):
        if stop:
            print(item, print_type="json")
            break
        print(f"delta/output: {item}")


def test_creator_agent():
    messages = {"messages": [{"role": "user", "content": "Please help me create a skill can open Google Chrome and search for openai"}], "verbose": True}
    for stop, item in open_creator_agent.iter(messages):
        if stop:
            print(item, print_type="json")
            break
        if item[0] == "CreatorAgent":
            print(f"delta/output: {item}")


if __name__ == "__main__":
    test_creator_agent()

