import sys
sys.path.append("..")
from creator.utils import stream_partial_json_to_dict


def test_stream_partial_json_to_dict():
    res = stream_partial_json_to_dict('{"language": "json", "code": "print(\'hello world')
    assert res == {"language": "json", "code": "print(\'hello world"}

def test_stream_partial_json_to_dict_empty_input():
    res = stream_partial_json_to_dict('')
    assert res == {}

def test_stream_partial_json_to_dict_invalid_json():
    try:
        res = stream_partial_json_to_dict('{"language": "json", "code": "print(\'hello world')
    except ValueError:
        assert True
    else:
        assert False

def test_stream_partial_json_to_dict_no_code_field():
    res = stream_partial_json_to_dict('{"language": "json"}')
    assert res == {"language": "json"}


if __name__ == "__main__":
    test_stream_partial_json_to_dict()
    test_stream_partial_json_to_dict_empty_input()
    test_stream_partial_json_to_dict_invalid_json()
    test_stream_partial_json_to_dict_no_code_field()
