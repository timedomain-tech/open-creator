import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

import creator


if __name__ == "__main__":
    skill = creator.create(skill_path="/Users/gongjunmin/.cache/open_creator/skill_library/solve_game_of_24")
    optimized_skill = skill.auto_optimize()
    optimized_skill.show()
    creator.save(skill=optimized_skill, skill_path="./solve_game_of_24")
