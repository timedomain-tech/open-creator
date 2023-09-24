

def generate_install_command(language: str, dependencies):
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
    

def _generate_python_install_command(dependencies):
    shell_command_str = 'pip show {package_name} || pip install "{package_name}'
    commands = []
    if not isinstance(dependencies, list):
        dependencies = [dependencies]
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


def _generate_r_install_command(dependencies):
    shell_command_str = "Rscript -e 'if (!requireNamespace(\"{package_name}\", quietly = TRUE)) install.packages(\"{package_name}\")'"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "==" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_javascript_install_command(dependencies):
    shell_command_str = "npm install {package_name}"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "@" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_shell_install_command(dependencies):
    shell_command_str = "apt-get install {package_name}"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "=" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_applescript_install_command(dependencies):
    shell_command_str = "osascript -e 'tell application \"Terminal\" to do script \"brew install {package_name}\"'"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "==" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)


def _generate_html_install_command(dependencies):
    shell_command_str = "apt-get install {package_name}"
    commands = []
    for dep in dependencies:
        if dep.dependency_type == "package":
            shell_command = shell_command_str.format(package_name=dep.dependency_name)
            if dep.dependency_version:
                shell_command += "=" + dep.dependency_version
            commands.append(shell_command)
    return "\n".join(commands)
