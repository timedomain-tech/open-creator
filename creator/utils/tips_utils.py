

def remove_tips(messages):
    new_messages = []
    for m in messages:
        if m.content is None or not m.content.startswith("=== Tips"):
            new_messages.append(m)
    return new_messages
