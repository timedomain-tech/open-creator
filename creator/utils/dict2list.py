
def convert_to_values_list(x):
    if isinstance(x, dict):
        value_list = list(x.values())
        if len(value_list) > 0 and isinstance(value_list[0], dict):
            key = list(x.keys())[0]
            value_list[0]["name"] = key
            return value_list
    elif isinstance(x, str):
        if x == "None":
            return []
        else:
            return [{
                "parameter_name": "result",
                "parameter_type": x
            }]
    return x
