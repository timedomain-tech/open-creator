from creator.callbacks import FunctionCallStreamingStdOut
from langchain.callbacks.manager import CallbackManager
# from langchain.chat_models import ChatLiteLLM
from langchain.chat_models import ChatOpenAI, AzureChatOpenAI


def create_llm(**kwargs):
    use_azure = kwargs.pop("use_azure", False)
    streaming = kwargs.get("streaming", True)
    model_name = kwargs.pop("model", None)
    if use_azure:
        llm = AzureChatOpenAI(
            deployment_name=model_name,
            callback_manager=CallbackManager(handlers=[FunctionCallStreamingStdOut()]) if streaming else None,
            **kwargs
        )
    else:
        llm = ChatOpenAI(
            model_name=model_name,
            callback_manager=CallbackManager(handlers=[FunctionCallStreamingStdOut()]) if streaming else None,
            **kwargs
        )
    return llm

