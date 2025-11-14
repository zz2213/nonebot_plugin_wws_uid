# nonebot_plugin_wws_uid/src/plugins/WutheringWavesUID/core/damage/register_char.py

from typing import Any, Callable, Dict, Optional
from .abstract import DamageAbstract

PROCESSOR: Dict[str, Callable[[DamageAbstract], Dict[str, Any]]] = {}

def register_char(
    char_id: str,
) -> Callable[[Callable[[DamageAbstract], Dict[str, Any]]], Any]:
    """
    (Framework A) 注册角色面板计算脚本
    """
    def decorator(
        func: Callable[[DamageAbstract], Dict[str, Any]]
    ) -> Callable[[DamageAbstract], Dict[str, Any]]:
        PROCESSOR[char_id] = func
        return func

    return decorator


def get_char(char_id: str) -> Optional[Callable[[DamageAbstract], Dict[str, Any]]]:
    """
    (Framework A) 获取角色面板计算脚本
    """
    return PROCESSOR.get(char_id)