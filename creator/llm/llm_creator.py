import os
from creator.callbacks import OutputBufferStreamingHandler, RichTerminalStreamingHandler, FileLoggerStreamingHandler
from langchain.callbacks.manager import CallbackManager
from .chatllm_with_trim import ChatOpenAIWithTrim, AzureChatOpenAIWithTrim


def create_llm(config, model=None):
    use_azure = True if os.getenv("OPENAI_API_TYPE", None) == "azure" else False

    if model is None or model == "":
        model_name = config.model
    else:
        model_name = model
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
