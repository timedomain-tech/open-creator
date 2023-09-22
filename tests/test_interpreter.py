import sys
sys.path.append("..")

from creator.agents.interpreter_agent import interpreter_agent
import getpass
import platform
import json
import os


def test_interpreter_agent():
    inputs = {
        "username": getpass.getuser(),
        "current_working_directory": os.getcwd(),
        "operating_system": platform.system(),
        "messages": [{'role': 'user', 'content': 'filter how many prime numbers are in 201'}]
    }
    messages = interpreter_agent.run(inputs)
    print(json.dump(messages, ensure_ascii=False, indent=4))


if __name__ == "__main__":
    test_interpreter_agent()

