import json
import re
from json import JSONEncoder

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


class DefaultEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


def loads(json_str: str, formatter=None, cls=None):
    if formatter is not None:
        json_str = formatter(json_str)
    json_object = json.loads(json_str)
    if cls is None:
        return json_object
    else:
        return cls(**json_object)


def dumps(obj, formatter=None):
    json_str = json.dumps(obj.__dict__, ensure_ascii=False, indent=4, cls=DefaultEncoder)
    if formatter is not None:
        json_str = formatter(json_str)
    return json_str


def format_camel_to_snake(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def format_snake_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)
