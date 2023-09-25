import sys
sys.path.append("..")

from creator.utils import load_yaml_config


config = load_yaml_config()

print(config)

