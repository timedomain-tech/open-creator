import os
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore


def create_embedding(config):

    use_azure = True if os.getenv("OPENAI_API_TYPE", None) == "azure" else False

    if use_azure:
        azure_model = os.getenv("EMBEDDING_DEPLOYMENT_NAME", None)
        print(azure_model)
        embedding = OpenAIEmbeddings(deployment=azure_model, model=azure_model)
    else:
        embedding = OpenAIEmbeddings()
    fs = LocalFileStore(config.embedding_cache_path)
    cached_embedding = CacheBackedEmbeddings.from_bytes_store(
        embedding, fs, namespace=embedding.model
    )
    return cached_embedding
