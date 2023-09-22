

def generate_skill_doc(skill):
    doc = f"""
# {skill.skill_name}
{'-' * len(skill.skill_name)}

{skill.skill_description}

# Version
{skill.skill_metadata.version}

# Usage:
{skill.skill_usage_example}

# Parameters:
"""
    # Handle skill_parameters
    if isinstance(skill.skill_parameters, list):
        for param in skill.skill_parameters:
            doc += f"    {param.param_name} ({param.param_type}): {param.param_description}\n"
            if param.param_required:
                doc += "        Required: True\n"
            if param.param_default:
                doc += f"        Default: {param.param_default}\n"
    elif skill.skill_parameters:  # If it's a single CodeSkillParameter
        param = skill.skill_parameters
        doc += f"    {param.param_name} ({param.param_type}): {param.param_description}\n"
        if param.param_required:
            doc += "        Required: True\n"
        if param.param_default:
            doc += f"        Default: {param.param_default}\n"

    # Handle skill_return
    doc += "\n# Returns:\n"
    if isinstance(skill.skill_return, list):
        for ret in skill.skill_return:
            doc += f"    {ret.param_name} ({ret.param_type}): {ret.param_description}\n"
    elif skill.skill_return:  # If it's a single CodeSkillParameter
        ret = skill.skill_return
        doc += f"    {ret.param_name} ({ret.param_type}): {ret.param_description}\n"

    return doc.strip()

