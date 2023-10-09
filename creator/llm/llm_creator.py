import os
from creator.callbacks import FunctionCallStreamingStdOut
from langchain.callbacks.manager import CallbackManager
from langchain.embeddings import OpenAIEmbeddings
from .chatopenai_with_trim import ChatOpenAIWithTrim, AzureChatOpenAIWithTrim


def create_llm(**kwargs):
    use_azure = True if os.getenv("OPENAI_API_TYPE", None) == "azure" else False

    streaming = kwargs.get("streaming", True)
    model_name = kwargs.pop("model", None)
    if use_azure:
        llm = AzureChatOpenAIWithTrim(
            deployment_name=model_name, 
            callback_manager=CallbackManager(handlers=[FunctionCallStreamingStdOut()]) if streaming else None,
            **kwargs
        )
    else:
        llm = ChatOpenAIWithTrim(
            model_name=model_name,
            callback_manager=CallbackManager(handlers=[FunctionCallStreamingStdOut()]) if streaming else None,
            **kwargs
        )
    return llm


def create_embedding(**kwargs):
    
    use_azure = True if os.getenv("OPENAI_API_TYPE", None) == "azure" else False

    if use_azure:
        azure_model = os.getenv("EMBEDDING_DEPLOYMENT_NAME", None)
        print(azure_model)
        embedding = OpenAIEmbeddings(deployment=azure_model, model=azure_model)
    else:
        embedding = OpenAIEmbeddings()
        
    return embedding
