import sys
sys.path.append("../")

import creator
import os


def test_config_path():
    print(creator.config.build_in_skill_config)
    print(os.path.isdir(creator.config.build_in_skill_config["create"]))
    print(creator.config.model)


def test_run_create_skill():
    create_skill = creator.create(skill_path=creator.config.build_in_skill_config["create"])
    skill = create_skill.run("create a skill that request is 'open the chrome and go to www.google.com in my mac'")
    print(repr(skill))

if __name__ == "__main__":
    test_run_create_skill()
