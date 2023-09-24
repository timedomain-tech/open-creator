from creator.utils.skill_doc import generate_skill_doc


class Refactorable:
    skills_to_combine: list = []
    user_request: str = "please help me refine the skill object"
    refactor_type: str = "refine"

    def __add__(self, other_skill):
        assert isinstance(other_skill, type(self)), f"Cannot combine {type(self)} with {type(other_skill)}"
        # If the list is empty, add the current object to it
        if not self.skills_to_combine:
            self.skills_to_combine.append(self)
        
        # Add the other_skill to the list
        self.skills_to_combine.append(other_skill)
        
        return self  # Return the current object to support continuous addition
    
    def __radd__(self, other_skill):
        self.__add__(other_skill)

    def __lt__(self, user_request:str):
        self.user_request = user_request
        self.refactor_type = "decompose"

    def __gt__(self, user_request:str):
        self.user_request = user_request
        self.refactor_type = "combine"

    def refactor(self, code_refactor_agent):
        refactor_skills = []
        if len(self.skills_to_combine) == 0:
            refactor_skills.append(self)
        else:
            refactor_skills = self.skills_to_combine

        num_output_skills = "one" if self.refactor_type != "decompose" else "appropriate number of"
        messages = [{
            "role": "system",
            "content": f"Your refactor type is: {self.refactor_type} and output {num_output_skills} skill object(s)"
        }]
        for refactor_skill in refactor_skills:
            messages.append(
                {
                    "role": "function",
                    "name": "get_skill",
                    "content": refactor_skill.model_dump_json()
                }
            )
        messages.append({
            "role": "user",
            "content": self.user_request
        })
        refactored_skill_jsons = code_refactor_agent.run(
            {
                "messages": messages,
                "verbose": True,
            }
        )
        parent_class = refactor_skills[0].__class__.__bases__[0]
        refactored_skills = []
        for refactored_skill_json in refactored_skill_jsons:
            refactored_skills.append(parent_class(**refactored_skill_json))

        return refactored_skills
    
    def __repr__(self):
        if len(self.skills_to_combine) == 0:
            self.skills_to_combine.append(self)
        skill_docs = []
        for skill in self.skills_to_combine:
            skill_docs.append(generate_skill_doc(skill))
        return "\n---\n".join(skill_docs)

