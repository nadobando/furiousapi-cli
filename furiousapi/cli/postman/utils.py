import typing
from typing import Callable

from pydantic.utils import to_lower_camel


def _camelcase_dict(_dict) -> dict:
    res = dict()
    for key in _dict.keys():
        if isinstance(_dict[key], dict):
            res[to_lower_camel(key)] = _camelcase_dict(_dict[key])
        else:
            res[to_lower_camel(key)] = _dict[key]
    return res


def _recursive_walk(dct: dict, func: Callable[[dict, typing.Any], None]) -> None:
    copied = dct.copy()
    for key in copied:
        if isinstance(dct[key], dict):
            _recursive_walk(dct[key], func)
        elif isinstance(dct[key], list):
            for array_key in dct[key]:
                if isinstance(array_key, dict):
                    _recursive_walk(array_key, func)
        else:
            func(dct, key)


def _recursive_remove_datetime_format(js):
    _recursive_walk(js, _remove_datetime_format)


def _remove_datetime_format(_dict, key):
    value = _dict[key]
    if key == "format" and value == "date-time":
        del _dict[key]
