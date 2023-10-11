from creator.callbacks import custom_message_box as cmb_module
import uuid
from loguru import logger
file_stack = []
code_file_stack = []
task_counters = {}

def message_start():
    global prev_message_length
    global prev_code_message_length

    prev_message_length = 0
    prev_code_message_length = 0

    
    # Determine the task level based on the current stack size
    task_level = len(file_stack) + 1
    
    # Increment the task counter for the current level or initialize it
    if task_level in task_counters:
        task_counters[task_level] += 1
    else:
        task_counters[task_level] = 1
    
    # Generate the filename based on the task level and counter
    filename = f"task_{task_level}_{task_counters[task_level]}.txt"
    code_filename = f"code_{task_level}_{task_counters[task_level]}.txt"
    
    # file = open(filename, 'w', encoding="utf-8")
    # code_file = open(code_filename, 'w', encoding="utf-8")
    # file_stack.append(file)
    # code_file_stack.append(code_file)

    file_stack.append(filename)
    code_file_stack.append(code_filename)


def message_update(message):
    # global prev_message_length
    
    if file_stack:  
        filename = file_stack[-1]  
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(message + '\n')

        # new_content = message[prev_message_length:]
        # file.write(new_content)
        logger.debug(f"message_update: {message}")
        # prev_message_length = len(message)

def code_message_update(message):
    global prev_code_message_length
    
    if code_file_stack:  
        # code_file = code_file_stack[-1]  
        # new_content = message[prev_code_message_length:]
        # code_file.write(new_content)
        # logger.debug(f"code_message_update: {new_content}")
        
        # prev_message_length = len(message)

        filename = code_file_stack[-1]  
        with open(filename, 'w', encoding="utf-8") as file:
            file.write(message + '\n')

def message_end():
    global prev_message_length
    global prev_code_message_length
    prev_message_length = 0
    prev_code_message_length = 0
    
    if file_stack:  
        file = file_stack.pop()  
        # file.close()
    if code_file_stack:  
        file = code_file_stack.pop()  

def add_file_callback():
    cmb_module.add_callback("start", message_start)
    cmb_module.add_callback("update", message_update)
    cmb_module.add_callback("update_code", code_message_update)
    cmb_module.add_callback("end", message_end)