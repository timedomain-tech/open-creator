import sys 
sys.path.append("..")


from creator.client.repl.app import OpenCreatorREPL
from creator.client.repl.handler import RequestHandler


handler = RequestHandler()

app = OpenCreatorREPL(handler)
app.run()
