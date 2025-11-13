# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/register_echo.py
from typing import Any, Callable, Dict

# 适配修改：从 from utils.map.damage.register import ...
from ..data.damage.register import register_echo as _register_echo, get_echo as _get_echo
from .abstract import DamageAbstract

PROCESSOR: Dict[str, Callable[[DamageAbstract], Dict[str, Any]]] = {}


def register_echo(
    echo_id: str,
) -> Callable[[Callable[[DamageAbstract], Dict[str, Any]]], Any]:
    def decorator(
        func: Callable[[DamageAbstract], Dict[str, Any]]
    ) -> Callable[[DamageAbstract], Dict[str, Any]]:
        PROCESSOR[echo_id] = func
        _register_echo(echo_id, func)
        return func

    return decorator


def get_echo(echo_id: str) -> Callable[[DamageB], Dict[str, Any]]:
    if echo_id in PROCESSOR:
        return PROCESSOR[echo_id]
    return _get_echo(echo_id)