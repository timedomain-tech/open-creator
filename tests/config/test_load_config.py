import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from creator.utils import load_yaml_config


config = load_yaml_config()

print(config)

