from typing import List
from creator.schema.skill import CodeSkillDependency, CodeSkill


def generate_skill_doc(skill: CodeSkill):
    if skill.skill_program_language == "python":
        return _generate_python_skill_doc(skill)
    # elif skill.skill_program_language == "R":
    #     return _generate_r_skill_doc(skill)
    # elif skill.skill_program_language == "javascript":
    #     return _generate_javascript_skill_doc(skill)
    # elif skill.skill_program_language == "shell":
    #     return _generate_shell_skill_doc(skill)
    # elif skill.skill_program_language == "applescript":
    #     return _generate_applescript_skill_doc(skill)
    # elif skill.skill_program_language == "html":
    #     return _generate_html_skill_doc(skill)
    else:
        raise NotImplementedError


def generate_language_suffix(language: str):
    if language == "python":
        return ".py"
    elif language == "R":
        return ".R"
    elif language == "javascript":
        return ".js"
    elif language == "shell":
        return ".sh"
    elif language == "applescript":
        return ".applescript"
    elif language == "html":
        return ".html"
    else:
        raise NotImplementedError


def generate_install_command(language: str, dependencies: List[CodeSkillDependency]):
    if language == "python":
        return _generate_python_install_command(dependencies)
    elif language == "R":
        return _generate_r_install_command(dependencies)
    elif language == "javascript":
        return _generate_javascript_install_command(dependencies)
    elif language == "shell":
        return _generate_shell_install_command(dependencies)
    elif language == "applescript":
        return _generate_applescript_install_command(dependencies)
    elif language == "html":
        return _generate_html_install_command(dependencies)
    else:
        raise NotImplementedError
    

def _generate_python_install_command(dependencies: List[CodeSkillDependency]):
    shell_command_str = 'pip show {package_name} || pip install "{package_name}'
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                if dep.dependency_version[:2] not in ("==", ">=", "<=", "!="):
                    shell_command += "==" + dep.dependency_version
                else:
                    shell_command += dep.dependency_version
            shell_command += '"'
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_r_install_command(dependencies: List[CodeSkillDependency]):
    shell_command_str = "Rscript -e 'if (!requireNamespace(\"{package_name}\", quietly = TRUE)) install.packages(\"{package_name}\")'"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "==" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_javascript_install_command(dependencies: List[CodeSkillDependency]):
    shell_command_str = "npm install {package_name}"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "@" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_shell_install_command(dependencies: List[CodeSkillDependency]):
    shell_command_str = "apt-get install {package_name}"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "=" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_applescript_install_command(dependencies: List[CodeSkillDependency]):
    shell_command_str = "osascript -e 'tell application \"Terminal\" to do script \"brew install {package_name}\"'"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "==" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_html_install_command(dependencies: List[CodeSkillDependency]):
    shell_command_str = "apt-get install {package_name}"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "=" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_python_skill_doc(skill: CodeSkill):
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
                doc += f"        Required: True\n"
            if param.param_default:
                doc += f"        Default: {param.param_default}\n"
    elif skill.skill_parameters:  # If it's a single CodeSkillParameter
        param = skill.skill_parameters
        doc += f"    {param.param_name} ({param.param_type}): {param.param_description}\n"
        if param.param_required:
            doc += f"        Required: True\n"
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

