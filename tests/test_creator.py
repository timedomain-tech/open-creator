import sys
sys.path.append("..")
import creator


if __name__ == "__main__":
    skill = creator.create(messages_json_path="./messages_example.json")
    creator.save(skill)

