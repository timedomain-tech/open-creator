import os
from creator.callbacks import OutputBufferStreamingHandler, RichTerminalStreamingHandler, FileLoggerStreamingHandler
from langchain.callbacks.manager import CallbackManager
from langchain.embeddings import OpenAIEmbeddings
from .chatopenai_with_trim import ChatOpenAIWithTrim, AzureChatOpenAIWithTrim


def create_llm(config):
    use_azure = True if os.getenv("OPENAI_API_TYPE", None) == "azure" else False

    model_name = config.model
    temperature = config.temperature
    streaming = config.use_stream_callback
    callbacks = [OutputBufferStreamingHandler()]
    if config.use_rich:
        callbacks.append(RichTerminalStreamingHandler())
    if config.use_file_logger:
        callbacks.append(FileLoggerStreamingHandler())
    if use_azure:
        llm = AzureChatOpenAIWithTrim(
            deployment_name=model_name,
            callback_manager=CallbackManager(handlers=callbacks) if streaming else None,
            temperature=temperature,
            streaming=streaming
        )
    else:
        llm = ChatOpenAIWithTrim(
            model_name=model_name,
            callback_manager=CallbackManager(handlers=callbacks) if streaming else None,
            temperature=temperature,
            streaming=streaming
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
