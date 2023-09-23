import numpy as np


def cosine_similarity(docs_matrix, query_vec, k=3):
    similarities = np.dot(docs_matrix, query_vec) / (np.linalg.norm(docs_matrix, axis=1) * np.linalg.norm(query_vec))
    top_k_indices = np.argsort(similarities)[-k:][::-1]
    return top_k_indices, similarities[top_k_indices]
