import subprocess
import traceback
import threading
import selectors
import time
import os


RETRY_LIMIT = 3


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
        self.output_cache = {"stdout": "", "stderr": ""}
        self.done = threading.Event()
        self.lock = threading.Lock()

    def get_persistent_process(self):
        if self.process:
            self.process.terminate()
            self.process = None
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
        sel = selectors.DefaultSelector()
        sel.register(stream, selectors.EVENT_READ)

        while not self.done.is_set():
            for key, _ in sel.select(timeout=0.1):   # Non-blocking with a small timeout
                line = key.fileobj.readline()

                if self.detect_program_end(line):
                    self.done.set()
                    break
                if time.time() - start_time > self.timeout:
                    self.done.set()
                    with self.lock:
                        self.output_cache["stderr"] += f"\nsession timeout ({self.timeout}) s\n"
                    break
                with self.lock:
                    if line:
                        if is_stderr:
                            self.output_cache["stderr"] += line
                        else:
                            self.output_cache["stdout"] += line
        sel.unregister(stream)
        sel.close()

    def add_program_end_detector(self, code):
        if self.process:
            print_command = self.print_command.format(self.PROGRAM_END_DETECTOR) + "\n"
            return code + "\n\n" + print_command
        else:
            return code

    def clear(self):
        self.output_cache = {"stdout": "", "stderr": ""}
        self.done.clear()
        self.stdout_thread = threading.Thread(target=self.handle_stream_output, args=(self.process.stdout, False), daemon=True)
        self.stderr_thread = threading.Thread(target=self.handle_stream_output, args=(self.process.stderr, True), daemon=True)
        self.stdout_thread.start()
        self.stderr_thread.start()

    def join(self, timeout):
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.done.is_set():
                break
        self.stdout_thread.join(0.1)
        self.stderr_thread.join(0.1)

    def preprocess(self, code):
        return code

    def postprocess(self, output):
        return output

    def run(self, query: str, is_start: bool = False, retries: int = 0) -> dict:
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
            code = self.add_program_end_detector(query)
            self.process.stdin.write(code + "\n")
            self.process.stdin.flush()

            time.sleep(0.2)
        except (BrokenPipeError, OSError):
            if retries < RETRY_LIMIT:
                time.sleep(retries * 2)  # Exponential back-off
                self.get_persistent_process()
                return self.run(query=query, retries=retries+1)
            else:
                stderr = traceback.format_exc()
                return {"status": "error", "stdout": "", "stderr": stderr}
        except subprocess.TimeoutExpired:
            self.process.kill()
            stdout, stderr = "", traceback.format_exc()
            return {"status": "error", "stdout": stdout, "stderr": stderr}

        self.join(self.timeout)
        return self.postprocess({"status": "success", **self.output_cache})

    def __del__(self):
        if self.process:
            self.process.terminate()
        if self.stdout_thread and self.stdout_thread.is_alive():
            self.stdout_thread.join()
        if self.stderr_thread and self.stderr_thread.is_alive():
            self.stderr_thread.join()
