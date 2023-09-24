"""
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

"""
refer to: https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor
use a creator agent that can select following actions:
1. create
2. save
3. search
4. additional meta prompt
    - exit
    - clear
    - resest
    - undo
    - help
tester, interpreter, extractor, and refactor agents are using differnt emoji
"""