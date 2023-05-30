CONF_API = {
    'version': 22,
    'boolean': False,
    'dict': {'a': 1, 'b': 2, 'c': 3},
    'int': 1,
    'float': 3.1,
    'list': [1, 2, 3],
    'null': None,
    'string': 'A string',
}

def conf_foo():
    return CONF_API

def hello(txt="Hello from lane UI"):
    return txt + txt


api_1 = hello("hei")
