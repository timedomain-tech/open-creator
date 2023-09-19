import sys
sys.path.append("..")
from creator.creator import Creator
import json


if __name__ == "__main__":
    creator = Creator()
    skill = creator.create(messages_json_path="./messages_example.json")
    
