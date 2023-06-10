CONF_UI = {
    'version': 24,
    'boolean': False,
    'dict': {'a': 1, 'b': 2, 'c': 3},
    'int': 1,
    'float': 3.1,
    'list': [1, 2, 3],
    'null': None,
    'string': 'A string',
}

def conf_ui():
    return CONF_UI

def hello(txt="Hello from the Lane UI"):
    return txt + txt


api_1 = hello()
