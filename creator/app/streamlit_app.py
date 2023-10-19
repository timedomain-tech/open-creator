import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

import streamlit as st
from creator.agents.creator_agent import open_creator_agent
from creator.agents import code_interpreter_agent
from creator import config
from langchain.callbacks.streamlit.streamlit_callback_handler import _convert_newlines
from langchain.output_parsers.json import parse_partial_json
from langchain.callbacks.streamlit.mutable_expander import MutableExpander
from langchain.adapters.openai import convert_message_to_dict
from loguru import logger
import os


st.title("OpenCreator Web Demo")

container = st.container()


def setup_slidebar():
    with st.sidebar:
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
        "[View the source code](https://github.com/timedomain-tech/open-creator/tree/main/creator/app/streamlit_app.py)"
        os.environ["OPENAI_API_KEY"] = openai_api_key
        model_list = ["gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-4"]
        model = st.selectbox("Model", model_list, key="model")
        config.model = model
        temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.05, key="temperature")
        config.temperature = temperature
        agent_list = ["creator_agent", "interpreter_agent"]
        agent = st.selectbox("Agent", agent_list, key="agent")
        if "agent" not in st.session_state:
            st.session_state["agent"] = agent

        if st.button("➕    New Chat", key="new_session"):
            add_session()


def add_session():
    agent_name = "creator_agent"
    if "agent" in st.session_state:
        agent_name = st.session_state["agent"]
    agent = open_creator_agent if agent_name == "creator_agent" else code_interpreter_agent

    session = {"title": "untitled", "messages": [], "agent": agent}
    st.session_state["sessions"].append(session)


def setup_state():
    logger.debug("setup_state-----------------------")
    if "sessions" not in st.session_state:
        st.session_state["sessions"] = []
        add_session()

    if "disabled" not in st.session_state:
        st.session_state["disabled"] = False

    if "langugae" not in st.session_state:
        st.session_state["language"] = "English"


def disable():
    st.session_state["disabled"] = True


def enable():
    st.session_state["disabled"] = False


def render_message(message, message_box, last_expander, last_str, last_expander_idx, content_box, content_box_index):
    content = message["content"] if message["content"] is not None else ""
    function_call = message.get('function_call', {})
    name = function_call.get("name", "")
    arguments = function_call.get("arguments", "")
    is_function_result = message["role"] == "function"
    language = ""
    code = ""
    if not name and not arguments and not content:
        return message_box, last_expander, last_str, last_expander_idx, content_box_index
    if len(name) > 0:
        if name in ("run_code", "python"):
            arguments_dict = parse_partial_json(arguments)
            if arguments_dict is not None:
                language = arguments_dict.get("language", "python")
                code = arguments_dict.get("code", "")
        else:
            language = "json"
            code = arguments

    render_content = content
    if not is_function_result and not code:
        content_box_index = content_box.markdown(body=render_content, index=content_box_index)
        return message_box, last_expander, last_str, last_expander_idx, content_box_index

    if last_expander is None:
        last_expander = MutableExpander(message_box, label=name, expanded=True)
        last_expander_idx = None

    if is_function_result:
        markdown = _convert_newlines(f"""{last_str}\n> STDOUT/STDERR\n```plaintext\n{render_content}\n```""")
        last_expander_idx = last_expander.markdown(body=markdown, index=last_expander_idx)

    if language and code:
        markdown = _convert_newlines(f"""```{language}\n{code}\n```""")
        last_str = markdown
        last_expander_idx = last_expander.markdown(body=markdown, index=last_expander_idx)

    return message_box, last_expander, last_str, last_expander_idx, content_box_index


def render_conversation_history(container, messages):
    last_message_box = None
    last_expander = None
    last_str = ""
    last_expander_idx = None
    content_box = None
    content_box_index = None
    for message in messages:
        role = message["role"]
        if role == "user":
            message_box = container.chat_message("user")
            content_box = MutableExpander(message_box, label="user", expanded=True)
            content_box_index = None
        elif role == "assistant":
            message_box = container.chat_message("assistant")
            content_box = MutableExpander(message_box, label="assistant", expanded=True)
            content_box_index = None
        else:
            message_box = last_message_box
        message_box, last_expander, last_str, last_expander_idx, content_box_index = render_message(message, message_box, last_expander, last_str, last_expander_idx, content_box, content_box_index)


def stream_render(agent, messages, container):
    message_box = None
    last_expander = None
    last_str = ""
    last_expander_idx = None
    content_box = None
    content_box_index = None
    index = 0
    for stop, (agent_name, (delta, full)) in agent.iter({"messages": messages}):
        if stop:
            # due to cache no stream output
            if index == 0:
                delta_messaes = full[len(messages):]
                render_conversation_history(container, delta_messaes)
            return full
        if delta is None and full is None:
            last_expander = None
            last_str = ""
            last_expander_idx = None
            message_box = container.chat_message("assistant")
            content_box = MutableExpander(message_box, label=agent_name, expanded=True)
            content_box_index = None
            continue
        message = convert_message_to_dict(full)
        message_box, last_expander, last_str, last_expander_idx, content_box_index = render_message(message, message_box, last_expander, last_str, last_expander_idx, content_box, content_box_index)
        if full.type != "function":
            index += 1


def handle_input():
    current_session = st.session_state["sessions"][-1]
    messages = current_session["messages"]

    if prompt := st.chat_input(on_submit=disable):
        messages.append({"role": "user", "content": prompt})
        print("current input messages", messages)
        render_conversation_history(container, messages)
        agent = current_session["agent"]
        return_messages = stream_render(agent, messages, container)
        current_session["messages"] = return_messages


setup_state()
setup_slidebar()
handle_input()
