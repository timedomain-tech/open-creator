from .app import OpenCreatorREPL
from .handler import RequestHandler

handler = RequestHandler()

repl_app = OpenCreatorREPL(handler)


__all__ = ["repl_app"]
