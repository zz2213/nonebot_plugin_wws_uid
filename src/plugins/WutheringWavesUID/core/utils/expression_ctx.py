# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/utils/expression_ctx.py
import re
import json


class ExpressionCtx:
    def __init__(self, data: dict, parent: 'ExpressionCtx' = None) -> None:
        self.data = data
        self.parent = parent

    def get(self, key: str, default=None):
        if key in self.data:
            return self.data[key]
        if self.parent:
            return self.parent.get(key, default)
        return default

    def set(self, key: str, value):
        self.data[key] = value

    def __contains__(self, key: str):
        if key in self.data:
            return True
        if self.parent:
            return key in self.parent
        return False

    def __str__(self) -> str:
        s = json.dumps(self.data)
        if self.parent:
            s += " -> " + str(self.parent)
        return s


FUNC_PATTERN = re.compile(r"(\w+)\((.*?)\)")


def get_func_name(text: str):
    match = FUNC_PATTERN.match(text)
    if match:
        return match.group(1)
    return None


def get_func_args(text: str):
    match = FUNC_PATTERN.match(text)
    if match:
        args_str = match.group(2)
        if not args_str:
            return []
        args = args_str.split(",")
        return [arg.strip() for arg in args]
    return None