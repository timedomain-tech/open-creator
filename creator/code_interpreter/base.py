import subprocess
import traceback
import threading
import time


class BaseInterpreter:
    """A tool for running base code in a terminal."""

    name: str = "base_interpreter"
    description: str = (
        "A base shell command tool. Use this to execute bash commands. "
        "It can also be used to execute any languages with interactive mode"
    )
    PROGRAM_END_DETECTOR = "[>>Open Creator CodeSkill Program End Placeholder<<]"
    start_command = "bash"
    print_command = "echo '{}'"
    timeout = 120

    def __init__(self):
        self.process = None
        self.stdout_thread = None
        self.stderr_thread = None

    def get_persistent_process(self):
        self.process = subprocess.Popen(
            args=self.start_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            universal_newlines=True
        )

    def detect_program_end(self, line):
        return self.PROGRAM_END_DETECTOR in line

    def handle_stream_output(self, stream, is_stderr):
        """Reads from a stream and appends data to either stdout_data or stderr_data."""
        start_time = time.time()
        while True:
            line = stream.readline()
            if self.detect_program_end(line):
                break
            if time.time() - start_time > self.timeout:
                self.output_cache["stderr"] += "\nsession timeout (self.timeout) s\n"
                break
            if line:
                if is_stderr:
                    self.output_cache["stderr"] += line
                else:
                    self.output_cache["stdout"] += line
            time.sleep(0.1)

    def add_program_end_detector(self):
        if self.process:
            print_command = self.print_command % self.PROGRAM_END_DETECTOR + "\n"
            self.process.stdin.write(print_command)
            self.process.stdin.flush()

    def clear(self):
        self.output_cache = {"stdout": "", "stderr": ""}
        if self.stdout_thread is not None:
            self.stdout_thread.terminate()
        if self.stderr_thread is not None:
            self.stderr_thread.terminate()
        self.stdout_thread = threading.Thread(target=self.handle_stream_output, args=(self.process.stdout, False), daemon=True)
        self.stderr_thread = threading.Thread(target=self.handle_stream_output, args=(self.process.stderr, True), daemon=True)
        self.stdout_thread.start()
        self.stderr_thread.start()
        self.start_command = "bash"

    def preprocess(self, code):
        return code

    def postprocess(self, output):
        return output

    def run(self, query: str, is_start: bool = False) -> dict:
        query = self.preprocess(query)
        if is_start or self.process is None:
            try:
                self.get_persistent_process()
                return {"status": "success", "stdout": "", "stderr": ""}
            except Exception:
                traceback_string = traceback.format_exc()
                return {"status": "error", "stdout": "", "stderr": traceback_string}
        self.clear()
        try:
            try:
                self.process.stdin.write(query + "\n")
                self.process.stdin.flush()
                self.add_program_end_detector()
                time.sleep(0.1)
            except subprocess.TimeoutExpired:
                self.process.kill()
                stdout, stderr = "", traceback.format_exc()
                return {"status": "error", "stdout": stdout, "stderr": stderr}
        except BrokenPipeError:
            stderr = traceback.format_exc()
            return {"status": "error", "stdout": "", "stderr": stderr}

        self.stdout_thread.join()
        self.stderr_thread.join()
        return self.postprocess({"status": "success", **self.output_cache})

    def __del__(self):
        if self.process:
            self.process.terminate()
        if self.stdout_thread:
            self.stdout_thread.terminate()
        if self.stderr_thread:
            self.stderr_thread.terminate()
