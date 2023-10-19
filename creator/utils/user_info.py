import getpass
import os
import platform


def get_user_info():
    user_info = """
[User Info]
Name: {username}
CWD: {current_working_directory}
OS: {operating_system}
"""
    username = getpass.getuser()
    current_working_directory = os.getcwd()
    operating_system = platform.system()
    return user_info.format(
        username=username,
        current_working_directory=current_working_directory,
        operating_system=operating_system
    )