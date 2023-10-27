import json
import textwrap


# reference:
# https://gist.github.com/CGamesPlay/dd4f108f27e2eec145eedf5c717318f5
# https://community.openai.com/t/how-to-calculate-the-tokens-when-using-function-call/266573/24

# Function overhead is 16: 3 for the system message plus this template.

FUNCTION_HEADER_STR = """# Tools

## functions

namespace functions {

} // namespace functions"""


def resolve_ref(schema, json_schema):
    if schema.get("$ref") is not None:
        ref = schema["$ref"][14:]
        schema = json_schema["definitions"][ref]
    return schema


def format_enum(schema):
    return " | ".join(json.dumps(o) for o in schema["enum"])


def format_default(schema):
    v = schema["default"]
    if schema["type"] == "number":
        return f"{v:.1f}" if float(v).is_integer() else str(v)
    else:
        return str(v)


def format_object(schema, indent, json_schema):
    result = "{\n"
    if "properties" not in schema or len(schema["properties"]) == 0:
        if schema.get("additionalProperties", False):
            return "object"
        return None
    for key, value in schema["properties"].items():
        value = resolve_ref(value, json_schema)
        value_rendered = format_schema(value, indent + 1, json_schema)
        if value_rendered is None:
            continue
        if "description" in value and indent == 0:
            for line in textwrap.dedent(value["description"]).strip().split("\n"):
                result += f"{'  '*indent}// {line}\n"
        optional = "" if key in schema.get("required", {}) else "?"
        comment = (
            ""
            if value.get("default") is None
            else f" // default: {format_default(value)}"
        )
        result += f"{'  '*indent}{key}{optional}: {value_rendered},{comment}\n"
    result += ("  " * (indent - 1)) + "}"
    return result


def format_schema(schema, indent, json_schema):
    schema = resolve_ref(schema, json_schema)
    if "enum" in schema:
        return format_enum(schema)
    elif schema["type"] == "object":
        return format_object(schema, indent, json_schema)
    elif schema["type"] == "integer":
        return "number"
    elif schema["type"] in ["string", "number"]:
        return schema["type"]
    elif schema["type"] == "array":
        return format_schema(schema["items"], indent, json_schema) + "[]"
    else:
        raise ValueError("unknown schema type " + schema["type"])


def format_tool(tool):
    json_schema = tool["parameters"]
    result = f"// {tool['description']}\ntype {tool['name']} = ("
    formatted = format_object(json_schema, 0, json_schema)
    if formatted is not None:
        result += "_: " + formatted
    result += ") => any;\n\n"
    return result


def get_function_calls_token_count(encoder, function_calls):
    head_cnt = 3 + len(encoder.encode(FUNCTION_HEADER_STR))
    functions_cnt = sum(len(encoder.encode(format_tool(f))) for f in function_calls)
    return head_cnt + functions_cnt
