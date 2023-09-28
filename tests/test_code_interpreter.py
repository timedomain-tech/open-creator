import sys
sys.path.append("..")
from creator.code_interpreter import PythonInterpreter, CodeInterpreter


def test_python_interpreter():
    code_interpreter = PythonInterpreter()
    query = """
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True
"""
    response1 = code_interpreter.run(query=query)
    print(response1)

    response2 = code_interpreter.run(query="""
print(is_prime(17))
""")
    print(response2)
    response3 = code_interpreter.run(query="""
print(is_prime('string'))  # This will cause a TypeError
""")
    print(response3)


def test_to_function_call():
    print(CodeInterpreter().to_function_schema())


def test_python_interpreter2():
    code = 'def is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprimes = [num for num in range(2, 201) if is_prime(num)]\nprimes'
    code_interpreter = PythonInterpreter()
    output = code_interpreter.run(code)
    print(output)


def test_python_interpreter3():
    code = 'input("do you want to run the code? Y or n")'
    code_interpreter = PythonInterpreter()
    output = code_interpreter.run(code)
    print(output)


if __name__ == "__main__":
    test_python_interpreter()