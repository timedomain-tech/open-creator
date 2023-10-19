def load_system_prompt(prompt_path):
    with open(prompt_path, encoding='utf-8') as f:
        prompt = f.read()
    return prompt
