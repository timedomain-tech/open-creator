# modified from: https://github.com/KillianLucas/tokentrim/blob/main/tokentrim/tokentrim.py
# MIT license

import tiktoken
from typing import List, Dict, Any, Tuple, Optional, Union


MODEL_MAX_TOKENS = {
    'gpt-4': 8192,
    'gpt-4-0613': 8192,
    'gpt-4-32k': 32768,
    'gpt-4-32k-0613': 32768,
    'gpt-3.5-turbo': 4096,
    'gpt-3.5-turbo-16k': 16384,
    'gpt-3.5-turbo-0613': 4096,
    'gpt-3.5-turbo-16k-0613': 16384,
}


def num_tokens_from_messages(messages: List[Dict[str, Any]],
                             model) -> int:
    """
    Function to return the number of tokens used by a list of messages.
    """

    # Check the model name at the beginning
    if "gpt-3.5-turbo" in model:
        model = "gpt-3.5-turbo-0613"
    elif "gpt-4" in model:
        model = "gpt-4-0613"

    # Attempt to get the encoding for the specified model
    if model is None:
        encoding = tiktoken.get_encoding("cl100k_base")
    else:
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

    # Token handling specifics for different model types
    if model is None:
        # Slightly raised numbers for an unknown model / prompt template
        # In the future this should be customizable
        tokens_per_message = 4
        tokens_per_name = 2
    else:
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
        }:
            tokens_per_message = 3
            tokens_per_name = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4
            tokens_per_name = -1
        else:
            # Slightly raised numbers for an unknown model / prompt template
            # In the future this should be customizable
            tokens_per_message = 4
            tokens_per_name = 2

    # Calculate the number of tokens
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            try:
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
            except Exception as e:
                print(f"Failed to parse '{key}'. and raised {e}")
                pass

    num_tokens += 3
    return num_tokens


def shorten_message_to_fit_limit(message: Dict[str, Any], tokens_needed: int,
                                 model) -> None:
    """
    Shorten a message to fit within a token limit by removing characters from the middle.
    """

    content = message["content"]

    while True:
        total_tokens = num_tokens_from_messages([message], model)

        if total_tokens < tokens_needed:
            break
        
        ratio = tokens_needed / total_tokens

        new_length = int(total_tokens * ratio)

        half_length = new_length // 2
        left_half = content[:half_length]
        right_half = content[-half_length:]

        trimmed_content = left_half + '...' + right_half
        message["content"] = trimmed_content
        content = trimmed_content


def trim(
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        trim_ratio: float = 0.75,
        return_response_tokens: bool = False,
        max_tokens: Optional[int] = None) -> Union[List[Dict[str, Any]], Tuple[List[Dict[str, Any]], int]]:
    """
    Trim a list of messages to fit within a model's token limit.

    Args:
        messages: Input messages to be trimmed. Each message is a dictionary with 'role' and 'content'.
        model: The OpenAI model being used (determines the token limit).
        system_message: Optional system message to preserve at the start of the conversation.
        trim_ratio: Target ratio of tokens to use after trimming. Default is 0.75, meaning it will trim messages so they use about 75% of the model's token limit.
        return_response_tokens: If True, also return the number of tokens left available for the response after trimming.
        max_tokens: Instead of specifying a model or trim_ratio, you can specify this directly.

    Returns:
        Trimmed messages and optionally the number of tokens available for response.
    """

    # Initialize max_tokens
    if max_tokens is None:

        # Check if model is valid
        if model not in MODEL_MAX_TOKENS:
            raise ValueError(f"Invalid model: {model}. Specify max_tokens instead")

        max_tokens = int(MODEL_MAX_TOKENS[model] * trim_ratio)

    # Deduct the system message tokens from the max_tokens if system message exists
    if system_message:

        system_message_event = {"role": "system", "content": system_message}
        system_message_tokens = num_tokens_from_messages([system_message_event],
                                                         model)

        if system_message_tokens > max_tokens:
            print("`tokentrim`: Warning, system message exceeds token limit, which is probably undesired. Trimming...")

            shorten_message_to_fit_limit(system_message_event, max_tokens, model)
            system_message_tokens = num_tokens_from_messages([system_message_event],
                                                             model)

        max_tokens -= system_message_tokens

    final_messages = []

    # Reverse the messages so we process oldest messages first
    messages = messages[::-1]

    # Process the messages
    for message in messages:
        temp_messages = [message] + final_messages
        temp_messages_tokens = num_tokens_from_messages(temp_messages, model)

        if temp_messages_tokens <= max_tokens:
            # If adding the next message doesn't exceed the token limit, add it to final_messages
            final_messages = [message] + final_messages
        else:
            final_messages_tokens = num_tokens_from_messages(final_messages, model)
            tokens_remaining = max_tokens - final_messages_tokens

            # If adding the next message exceeds the token limit, try trimming it
            # (This only works for non-function call messages)
            if "function_call" not in message:
                shorten_message_to_fit_limit(message, tokens_remaining, model)

            # If the trimmed message can fit, add it
            if num_tokens_from_messages([message], model) + final_messages_tokens <= max_tokens:
                final_messages = [message] + final_messages

            break

    # Add system message to the start of final_messages if it exists
    if system_message:
        final_messages = [system_message_event] + final_messages

    if return_response_tokens:
        response_tokens = max_tokens - num_tokens_from_messages(
            final_messages, model)
        return final_messages, response_tokens

    return final_messages
