

def generate_language_suffix(language: str):
    if language == "python":
        return ".py"
    elif language == "R":
        return ".R"
    elif language == "javascript":
        return ".js"
    elif language == "shell":
        return ".sh"
    elif language == "applescript":
        return ".applescript"
    elif language == "html":
        return ".html"
    else:
        raise NotImplementedError
