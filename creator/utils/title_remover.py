

def remove_title(schema):
    """
    Remove all title and its properties's title
    Recursively remove all titles including `$defs`
    
    Args:
    - schema (dict): The input schema dictionary.
    
    Returns:
    - dict: The schema dictionary after removing the "title" field.
    
    Example:
    >>> schema = {
    ...     "title": "Example Schema",
    ...     "properties": {
    ...         "name": {
    ...             "title": "Name",
    ...             "type": "string"
    ...         },
    ...         "age": {
    ...             "title": "Age",
    ...             "type": "integer"
    ...         }
    ...     },
    ...     "$defs": {
    ...         "address": {
    ...             "title": "Address",
    ...             "type": "object",
    ...             "properties": {
    ...                 "street": {
    ...                     "title": "Street",
    ...                     "type": "string"
    ...                 }
    ...             }
    ...         }
    ...     }
    ... }
    >>> remove_title(schema)
    {
        "properties": {
            "name": {
                "type": "string"
            },
            "age": {
                "type": "integer"
            }
        },
        "$defs": {
            "address": {
                "type": "object",
                "properties": {
                    "street": {
                        "type": "string"
                    }
                }
            }
        }
    }
    """
    if "title" in schema:
        schema.pop("title")
    if "properties" in schema:
        for prop in schema["properties"]:
            remove_title(schema["properties"][prop])
    if "$defs" in schema:
        for prop in schema["$defs"]:
            remove_title(schema["$defs"][prop])
    return schema
