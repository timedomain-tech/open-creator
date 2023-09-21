import sys
sys.path.append("..")
from creator.dependency.code_interpreter import PythonInterpreter
import creator

def test_code_interpreter_python_case_1():
    code_interpreter = PythonInterpreter()
    response1 = code_interpreter.run(code="""
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
""")
    print(response1)

    response2 = code_interpreter.run(code="""
print(is_prime(17))  # This will cause a TypeError
""")
    print(response2)
    response3 = code_interpreter.run(code="""
print(is_prime('string'))  # This will cause a TypeError
""")
    print(response3)


# def test_run_python_skill():
#     skill = creator.create(skill_json_path="./skill_schema_example.json")
#     code_interpreter = PythonInterpreter()
#     result = code_interpreter.run(code=skill.skill_code)
#     print(result)
#     code = """
# 1/0
# """
#     print("???")
#     result = code_interpreter.run(code=code)
#     print(result, type(result))
#     print("done")
    

if __name__ == "__main__":
    test_code_interpreter_python_case_1()