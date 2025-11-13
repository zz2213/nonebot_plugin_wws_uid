# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/register_char.py
from typing import Any, Callable, Dict

# 适配修改：从 from utils.map.damage.register import ...
from ..data.damage.register import register_char as _register_char, get_char as _get_char
from .abstract import DamageAbstract

PROCESSOR: Dict[str, Callable[[DamageAbstract], Dict[str, Any]]] = {}


def register_char(
    char_id: str,
) -> Callable[[Callable[[DamageAbstract], Dict[str, Any]]], Any]:
    def decorator(
        func: Callable[[DamageAbstract], Dict[str, Any]]
    ) -> Callable[[DamageAbstract], Dict[str, Any]]:
        PROCESSOR[char_id] = func
        _register_char(char_id, func)
        return func

    return decorator


def get_char(char_id: str) -> Callable[[DamageAbstract], Dict[str, Any]]:
    if char_id in PROCESSOR:
        return PROCESSOR[char_id]
    return _get_char(char_id)