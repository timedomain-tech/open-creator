import os
import shutil
import appdirs
import yaml
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


def load_yaml_config():
    """
    Load the configuration from a YAML file.
    
    If the config file doesn't exist in the user's directory, it copies the default from the project directory.
    
    Returns:
        dict: The loaded YAML configuration.
    """
    # Determine the current file's directory
    current_file_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the project config path using a relative path from the current file's directory
    project_config_path = os.path.join(current_file_dir, '..', 'config.yaml')
    project_config_path = os.path.normpath(project_config_path)

    # Determine user data directory
    user_config_dir = appdirs.user_config_dir('Open-Creator', appauthor=False)
    if not os.path.exists(user_config_dir):
        os.makedirs(user_config_dir)

    user_config_path = os.path.join(user_config_dir, 'config.yaml')

    # Check if config file exists in user data directory, if not, copy from project path
    if not os.path.exists(user_config_path):
        shutil.copy(project_config_path, user_config_path)

    # Load YAML config file using the new path
    with open(user_config_path, 'r') as file:
        yaml_config = yaml.safe_load(file)
    
    # env vs yaml, yaml first if not empty
    for key, value in yaml_config.items():
        if os.environ.get(key) and not value:
            yaml_config[key] = os.environ.get(key)
        # if yaml has some configs that env does not, write to env
        if not os.environ.get(key) and value:
            os.environ[key] = str(value)

    return yaml_config

