# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/register_echo.py

from typing import Any, Callable, Dict, Optional
from .abstract import DamageAbstract

PROCESSOR: Dict[str, Callable[[DamageAbstract], Dict[str, Any]]] = {}

def register_echo(
    echo_id: str,
) -> Callable[[Callable[[DamageAbstract], Dict[str, Any]]], Any]:
    """
    (Framework A) 注册声骸面板计算脚本
    """
    def decorator(
        func: Callable[[DamageAbstract], Dict[str, Any]]
    ) -> Callable[[DamageAbstract], Dict[str, Any]]:
        PROCESSOR[echo_id] = func
        return func

    return decorator


def get_echo(echo_id: str) -> Optional[Callable[[DamageAbstract], Dict[str, Any]]]:
    """
    (Framework A) 获取声骸面板计算脚本
    """
    return PROCESSOR.get(echo_id)