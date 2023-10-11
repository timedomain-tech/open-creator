import sys
sys.path.append("..")

from creator.agents import code_interpreter_agent


def test_interpreter_agent():
    inputs = {
        "messages": [{'role': 'user', 'content': 'filter how many prime numbers are in 201'}]
    }
    messages = code_interpreter_agent.run(inputs)
    print(messages)


if __name__ == "__main__":
    test_interpreter_agent()

