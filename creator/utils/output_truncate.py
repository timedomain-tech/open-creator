

def truncate_output(tool_result, max_output_chars=2000):
    stdout, stderr = tool_result.get("stdout", ""), tool_result.get("stderr", "")
    stdout_str, stderr_str = str(stdout), str(stderr)
    type_of_stdout, type_of_stderr = type(stdout), type(stderr)
    if not stdout_str and len(stdout_str) > max_output_chars:
        tool_result["stdout"] = stdout_str[:max_output_chars]
        tool_result["stdout"] += f"Output truncated. Showing the first {max_output_chars} characters.\n\n"
    if not stdout_str and len(stderr_str) > max_output_chars:
        tool_result["stderr"] = f"Output truncated. Showing the last {max_output_chars} characters.\n\n"
        tool_result["stderr"] += stderr_str[-max_output_chars:]
    if len(stdout_str+stderr_str) > max_output_chars:
        tool_result["stderr"] = f"Output truncated. Showing the last {max_output_chars} characters.\n\n"
        left_chars = max_output_chars - len(stdout_str)
        tool_result["stderr"] += stderr_str[-left_chars:]
    
    if type_of_stdout != str:
        try:
            tool_result["stdout"] = type_of_stdout(tool_result["stdout"])
        except Exception:
            pass
    if type_of_stderr != str:
        try:
            tool_result["stderr"] = type_of_stderr(tool_result["stderr"])
        except Exception:
            pass
    return tool_result
