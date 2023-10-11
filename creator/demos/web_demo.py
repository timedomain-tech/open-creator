from loguru import logger
import streamlit as st
import time
import sys
from random import randint
import time
import os
import asyncio
import json
import aiohttp
import threading
import queue
import requests

sys.path.append("..")
import creator
from rich.markdown import Markdown
from creator.callbacks import custom_message_box as cmb_module


help_message_en = """
The open-creator contains three components: **create**, **save**, **search**. \n
The specific command parameters of each component can be viewed by `creator create|save|search -h`, e.g. `creator create -h`. \n

In the current demo, the system will automatically recognize and execute the corresponding component, if necessary, you can use the command to force the use of the corresponding component. \n
"""

help_message_zh = """
open-creator包含三个组件：**create**, **save**, **search**。\n
每个组件的具体指令参数可以通过`creator create|save|search -h`来查看，比如`creator create -h`。\n

在当前demo中，系统会自动识别并执行对应组件，如果有需要可以使用指令强制使用对应组件。\n
"""

init_message_en = f"""
Welcome to experience the WebDemo of [OpenCreator](https://github.com/timedomain-tech/open-creator), which will show you various uses of OpenCreator. \n
Currently existing agents still face challenges in persisting, sharing, and updating skill repositories, so we propose open-creator, a brand new framework designed to help AI agents better unify the extraction, testing, and refactoring of skills from a variety of sources. \n
open-creator consists of the following key components:
```
1. creation: extracting specific skills through dialog interactions with users.
2. Save: persists skills to be saved locally or in the cloud.
3. search: find and use the most relevant skills on demand.
4. push/pull: allow users to share their skills, which in turn enhances the knowledge base of the entire community.
```
{help_message_en}

Welcome to join the community discussion at: [Discord](https://discord.gg/xvueEJ2Rt)\n
To search and share skills visit: [Skill Library Hub](https://huggingface.co/spaces/timedomain/skill-library-hub)\n
So, what can I do to help you?
"""

init_message_zh = f"""
欢迎体验[OpenCreator](https://github.com/timedomain-tech/open-creator)的WebDemo，该Demo将向您展示OpenCreator的各种用法。\n
当前存在的agent在技能库的持久化、共享和更新方面仍然面临挑战，因此我们提出了open-creator，一个全新的框架，旨在帮助AI代理更好地从各种来源统一技能的抽取、测试和重构。\n
open-creator主要包括以下几个关键部分：
```
1. 创建：通过与用户的对话交互，抽取特定的技能。
2. 保存：持久化技能，在本地或云端进行保存。
3. 搜索：根据需求查找和使用最相关的技能。
4. 推送/拉取：允许用户分享他们的技能，进而增强整个社区的知识库。
```
{help_message_zh}

欢迎加入社群讨论：[Discord](https://discord.gg/xvueEJ2Rt)\n
搜索与共享技能请访问：[Skill Library Hub](https://huggingface.co/spaces/timedomain/skill-library-hub)\n
那么，有什么是我可以帮助你的呢？
"""

def setup_slidebar():
    with st.sidebar:
        st.title("🎈 Open Creator")
        with st.expander("🌐 Language", True):
            language = st.radio(
                "languae",
                ["English", "Chinese"],
                index=0,
                label_visibility="collapsed"
            )
            st.session_state.messages[0]["content"] = init_message_en if language == "English" else init_message_zh
        with st.expander("🔧 Config", True):
            st.write("Coming soon...")

def setup_state():
    logger.debug("setup_state-----------------------")

    if "should_rerun" not in st.session_state:
        st.session_state.should_rerun = False
    if "server_message" not in st.session_state:
        st.session_state.server_message = ""
    if "reply_message" not in st.session_state:
        st.session_state.reply_message = ""
    if "conversation" not in st.session_state:
        st.session_state.conversation = []
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": init_message_en}]
    if "disabled" not in st.session_state:
        st.session_state["disabled"] = False


    # if st.session_state.message_id is not None:
    #     message_id = st.session_state.message_id
    #     response = requests.get(f"http://localhost:8001/message/{message_id}")
    #     logger.success(f"response: {response.json()} ")
    #     response_data = response.json()
    #     reply(response_data)
    #     if response_data["is_end"]:
    #         st.session_state.message_id = None

def display_messages():
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if i==0:
                with st.expander("Info", True):
                    st.markdown(message["content"])
            else:
                st.markdown(message["content"])

def disable():
    st.session_state["disabled"] = True

def enable():
    st.session_state["disabled"] = False

def reply(message):
    logger.debug(f"reply: {message}")
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = message
        message_placeholder.markdown(full_response)
        st.markdown(message)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        enable()
        st.rerun()

def handle_input():
    if prompt:= st.chat_input("What is up?", disabled=st.session_state.disabled, on_submit=disable):#
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation.append({"role":"user", "content": prompt})
        
        if prompt == "-h":
            assistant_response = help_message_en if language == "English" else help_message_zh
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        elif prompt == "-n":
            assistant_response = init_message_en if language == "English" else init_message_zh
            st.session_state.messages = [{"role": "assistant", "content": assistant_response}]
            st.session_state.conversation = []
        else:
            user_message = json.dumps(st.session_state.conversation, ensure_ascii=False)
            response = requests.post("http://localhost:8001/message", json={"content": user_message})
            logger.debug(f"response: {response.json()}")
            st.session_state.message_id = response.json()["id"]
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_id = st.session_state.message_id
                while True:
                    if "message_id" in st.session_state and st.session_state.message_id is not None:
                        logger.debug(f"start get response")
                        response = requests.get(f"http://localhost:8001/message/{message_id}")
                        logger.debug(f"get response")
                        response_data = response.json()
                        is_end = response_data["is_end"]
                        json_data = response_data["content"]
                        if json_data is not None and json_data != "":
                            array = json.loads(json_data)
                            if isinstance(array, str):
                                full_response = array
                            else:
                                for message in array:
                                    full_response+=message+"\n"

                            logger.success(f"response: {full_response} is_end: {is_end}")
                            message_placeholder.markdown(full_response)

                        if response_data["is_end"]:
                            st.session_state.message_id = None
                            st.session_state.messages.append({"role": "assistant", "content": full_response})
                            st.session_state.conversation.append({"role":"assistant", "content": full_response})
                            enable()
                            st.rerun()
                            return
                        time.sleep(0.01)
                    else:
                        time.sleep(0.01)
                    

            
setup_state()
st.title("OpenCreator Web Demo")
language = "English"
setup_slidebar()
display_messages()
handle_input()


