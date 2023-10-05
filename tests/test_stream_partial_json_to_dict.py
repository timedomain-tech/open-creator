from langchain.output_parsers.json import parse_partial_json


def test_langchain_json_parser():
    arguments = "{\n  \"language\": \"python\",\n  \"code\": \"\nimport json\n\ndef is_prime(n):\n    if n <= 1:\n        return False\n    for i in range(2, int(n**0.5) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprimes = []\nfor num in range(2, 201):\n    if is_prime(num):\n        primes.append(num)\n\nresult = {\n    'num_primes': len(primes),\n    'primes': primes\n}\n\njson_output = json.dumps(result)\njson_output\n\"\n}"
    for i in range(len(arguments)):
        json_str = arguments[:i+1]
        print(parse_partial_json(json_str))


if __name__ == "__main__":
    test_langchain_json_parser()

