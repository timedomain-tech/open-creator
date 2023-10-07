def load_system_prompt(prompt_path):
    with open(prompt_path) as f:
        prompt = f.read()
    return prompt
