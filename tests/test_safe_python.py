import sys
sys.path.append("..")

from creator.code_interpreter.safe_python import SafePythonInterpreter
import creator
import unittest

# Setup code to be run initially in the interpreter
setup_code = """
def search(x):
    return x * 2

class CodeSkill:
    def show(self):
        return "Showing CodeSkill"

    def test(self):
        return "Testing CodeSkill"
    
    def run(self):
        return "Running CodeSkill"
"""


class TestSafePythonInterpreter(unittest.TestCase):
    
    def setUp(self):
        self.interpreter = SafePythonInterpreter()
        self.interpreter.setup(setup_code)

    def test_allowed_function_call(self):
        # Test that allowed functions can be called
        code = "result = search(5)"
        result = self.interpreter.run(code)
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.interpreter.namespace["result"], 10)
        
    def test_disallowed_function_call(self):
        # Test that disallowed functions cannot be called
        code = "result = not_allowed_function(5)"
        result = self.interpreter.run(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("ValueError", result["stderr"])
        
    def test_allowed_method_call(self):
        # Test that allowed methods can be called
        code = """
cs = CodeSkill()
result = cs.show()
        """
        result = self.interpreter.run(code)
        print(result)
        self.assertEqual(result["status"], "success")
        self.assertEqual(self.interpreter.namespace["result"], "Showing CodeSkill")
        
    def test_disallowed_method_call(self):
        # Test that disallowed methods cannot be called
        code = """
cs = CodeSkill()
result = cs.not_allowed_method()
        """
        result = self.interpreter.run(code)
        self.assertEqual(result["status"], "error")
        self.assertIn("Usage of disallowed function/method", result["stderr"])

    def test_open_creator_agent(self):
        code_interpreter = SafePythonInterpreter()
        create_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["create"])
        save_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["save"])
        search_skill_obj = creator.create(skill_path=creator.config.build_in_skill_config["search"])
        code = "\n\n".join([create_skill_obj.skill_code, save_skill_obj.skill_code, search_skill_obj.skill_code])
        code_interpreter.setup(code)
        result = code_interpreter.run("skill = create(request='given a 4 digit sequence and output the solution of Game of 24 and test it on 1 1 2 12')")
        print(result)
        result = code_interpreter.run("save(skill)")
        print(result)


# Run the tests
unittest.TextTestRunner().run(unittest.TestLoader().loadTestsFromTestCase(TestSafePythonInterpreter))

from creator.utils import load_system_prompt
from creator.config import config
import os

code_interpreter = SafePythonInterpreter()
    
create_skill_code = load_system_prompt(os.path.join(config.build_in_skill_config["create"], "skill_code.py"))
save_skill_code = load_system_prompt(os.path.join(config.build_in_skill_config["save"], "skill_code.py"))
search_skill_code = load_system_prompt(os.path.join(config.build_in_skill_config["search"], "skill_code.py"))
code = "\n\n".join([create_skill_code, save_skill_code, search_skill_code])
code_interpreter.setup(code)

result = code_interpreter.run("skill = create(request='given a 4 digit sequence and output the solution of Game of 24 and test it on 1 1 2 12')")

print(result)
