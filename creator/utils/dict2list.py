
def convert_to_values_list(x):
    if isinstance(x, dict):
        value_list = list(x.values())
        if len(value_list) > 0 and isinstance(value_list[0], dict):
            return value_list
    return x