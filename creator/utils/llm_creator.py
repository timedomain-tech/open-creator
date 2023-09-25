from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")


def create_llm(**kwargs):
    
    if AZURE_OPENAI_API_BASE and AZURE_OPENAI_API_VERSION and DEPLOYMENT_NAME and AZURE_OPENAI_API_KEY:
        return AzureChatOpenAI(
            openai_api_base=AZURE_OPENAI_API_BASE,
            openai_api_version=AZURE_OPENAI_API_VERSION,
            deployment_name=DEPLOYMENT_NAME,
            openai_api_key=AZURE_OPENAI_API_KEY,
            openai_api_type="azure",
            **kwargs
        )
    return ChatOpenAI(**kwargs)


