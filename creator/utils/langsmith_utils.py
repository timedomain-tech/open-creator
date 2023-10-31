import os
from langsmith import Client
from langsmith.utils import LangSmithConnectionError
from printer import print


def check_langsmith_ok():
    cli = Client()
    if os.environ.get("LANGCHAIN_TRACING_V2", "false") == "false":
        return False
    try:
        cli.read_project(project_name="open-creator")
    except LangSmithConnectionError as e:
        if "Connection error" in str(e):
            print("[red]Warning:[/red] [yellow]Langsmith is not running. Please run `langsmith start`.[/yellow]")
            return False
        else:
            cli.create_project(project_name="open-creator")
    return True


langsmith_ok = check_langsmith_ok()
