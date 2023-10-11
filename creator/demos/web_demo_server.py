from loguru import logger
from creator.callbacks import custom_message_box as cmb_module
from creator.callbacks.file_callback import add_file_callback
from fastapi import FastAPI, BackgroundTasks
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from creator.agents.creator_agent import open_creator_agent
import json
from fastapi.responses import StreamingResponse
from typing import Generator
import uuid
import time
import queue

messages = {}
def set_reply_message(message):
    global current_message_id
    global messages
    if current_message_id in messages:
        if len(messages[current_message_id]) == 0:
            messages[current_message_id].append("")
        messages[current_message_id][-1] = message
        # logger.debug(f"set_reply_message: {message}\n{messages[current_message_id][-1]}")
    else:
        messages[current_message_id] = [message]



is_message_end = False

def message_end():
    global current_message_id
    global messages
    if current_message_id in messages:
        messages[current_message_id].append("")

def message_start():
    global current_message_id
    global messages
    if current_message_id in messages:
        messages[current_message_id].append("")
    else:
        messages[current_message_id] = [""]
    

cmb_module.add_callback("start", message_start)
cmb_module.add_callback("update", set_reply_message)
cmb_module.add_callback("end", message_end)
add_file_callback()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    content: str

processing_messages = {}

current_message_id = None
current_message_id_lock = asyncio.Lock()

async def process_message():
    global current_message_id
    global is_message_end
    global messages
    while True:
        async with current_message_id_lock:
            # logger.success(f"current_message_id_lock: {current_message_id}")
            if current_message_id is not None and messages is not None and current_message_id in messages:
                json_data = json.dumps(messages[current_message_id])
                processing_messages[current_message_id]["content"] = json_data
                # result = processing_messages[current_message_id]["content"]
                # logger.success(f"result: {result}")
                if is_message_end:
                    processing_messages[current_message_id]["is_end"] = True
                    is_message_end = False
                    current_message_id = None
                await asyncio.sleep(0.1)
            else:
                await asyncio.sleep(1)

@app.on_event("startup")
async def on_startup():
    logger.debug("on_startup: Creating process_message task")
    asyncio.create_task(process_message())

def process_messages(json_data):
    global current_message_id
    global is_message_end
    global messages
    result = open_creator_agent.run({
        "messages": json_data,
        "verbose": True,
    })
    if result is not None:
        messages[current_message_id] = result[-1]["content"]
        is_message_end = True

@app.post("/message")
async def post_message_endpoint(message: Message, background_tasks: BackgroundTasks):
    global current_message_id
    message_id = str(uuid.uuid4())
    processing_messages[message_id] = {"content": "", "is_end": False}
    
    async with current_message_id_lock:
        current_message_id=message_id

    json_data = json.loads(message.content)
    background_tasks.add_task(process_messages, json_data)
    return {"id": message_id}


@app.get("/message/{message_id}")
async def get_message_endpoint(message_id: str):
    return processing_messages.get(message_id, {"content": "Not found", "is_end": True})

