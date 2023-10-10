import sys
sys.path.append("..")
from creator.code_interpreter.python import flatten_functions

if __name__ == "__main__":
    
    code = """
def function_with_multiple_nested_functions(x):
    
    def first_nested(y):
        return y + 5
    
    def second_nested(z):
        return z * 2
    
    return first_nested(x) + second_nested(x)

"""

    print(flatten_functions(code))
