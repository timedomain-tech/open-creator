import tiktoken
from typing import List, Dict, Any, Optional


# Define model configurations in a centralized location
MODEL_CONFIGS = {
    'gpt-4': {
        'max_tokens': 8192,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    },
    'gpt-4-0613': {
        'max_tokens': 8192,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    },
    'gpt-4-32k': {
        'max_tokens': 32768,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    },
    'gpt-4-32k-0613': {
        'max_tokens': 32768,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    },
    'gpt-3.5-turbo': {
        'max_tokens': 4096,
        'tokens_per_message': 4,
        'tokens_per_name': 2
    },
    'gpt-3.5-turbo-16k': {
        'max_tokens': 16384,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    },
    'gpt-3.5-turbo-0613': {
        'max_tokens': 4096,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    },
    'gpt-3.5-turbo-16k-0613': {
        'max_tokens': 16384,
        'tokens_per_message': 3,
        'tokens_per_name': 1
    }
}

# Default configuration
DEFAULT_CONFIG = {
    'max_tokens': 4096,
    'tokens_per_message': 4,
    'tokens_per_name': 2
}


# Extracted helper functions
def get_encoding_for_model(model: Optional[str]) -> Any:
    """
    Get the encoding for the specified model.
    """
    if model is None or model not in MODEL_CONFIGS:
        return tiktoken.get_encoding("cl100k_base")

    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def get_model_config(model: Optional[str]) -> Dict[str, int]:
    """
    Get the configuration for the specified model.
    """
    if model in MODEL_CONFIGS:
        return MODEL_CONFIGS[model]
    return DEFAULT_CONFIG


def tokens_for_message(message: Dict[str, Any], encoding: Any, config: Dict[str, int]) -> int:
    """
    Calculate the number of tokens for a single message.
    """
    num_tokens = config['tokens_per_message']
    
    for key, value in message.items():
        try:
            num_tokens += len(encoding.encode(str(value)))
            if key == "name":
                num_tokens += config['tokens_per_name']
        except Exception as e:
            print(f"Failed to parse '{key}'. and raised {e}")
            pass

    return num_tokens


# Refactored main function
def num_tokens_from_messages(messages: List[Dict[str, Any]], model: Optional[str] = None) -> int:
    """
    Function to return the number of tokens used by a list of messages.
    """
    encoding = get_encoding_for_model(model)
    config = get_model_config(model)

    return sum(tokens_for_message(message, encoding, config) for message in messages) + 3


# Helper function to trim a single message
def trim_single_message(message: Dict[str, Any], to_trim_tokens: int) -> None:
    """
    Shorten a message to fit within a token limit by removing characters from the middle.
    """
    content = message["content"]
    function_call = message.get("function_call", None)
    if content:
        to_trim_tokens += 8  # for the ellipsis and the <content-trimmed> tag
        half_length = len(content) // 2
        left_half = content[:half_length-to_trim_tokens//2]
        right_half = content[half_length+to_trim_tokens//2:]
        new_content = left_half + "...<content-trimmed>..." + right_half
        message["content"] = new_content
    elif function_call:
        arguments = function_call["arguments"]
        half_length = len(arguments) // 2
        left_half = arguments[:half_length-to_trim_tokens//2]
        right_half = arguments[half_length+to_trim_tokens//2:]
        new_arguments = left_half + "...<arguments-trimmed>..." + right_half
        function_call["arguments"] = new_arguments
        message["function_call"] = function_call
    return message


def trim(
    messages: List[Dict[str, Any]],
    model: Optional[str] = None,
    trim_ratio: float = 0.75,
    max_tokens: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Trim a list of messages to fit within a model's token limit.
    """
    if not messages:
        return messages

    # Initialize max_tokens
    if max_tokens is None:
        config = get_model_config(model)
        max_tokens = int(config['max_tokens'] * trim_ratio)

    total_tokens = num_tokens_from_messages(messages, model)
    if total_tokens <= max_tokens:
        return messages

    # Deduct the system message tokens from the max_tokens if system message exists
    system_messages = [msg for msg in messages if msg["role"] == "system"]
    system_message_tokens = num_tokens_from_messages(system_messages, model)

    available_tokens = max_tokens - system_message_tokens

    if available_tokens < 0:
        print("`tokentrim`: Warning, system message exceeds token limit. Trimming...")
        curr_tokens = total_tokens

        trimmed_messages = []
        for idx, message in enumerate(messages):
            msg_tokens = num_tokens_from_messages([message], model)
            if curr_tokens - msg_tokens > max_tokens:
                curr_tokens -= msg_tokens
            else:
                to_trim_tokens = max_tokens - (curr_tokens - msg_tokens)
                message = trim_single_message(message, to_trim_tokens)
                trimmed_messages.append(message)
                trimmed_messages.extend(messages[idx+1:])
                break
        return trimmed_messages

    # trim except system messages
    idx = 0
    removed_idxs = set()
    while idx < len(messages):
        if messages[idx]["role"] == "system":
            idx += 1
            continue
        msg_tokens = num_tokens_from_messages([messages[idx]], model)
        if available_tokens - msg_tokens > max_tokens:
            available_tokens -= msg_tokens
            removed_idxs.add(idx)
            idx += 1
        else:
            to_trim_tokens = msg_tokens - (available_tokens - msg_tokens)
            messages[idx] = trim_single_message(messages[idx], to_trim_tokens)
            idx += 1
            break

    return [msg for i, msg in enumerate(messages) if i not in removed_idxs]
