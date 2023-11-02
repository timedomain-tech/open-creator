from langchain.schema.runnable import RunnableLambda
from langchain.callbacks import tracing_v2_enabled
from .printer import print
from .langsmith_utils import langsmith_ok


def runnable(run_name):
    def decorator(func):
        return RunnableLambda(func).with_config({"run_name": run_name})
    return decorator


def print_run_url(func):
    def wrapper(*args, **kwargs):
        if langsmith_ok:
            with tracing_v2_enabled() as cb:
                result = func(*args, **kwargs)
                run_url = cb.get_run_url()
                if run_url is not None:
                    print(f"Langsmith Run URL: [{run_url}]({run_url})", print_type="markdown")
        else:
            result = func(*args, **kwargs)
        return result
    return wrapper
