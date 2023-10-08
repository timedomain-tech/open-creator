from langchain.tools import BaseTool, format_tool_to_openai_function
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field
from creator.utils import remove_title
from typing import Type, Optional
import threading
import traceback
import ast


class PythonInput(BaseModel):
    code: str = Field(description="The code to execute")


class SafePythonInterpreter(BaseTool):
    name: str = "python"
    description: str = "A python interpreter for safe run"
    args_schema: Type[BaseModel] = PythonInput
    namespace: dict = {}
    setup_done: bool = False

    ALLOWED_FUNCTIONS = {"create", "save", "search", "CodeSkill"}
    ALLOW_METHODS = {".show", ".test", ".run", "__add__", "__gt__", "__lt__", "__annotations__"}
    TIMEOUT = 1200

    def setup(self, setup_code: str):
        self.run_code(setup_code)
        self.setup_done = True

    def is_allowed_function(self, node):
        # Check if the node represents a call to an allowed function
        return (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in self.ALLOWED_FUNCTIONS
        )
    
    def is_allowed_method(self, node):
        # Check if the node represents a call to an allowed method of an allowed class
        return (
            isinstance(node, ast.Call)
            and any( allowed_method in ast.unparse(node.func) for allowed_method in self.ALLOW_METHODS)
        )
    
    def preprocess(self, query: str):
        try:
            # Parse the code to an AST
            tree = ast.parse(query)

            # If setup is done, restrict the allowed nodes
            if getattr(self, "setup_done", False):
                for node in ast.walk(tree):
                    # Check for unsafe nodes
                    if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
                        raise ValueError(f"Usage of {node.__class__.__name__} nodes is not allowed")
                    # Check for disallowed function/method calls
                    elif isinstance(node, ast.Call):
                        if not (self.is_allowed_function(node) or self.is_allowed_method(node)):
                            raise ValueError("Usage of disallowed function/method: " + ast.unparse(node))

            # If all checks pass, return the original query
            return query
        
        except Exception as e:
            # Save exception info in the namespace to retrieve it later in the main thread.
            self.namespace['_preprocess_info'] = (type(e), e, e.__traceback__)
            return ""
    
    def run_code(self, query: str) -> dict:
        try:
            # Execute the code in the namespace to preserve state across code blocks.
            exec(query, self.namespace)
        except Exception as e:
            # Save exception info in the namespace to retrieve it later in the main thread.
            self.namespace['_exec_info'] = (type(e), e, e.__traceback__)
    
    def _run(self, 
             query: str, 
             run_manager: Optional[CallbackManagerForToolRun] = None
             ) -> dict[str, str]:
        # Preprocess the query
        query = self.preprocess(query)

        # If there was an error in preprocessing, retrieve and return the exception info.
        preprocess_info = self.namespace.pop('_preprocess_info', None)

        if preprocess_info:
            tb_lines = traceback.format_exception(*preprocess_info)
            return {"status": "error", "stdout": "", "stderr": "".join(tb_lines)}
    
        # Run the code in a separate thread and wait for it to finish or to timeout.
        thread = threading.Thread(target=self.run_code, args=(query,))
        thread.start()
        thread.join(timeout=self.TIMEOUT)
        
        # If the thread is still alive after the timeout, it is stuck in a long-running operation (e.g., an infinite loop).
        if thread.is_alive():
            # If possible, kill the thread. Note: This is not always safe and may result in inconsistencies.
            # ... add any thread termination logic here ...
            return {"status": "error", "stdout": "", "stderr": "Code execution timed out"}
        
        # Retrieve and clear the saved exception info from the namespace.
        exec_info = self.namespace.pop('_exec_info', None)
        if exec_info:
            # Format and return the exception info.
            tb_lines = traceback.format_exception(*exec_info)
            return {"status": "error", "stdout": "", "stderr": "".join(tb_lines)}
        
        return {"status": "success", "stdout": "", "stderr": ""}
    
    def to_function_schema(self):
        function_schema = format_tool_to_openai_function(self)
        function_schema["parameters"] = remove_title(function_schema["parameters"])
        return function_schema
