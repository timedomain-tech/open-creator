from langchain.schema.runnable import RunnableLambda


def runnable(run_name):
    def decorator(func):
        return RunnableLambda(func).with_config({"run_name": run_name})
    return decorator
