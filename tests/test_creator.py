import sys
sys.path.append("..")
import creator


if __name__ == "__main__":
    # skill = creator.create(messages_json_path="./messages_example.json")
    # creator.save(skill)
    skill = creator.create(file_path="/Users/gongjunmin/LLM/open_creator_dev/open-interpreter/interpreter/code_interpreter.py")
    creator.save(skill)

