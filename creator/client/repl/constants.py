from prompt_toolkit.formatted_text import FormattedText


help_text = """
Open-Creator 0.1.2 - Build your costomized skill library
Type "%help" for more information. Pressing Ctrl-Q/Ctrl-D to exit
  ___                      ____                _             
 / _ \ _ __   ___ _ __    / ___|_ __ ___  __ _| |_ ___  _ __ 
| | | | '_ \ / _ \ '_ \  | |   | '__/ _ \/ _` | __/ _ \| '__|
| |_| | |_) |  __/ | | | | |___| | |  __/ (_| | || (_) | |   
 \___/| .__/ \___|_| |_|  \____|_|  \___|\__,_|\__\___/|_|   
      |_|                                                   
"""


prompt_message = FormattedText([
    ('class:prompt', 'creator'),
    ('', ' ◐ ')
])

prompt_prefix = "\n<prompt>creator</prompt> ◐ "

help_commands = """
# Entering Help Commands

- `%create`: Create a new skill from above conversation history
    - `-s` or `--save`: Save skill after creation

- `%save`: Save the skill
    - `-sp` or `--skill_path`: Path to skill JSON file
    - `-hf` or `--huggingface`: Huggingface repo ID

- `%search`: Search for a skill
    - `-q` or `--query`: Search query
    - `-k` or `--top_k`: Number of results to return, default 3

- `%exit`: Exit the CLI
- `%clear`: clear current skill cache and printed messages
- `%reset`: reset all messages and cached skills
- `%undo`: undo the last request
- `%help`: Print this help message
"""
