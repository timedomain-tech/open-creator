import sys
sys.path.append("../")

import creator
import os


if __name__ == "__main__":
    print(creator.config.build_in_skill_config)
    print(os.path.isdir(creator.config.build_in_skill_config["create"]))
    print()
    print(creator.config.model)