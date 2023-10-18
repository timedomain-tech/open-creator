import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from creator.llm.tokentrim import trim


# Test the refactored trim function with sample messages
sample_messages = [
    {"role": "user", "content": "Hello, world! This is a very long message that we want to trim to fit within the model's token limit."},
    {"role": "system", "content": "System message that should not be trimmed."},
    {"role": "user", "content": "Another user message."}
]
return_messages = trim(sample_messages, 'gpt-4', max_tokens=15)
print(return_messages)
