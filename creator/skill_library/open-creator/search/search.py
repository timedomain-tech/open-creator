from creator.core import creator
from creator.core.skill import CodeSkill


def search(query: str, top_k=1, threshold=0.8) -> list[CodeSkill]:
    """
    Search skills by query.
    
    Parameters:
    query: str, the query.
    top_k: int, optional, the maximum number of skills to return.
    threshold: float, optional, the minimum similarity score to return a skill.
    Returns:
    a list of CodeSkill objects.

    Example:
    >>> import creator
    >>> skills = search("I want to extract some pages from a pdf")
    """

    return creator.search(query=query, top_k=top_k, threshold=threshold)

