from langchain.callbacks.streamlit.mutable_expander import MutableExpander

import streamlit as st
import time


container = st.container()

message = container.chat_message(name="ai")

message.write('# hello wolrd')

expander = MutableExpander(message, label='run_code', expanded=True)


tool_inputs = """
```python\nimport streamlit as st\n\nst.markdown('''Happy Streamlit-ing! :balloon:''')\ndef hello():
    print("hello world")
```

"""

index = None

for i in range(len(tool_inputs)):
    time.sleep(0.01)
    index = expander.markdown(tool_inputs[:i], index=index)

tool_result = """
> STDOUT/STDERR
```plaintext
{"status": "success", "stdout": "", "stderr": ""}
```
"""


index = expander.markdown(tool_inputs+tool_result, index=index)


message = container.chat_message(name="ai")

message.write('the code run successfully')

