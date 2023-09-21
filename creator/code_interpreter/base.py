import subprocess
import traceback


def get_persistent_process(start_cmd: str):
    process = subprocess.Popen(
        args=start_cmd.split(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    return process


class BaseInterpreter:
    """A tool for running base code in a terminal."""

    name: str = "base_interpreter"
    description: str = (
        "A base shell command tool. Use this to execute bash commands. "
        "It can also be used to execute any language with interactive mode"
    )

    def __init__(self):
        self.process = None
        self.done = None

    def run(self, query: str, is_start: bool = False) -> dict:
        if is_start or self.process is None:
            try:
                self.process = get_persistent_process(query)
                return {"status": "success", "stdout": "", "stderr": ""}
            except Exception:
                traceback_string = traceback.format_exc()
                return {"status": "error", "stdout": "", "stderr": traceback_string}
        
        stdout, stderr = "", ""
        try:
            stdout, stderr = self.process.communicate(input=query)
        except BrokenPipeError:
            stderr = traceback.format_exc()

        return {"status": "success", "stdout": stdout, "stderr": stderr}

