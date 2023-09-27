import sys
sys.path.append("..")

from creator.config.library import config
import creator


if __name__ == "__main__":
    print(config)
    
    config.build_in_skill_config = {
        "test": "A"
    }
    print(creator.config.build_in_skill_config)

    creator.config.build_in_skill_config = {
        "test": "B"
    }
    print(config.build_in_skill_config)