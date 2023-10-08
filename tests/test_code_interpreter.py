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
    code = 'def filter_prime_numbers(start, end):\n\n    def isPrime(num):\n        if num < 2:\n            return False\n        for i in range(2, int(num ** 0.5) + 1):\n            if num % i == 0:\n                return False\n        return True\n    count = 0\n    for num in range(start, end + 1):\n        if isPrime(num):\n            count += 1\n    return count'
    code_interpreter = PythonInterpreter()
    output = code_interpreter.run(code)
    print(output)
    output = code_interpreter.run(query="filter_prime_numbers(2, 202)")
    print(output)

def test_python_interpreter3():
    code = 'input("do you want to run the code? Y or n")'
    code_interpreter = PythonInterpreter()
    output = code_interpreter.run(code)
    print(output)

def test_python_interpreter4():
    arguments = '{\n  "language": "python",\n  "code": "def is_prime(n):\\n    if n <= 1:\\n        return False\\n    elif n <= 3:\\n        return True\\n    elif n % 2 == 0 or n % 3 == 0:\\n        return False\\n    i = 5\\n    while i * i <= n:\\n        if n % i == 0 or n % (i + 2) == 0:\\n            return False\\n        i += 6\\n    return True\\n\\n# Test the function\\nprint(is_prime(2))  # Should return True\\nprint(is_prime(4))  # Should return False"\n}'
    import json
    arguments = json.loads(arguments)
    code_interpreter = PythonInterpreter()
    output = code_interpreter.run(arguments["code"])
    print(output)

if __name__ == "__main__":
    test_python_interpreter4()