import sys
sys.path.append("..")
from creator.utils import stream_partial_json_to_dict


if __name__ == "__main__":
    res = stream_partial_json_to_dict('{"language": "json", "code": "print(\'hello world')
    print(res)
