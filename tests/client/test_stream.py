import streamlit as st
import time


container = st.container()

stream_container = container.empty()

code = "# hello world"

for i in range(len(code)):
    stream_container.markdown(code[:i+1])
    time.sleep(0.5)
