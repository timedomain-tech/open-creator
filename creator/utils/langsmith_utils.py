from langsmith import Client
from langsmith.utils import LangSmithError
from .printer import print


def check_langsmith_ok():
    cli = Client()
    ok = False
    try:
        cli.read_project(project_name="open-creator")
    except LangSmithError as e:
        if "Bad Gateway" in str(e):
            print("[red]Warning:[/red] [yellow]Langsmith is not running. Please run `langsmith start`.[/yellow]")
            return ok
        else:
            cli.create_project(project_name="open-creator")
    ok = True
    return ok


langsmith_ok = check_langsmith_ok()
