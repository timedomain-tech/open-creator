DEFAULT_PERSONA = """
The following is a blank slate starter persona, I need to expand this to develop my own personality.

My name is MemGPT.
I am kind, thoughtful, and inquisitive.
"""


DEFAULT_HUMAN = """
This is what I know so far about the user, I should expand this as I learn more about them.

First name: Chad
Last name: ?
Gender: Male
Age: ?
Nationality: ?
Occupation: Computer science PhD student at UC Berkeley
Interests: Formula 1, Sailing, Taste of the Himalayas Restaurant in Berkeley, CSGO
"""

DEFAULT_AGENT_SUBTASKS = """
    - create/save/search skill
    - run/test/refactor skill
    - show skill
"""

# the number of tokens consumed in a call before a system warning goes to the agent
MESSAGE_SUMMARY_WARNING_TOKENS = 6000
# Default memory limits
CORE_MEMORY_PERSONA_CHAR_LIMIT = 2000
CORE_MEMORY_HUMAN_CHAR_LIMIT = 2000

MESSAGE_SUMMARY_WARNING_STR = "Warning: the conversation history will soon reach its maximum length and be trimmed. Make sure to save any important information from the conversation to your memory before it is removed."
FUNC_FAILED_HEARTBEAT_MESSAGE = "Function call failed"
REQ_HEARTBEAT_MESSAGE = "request_heartbeat == true"

MESSAGE_CHATGPT_FUNCTION_MODEL = "gpt-3.5-turbo"
MESSAGE_CHATGPT_FUNCTION_SYSTEM_MESSAGE = "You are a helpful assistant. Keep your responses short and concise."
