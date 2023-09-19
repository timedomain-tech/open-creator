import sys
sys.path.append("..")
from creator.creator import Creator
import json


if __name__ == "__main__":
    skill = Creator.create(messages_json_path="./messages_example.json")
    Creator.save(skill)

