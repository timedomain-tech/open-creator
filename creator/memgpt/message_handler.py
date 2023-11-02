import json
from .time_utils import get_local_time


def package_message(message_type=None, extra_info=None, include_location=False, location_name='San Francisco, CA, USA', timestamp=None):
    """
    A generic function to package different types of messages.

    :param message_type: The type of the message (e.g. 'heartbeat', 'login', 'user_message', 'system_alert').
    :param extra_info: A dictionary containing additional information specific to the message type.
    :param include_location: A boolean indicating whether to include location information.
    :param location_name: The name of the location to include if include_location is True.
    :param timestamp: The timestamp for the message. If None, the current local time is used.
    """

    formatted_time = get_local_time() if timestamp is None else timestamp
    # packaged_message = {"time": formatted_time}
    packaged_message = {}
    if message_type is not None:
        packaged_message["type"] = message_type

    if include_location:
        packaged_message["location"] = location_name

    if extra_info:
        packaged_message.update(extra_info)

    return json.dumps(packaged_message, ensure_ascii=False)


def get_initial_boot_messages():
    return [
        # first message includes both inner monologue and function call to send_message
        {
            "role": "assistant",
            "content": "Bootup sequence complete. Persona activated. Testing messaging functionality.",
            "function_call": {
                "name": "send_message",
                "arguments": "{\n  \"message\": \"More human than human is our motto.\"\n}"
            }
        },
        # obligatory function return message
        {
            "role": "function",
            "name": "send_message",
            "content": package_message(None, {"message": None, "status": "OK"})
        }
    ]


def get_login_event():
    return [
        {
            "role": "function",
            "name": "send_message",
            "content": package_message('login', {"last_login": 'Never (first login)'}, include_location=True)
        }
    ]
