import sys
sys.path.append("..")
from creator.agents import code_interpreter_agent
from creator.utils import print


def main():
    messages = {"messages": [{"role": "user", "content": "Please help me open Google Chrome and search for openai chatgpt"}], "verbose": True}
    for stop, item in code_interpreter_agent.iter(messages):
        if stop:
            print(item, print_type="json")
            break
        print(f"delta/output: {item}")


if __name__ == "__main__":
    main()

