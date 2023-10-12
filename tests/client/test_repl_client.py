import sys
import os
script_path = os.path.abspath(__file__)
sys.path.append(os.path.join(os.path.dirname(script_path), "../.."))

from creator.client.repl.app import OpenCreatorREPL
from creator.client.repl.handler import RequestHandler


handler = RequestHandler()

app = OpenCreatorREPL(handler)
app.run()
