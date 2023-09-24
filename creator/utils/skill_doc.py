

def generate_skill_doc(skill):
    def format_parameter(param):
        """Helper function to format a parameter for markdown."""
        details = [f"   - **{param.param_name}** ({param.param_type}): {param.param_description}"]
        if param.param_required:
            details.append("        - Required: True")
        if param.param_default:
            details.append(f"      - Default: {param.param_default}")
        return "\n".join(details)

    def format_return(ret):
        """Helper function to format a return for markdown."""
        return f"   - **{ret.param_name}** ({ret.param_type}): {ret.param_description}"

    doc = f"""## Skill Details:
- **Name**: {skill.skill_name}
- **Description**: {skill.skill_description}
- **Version**: {skill.skill_metadata.version}
- **Usage**:
```{skill.skill_program_language}
{skill.skill_usage_example}
```
- **Parameters**:
"""
    # Handle skill_parameters
    if isinstance(skill.skill_parameters, list):
        for param in skill.skill_parameters:
            doc += format_parameter(param) + "\n"
    elif skill.skill_parameters:  # If it's a single CodeSkillParameter
        doc += format_parameter(skill.skill_parameters) + "\n"
    
    doc += "\n- **Returns**:\n"

    if isinstance(skill.skill_return, list):
        for ret in skill.skill_return:
            doc += format_return(ret) + "\n"
    elif skill.skill_return:  # If it's a single CodeSkillParameter
        doc += format_return(skill.skill_return) + "\n"

    return doc.strip()

