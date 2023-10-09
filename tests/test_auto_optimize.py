import sys
sys.path.append("..")

import creator


if __name__ == "__main__":
    skill = creator.create(skill_path="/Users/gongjunmin/.cache/open_creator/skill_library/solve_game_of_24")
    optimized_skill = skill.auto_optimize()
    optimized_skill.show()
    creator.save(skill=optimized_skill, skill_path="./solve_game_of_24")
