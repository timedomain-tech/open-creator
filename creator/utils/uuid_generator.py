import hashlib


def generate_uuid_like_string(text):
    """
    Generates a UUID-like string based on the given text.

    The function uses the SHA-256 hash function to hash the input text.
    It then extracts 32 characters from the hash result and formats
    them to mimic the structure of a UUID.

    Parameters:
    text (str): The input text to be hashed and converted into a UUID-like string.

    Returns:
    str: A UUID-like string derived from the input text.
    """
    # Use the SHA-256 hash function to hash the input text
    hash_object = hashlib.sha256(text.encode())
    hex_dig = hash_object.hexdigest()

    # Extract 32 characters from the hash result and add separators to mimic the UUID format
    return f"{hex_dig[:8]}-{hex_dig[8:12]}-{hex_dig[12:16]}-{hex_dig[16:20]}-{hex_dig[20:32]}"
