import subprocess
import traceback
import threading
import time
import os


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
        self.done = threading.Event()

    def get_persistent_process(self):
        self.process = subprocess.Popen(
            args=self.start_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            universal_newlines=True,
            env=os.environ.copy(),
        )

    def detect_program_end(self, line):
        return self.PROGRAM_END_DETECTOR in line

    def handle_stream_output(self, stream, is_stderr):
        """Reads from a stream and appends data to either stdout_data or stderr_data."""
        start_time = time.time()
        for line in stream:
            if self.detect_program_end(line):
                start_time = time.time()
                break
            if time.time() - start_time > self.timeout:
                start_time = time.time()
                self.output_cache["stderr"] += f"\nsession timeout ({self.timeout}) s\n"
                break
            if line:
                if is_stderr:
                    self.output_cache["stderr"] += line
                else:
                    self.output_cache["stdout"] += line
            time.sleep(0.1)

    def add_program_end_detector(self, code):
        if self.process:
            print_command = self.print_command.format(self.PROGRAM_END_DETECTOR) + "\n"
            return code + "\n\n" + print_command

    def clear(self):
        self.output_cache = {"stdout": "", "stderr": ""}
        self.done.clear()
        self.stdout_thread = threading.Thread(target=self.handle_stream_output, args=(self.process.stdout, False), daemon=True)
        self.stderr_thread = threading.Thread(target=self.handle_stream_output, args=(self.process.stderr, True), daemon=True)
        self.stdout_thread.start()
        self.stderr_thread.start()

    def preprocess(self, code):
        return code

    def postprocess(self, output):
        return output

    def run(self, query: str, is_start: bool = False) -> dict:
        try:
            query = self.preprocess(query)
        except Exception:
            traceback_string = traceback.format_exc()
            return {"status": "error", "stdout": "", "stderr": traceback_string}
        if is_start or self.process is None:
            try:
                self.get_persistent_process()
            except Exception:
                traceback_string = traceback.format_exc()
                return {"status": "error", "stdout": "", "stderr": traceback_string}
        self.clear()
        try:
            try:
                query = self.add_program_end_detector(query)
                self.process.stdin.write(query + "\n")
                self.process.stdin.flush()
                
                time.sleep(0.2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                stdout, stderr = "", traceback.format_exc()
                return {"status": "error", "stdout": stdout, "stderr": stderr}
        except BrokenPipeError:
            stderr = traceback.format_exc()
            return {"status": "error", "stdout": "", "stderr": stderr}

        return self.postprocess({"status": "success", **self.output_cache})

    def __del__(self):
        if self.process:
            self.process.terminate()
        if self.stdout_thread:
            self.stdout_thread.terminate()
        if self.stderr_thread:
            self.stderr_thread.terminate()